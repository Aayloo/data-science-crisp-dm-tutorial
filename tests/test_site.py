from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.local_resources: list[str] = []
        self.fragments: list[str] = []
        self.images_without_alt: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        for attribute in ("src", "href"):
            value = values.get(attribute)
            if not value:
                continue
            parsed = urlparse(value)
            if value.startswith("#"):
                self.fragments.append(value[1:])
            elif not parsed.scheme and not parsed.netloc:
                self.local_resources.append(value.split("#", 1)[0])
        if tag == "img" and "alt" not in values:
            self.images_without_alt.append(values.get("src") or "<unknown>")


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def test_html_ids_and_local_resources_are_valid():
    for page in (ROOT / "index.html", ROOT / "references" / "index.html"):
        source = page.read_text(encoding="utf-8")
        inside_style = re.sub(r"<style>.*?</style>", "", source, flags=re.DOTALL)
        inside_script = re.sub(r"<script>.*?</script>", "", inside_style, flags=re.DOTALL)
        parser = PageParser()
        parser.feed(inside_script)

        assert len(parser.ids) == len(set(parser.ids)), f"duplicate id in {page}"
        assert not parser.images_without_alt, f"image without alt in {page}"
        for fragment in parser.fragments:
            assert fragment in parser.ids, f"missing fragment #{fragment} in {page}"
        for resource in parser.local_resources:
            assert (page.parent / resource).resolve().exists(), f"missing resource {resource} in {page}"


def test_generated_results_are_present():
    script = (ROOT / "assets" / "data" / "results.js").read_text(encoding="utf-8")
    assert "window.TUTORIAL_RESULTS" in script
    assert "churn" in script
    assert "housing" in script
    assert "demand" in script
