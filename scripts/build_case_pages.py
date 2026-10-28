"""Render executed notebooks as notebook pages inside the tutorial website."""

from __future__ import annotations

import html
import re
from pathlib import Path

from nbconvert import HTMLExporter
from nbformat import read, validate
from pygments.formatters import HtmlFormatter


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
CASES_DIR = ROOT / "cases"

CASES = [
    {
        "slug": "customer-churn",
        "number": "A",
        "title": "Customer Churn",
        "notebook": "01-customer-churn.ipynb",
        "summary": (
            "A binary-classification lab that compares logistic regression with a "
            "decision tree and shows why the decision threshold matters."
        ),
        "previous": ("demand-forecast", "Case C · Demand Forecasting"),
        "next": ("house-price", "Case B · House Prices"),
        "alts": [
            "Bar chart showing missing values by customer field.",
            "Confusion matrix for the logistic-regression churn model.",
            "Line chart showing precision, recall, and F1 across thresholds.",
            "Grouped bar chart comparing logistic regression and a decision tree.",
        ],
    },
    {
        "slug": "house-price",
        "number": "B",
        "title": "House Prices",
        "notebook": "02-house-price.ipynb",
        "summary": (
            "A regression lab that establishes a transparent linear baseline and "
            "tests whether a random forest improves out-of-sample error."
        ),
        "previous": ("customer-churn", "Case A · Customer Churn"),
        "next": ("demand-forecast", "Case C · Demand Forecasting"),
        "alts": [
            "Scatter plot comparing actual and predicted house prices with a reference line.",
        ],
    },
    {
        "slug": "demand-forecast",
        "number": "C",
        "title": "Demand Forecasting",
        "notebook": "03-demand-forecast.ipynb",
        "summary": (
            "A time-series lab that preserves chronology and compares seasonal naive "
            "with a simple seasonal-linear forecast."
        ),
        "previous": ("house-price", "Case B · House Prices"),
        "next": ("customer-churn", "Case A · Customer Churn"),
        "alts": [
            "Line chart of synthetic monthly demand over time.",
            "Line chart comparing actual monthly demand with two forecast methods.",
        ],
    },
]


def add_image_alt_text(fragment: str, descriptions: list[str]) -> str:
    iterator = iter(descriptions)
    pattern = re.compile(r"<img\b([^>]*)>", re.IGNORECASE)

    def replacement(match: re.Match[str]) -> str:
        description = next(iterator, "Notebook output visualisation.")
        attributes = re.sub(
            r"\balt=(?:\"[^\"]*\"|'[^']*')",
            "",
            match.group(1),
            flags=re.IGNORECASE,
        ).strip()
        escaped = html.escape(description, quote=True)
        spacer = " " if attributes else ""
        return f'<img alt="{escaped}"{spacer}{attributes}>'

    return pattern.sub(replacement, fragment)


def page_shell(case: dict, fragment: str) -> str:
    slug = case["slug"]
    notebook_path = f"../../notebooks/{case['notebook']}"
    github_url = (
        "https://github.com/Aayloo/data-science-crisp-dm-tutorial/"
        f"blob/main/notebooks/{case['notebook']}"
    )
    previous_slug, previous_title = case["previous"]
    next_slug, next_title = case["next"]
    syntax_css = HtmlFormatter(style="friendly").get_style_defs(".highlight")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(case['summary'], quote=True)}">
  <meta name="theme-color" content="#17324d">
  <title>{html.escape(case['title'])} · Case Lab {case['number']}</title>
  <link rel="icon" href="../../assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../../assets/css/notebook.css?v=20261028-6">
  <style>{syntax_css}</style>
</head>
<body>
  <a class="skip-link" href="#notebook">Skip to notebook</a>
  <header class="notebook-topbar">
    <a href="../../index.html">← Back to tutorial</a>
    <span>Case Lab {case['number']} / Executed notebook</span>
    <a href="../../index.html#case-labs">All case labs</a>
  </header>

  <main class="notebook-shell" id="notebook">
    <section class="notebook-banner" aria-labelledby="case-title">
      <div>
        <p class="eyebrow">CASE LAB {case['number']} / {slug.replace('-', ' ').upper()}</p>
        <h1 id="case-title">{html.escape(case['title'])}</h1>
        <p>{html.escape(case['summary'])}</p>
      </div>
      <div class="notebook-actions">
        <a class="notebook-button notebook-button-primary" href="{notebook_path}" download>Download .ipynb</a>
        <a class="notebook-button" href="{github_url}">View source on GitHub</a>
      </div>
    </section>

    <article class="notebook-document" aria-label="Executed notebook">
      {fragment}
    </article>

    <nav class="notebook-pager" aria-label="Case navigation">
      <a href="../{previous_slug}/">
        <span>Previous case</span>
        <strong>{html.escape(previous_title)}</strong>
      </a>
      <a class="next" href="../{next_slug}/">
        <span>Next case</span>
        <strong>{html.escape(next_title)}</strong>
      </a>
    </nav>

    <footer class="notebook-footer">
      Executed notebook generated from the committed <code>.ipynb</code> source.
      Synthetic teaching data only.
    </footer>
  </main>
</body>
</html>
"""


def build_case(case: dict) -> Path:
    notebook_path = NOTEBOOK_DIR / case["notebook"]
    notebook = read(notebook_path, as_version=4)
    validate(notebook)

    exporter = HTMLExporter(template_name="basic")
    exporter.embed_images = True
    fragment, _ = exporter.from_filename(notebook_path)

    # The page has its own heading; remove the duplicate notebook H1.
    fragment = re.sub(r"<h1\b.*?</h1>", "", fragment, count=1, flags=re.DOTALL)
    fragment = add_image_alt_text(fragment, case["alts"])

    output_dir = CASES_DIR / case["slug"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "index.html"
    output_path.write_text(page_shell(case, fragment), encoding="utf-8")
    return output_path


def main() -> None:
    for case in CASES:
        output = build_case(case)
        size_kb = output.stat().st_size / 1024
        print(f"Built {output.relative_to(ROOT)} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
