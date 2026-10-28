"""Create the three learner-facing Jupyter notebooks."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"


def notebook(cells: list[tuple[str, str]], title: str):
    document = nbf.v4.new_notebook()
    document["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.10+",
        },
        "title": title,
    }
    document["cells"] = [
        nbf.v4.new_markdown_cell(source) if cell_type == "markdown" else nbf.v4.new_code_cell(source)
        for cell_type, source in cells
    ]
    return document


def setup_cell() -> tuple[str, str]:
    return (
        "code",
        """from pathlib import Path
import sys

ROOT = Path.cwd()
if not (ROOT / "src").exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import Image, display

from tutorial.data import write_datasets

plt.rcParams.update({
    "figure.dpi": 150,
    "font.family": "serif",
    "font.serif": ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "axes.grid": True,
    "grid.color": "#c8c8c8",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.7,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.labelsize": 10,
    "axes.titlesize": 10.5,
    "lines.linewidth": 1.4,
})

paths = write_datasets(ROOT / "data")
print(f"Project root: {ROOT.name}")""",
    )


def build_churn() -> None:
    cells = [
        (
            "markdown",
            """# Case A · Customer churn classification

## CRISP-DM question

Which customers should receive a limited retention offer?

The target is whether a customer churns in the next 30 days. Accuracy alone is
not enough: the campaign budget limits how many customers can be contacted.

**Learning objective:** compare a transparent baseline with a small tree model
and explain why the decision threshold changes the result.
""",
        ),
        setup_cell(),
        (
            "code",
            """df = pd.read_csv(paths["churn"])
df.head()""",
        ),
        (
            "code",
            """print(df.info())
print("\\nMissing share:")
print(df.isna().mean().sort_values(ascending=False))
print("\\nTarget distribution:")
print(df["churned"].value_counts(normalize=True).rename("share"))""",
        ),
        (
            "markdown",
            """**Figure A0 | Missing values by field.** Source: synthetic tutorial
data; one row represents one customer. The plot makes the preparation choices
visible before any model is fitted.""",
        ),
        (
            "code",
            """display(Image(filename=str(ROOT / "assets" / "img" / "missing-values.png")))""",
        ),
        (
            "markdown",
            """## Fit the two candidate models

The reusable implementation uses one train/test split, a preprocessing
pipeline and a threshold of 0.40. This avoids fitting transformations on the
test set.
""",
        ),
        (
            "code",
            """from tutorial.examples import run_churn_example

churn = run_churn_example()

pd.DataFrame({
    "logistic regression": churn.logistic_metrics,
    "decision tree": churn.tree_metrics,
}).T""",
        ),
        (
            "code",
            """pd.Series(churn.confusion, name="customers").to_frame()""",
        ),
        (
            "markdown",
            """**Figure A1 | Confusion matrix at the selected threshold.** Source:
tutorial calculations on the synthetic churn holdout set.""",
        ),
        (
            "code",
            """display(Image(filename=str(ROOT / "assets" / "img" / "churn-confusion.png")))""",
        ),
        (
            "markdown",
            """**Figure A2 | Precision, recall, and F1 as the threshold changes.**
Source: tutorial calculations on the holdout set. The chosen threshold is a
decision rule, not a universal constant.""",
        ),
        (
            "code",
            """display(Image(filename=str(ROOT / "assets" / "img" / "churn-thresholds.png")))""",
        ),
        (
            "markdown",
            """**Figure A3 | Baseline and tree model compared on one holdout split.**
Source: tutorial calculations. The comparison is valid because both models use
the same split, preprocessing protocol, and threshold.""",
        ),
        (
            "code",
            """display(Image(filename=str(ROOT / "assets" / "img" / "model-comparison.png")))""",
        ),
        (
            "markdown",
            """## Interpretation and exercise

1. Which model has higher Recall at the selected threshold?
2. What happens if you lower the threshold from 0.40 to 0.30?
3. Which error is more expensive for the business: a missed churner or an
   unnecessary retention offer?

The synthetic relationship is only a teaching device. It is not evidence about
real customers.
""",
        ),
    ]
    nbf.write(notebook(cells, "Customer churn case"), NOTEBOOK_DIR / "01-customer-churn.ipynb")


def build_housing() -> None:
    cells = [
        (
            "markdown",
            """# Case B · House-price regression

## CRISP-DM question

Can a model estimate residential prices closely enough to support a first-pass
budget screen?

**Learning objective:** establish a linear baseline, compare it with a random
forest, and explain why a more complex model does not automatically improve
out-of-sample error.
""",
        ),
        setup_cell(),
        (
            "code",
            """df = pd.read_csv(paths["housing"])
df.head()""",
        ),
        (
            "code",
            """df.describe().T""",
        ),
        (
            "code",
            """from tutorial.examples import run_housing_example

housing = run_housing_example()

pd.DataFrame({
    "linear regression": housing.linear_metrics,
    "random forest": housing.forest_metrics,
}).T""",
        ),
        (
            "markdown",
            """**Figure B2 | Actual versus predicted prices.** Source: tutorial
calculations on the 20% holdout set. Points close to the reference line indicate
lower prediction error.""",
        ),
        (
            "code",
            """display(Image(filename=str(ROOT / "assets" / "img" / "housing-predictions.png")))""",
        ),
        (
            "markdown",
            """## Interpretation and exercise

The linear baseline has lower MAE and RMSE in this controlled synthetic case.
That is a useful result, not a failed demonstration:

- the data-generating process is close to additive;
- the sample is small;
- default tree settings are not guaranteed to be optimal;
- model complexity must earn its place on the holdout set.

Change one forest hyperparameter and ask whether the improvement is stable or
only a single-split accident.
""",
        ),
    ]
    nbf.write(notebook(cells, "House-price case"), NOTEBOOK_DIR / "02-house-price.ipynb")


def build_demand() -> None:
    cells = [
        (
            "markdown",
            """# Case C · Monthly demand forecasting

## CRISP-DM question

Can a simple seasonal model improve a one-year operational plan over last
year's same-month baseline?

**Learning objective:** keep chronology intact, create forecasts from past
information only, and compare models with MAE and MAPE.
""",
        ),
        setup_cell(),
        (
            "code",
            """df = pd.read_csv(paths["demand"], parse_dates=["month"])
df.tail()""",
        ),
        (
            "code",
            """df.set_index("month").plot(
    figsize=(9, 4),
    title="Synthetic monthly demand",
    ylabel="Demand",
    color="#0f766e",
    legend=False,
)""",
        ),
        (
            "markdown",
            """## Chronological validation

The final 12 months are the test period. A random split would allow future
information to leak into the training set.
""",
        ),
        (
            "code",
            """from tutorial.examples import run_demand_example

demand = run_demand_example()

pd.DataFrame({
    "seasonal naive": demand.seasonal_naive_metrics,
    "seasonal linear": demand.seasonal_linear_metrics,
}).T""",
        ),
        (
            "markdown",
            """**Figure C1 | Actual demand versus two forecasts.** Source: tutorial
calculations. The final 12 months are held out in chronological order.""",
        ),
        (
            "code",
            """display(Image(filename=str(ROOT / "assets" / "img" / "demand-forecast.png")))""",
        ),
        (
            "markdown",
            """## Interpretation and exercise

MAPE becomes unstable when actual demand approaches zero. For real operational
data, inspect the cost of over- and under-forecasting rather than choosing a
metric by habit.

Exercise: change the holdout from 12 to 6 months and explain why the model
comparison may change.
""",
        ),
    ]
    nbf.write(notebook(cells, "Demand-forecasting case"), NOTEBOOK_DIR / "03-demand-forecast.ipynb")


def main() -> None:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    build_churn()
    build_housing()
    build_demand()
    print(f"Wrote notebooks to {NOTEBOOK_DIR}")


if __name__ == "__main__":
    main()
