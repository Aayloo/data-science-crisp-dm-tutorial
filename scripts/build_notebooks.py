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
            """## Build the model comparison directly

The cells below expose the full learning path: split, preprocessing, fit,
predict and evaluate. Keeping preprocessing inside a Pipeline ensures that
imputation and scaling are learned from the training data only.
""",
        ),
        (
            "code",
            """from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

X = df.drop(columns="churned")
y = df["churned"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y,
)

numeric = ["tenure_months", "monthly_charge", "support_calls", "usage_hours"]
categorical = ["contract", "autopay", "region"]

preprocess = ColumnTransformer([
    ("numeric", Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]), numeric),
    ("categorical", Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ]), categorical),
])""",
        ),
        (
            "markdown",
            """The split happens before any transformation. `preprocess` is then
placed inside each model Pipeline, so its medians, category levels and scaling
statistics are fitted on `X_train` only. The tree and logistic models therefore
share the same information boundary.""",
        ),
        (
            "code",
            """logistic = Pipeline([
    ("prepare", preprocess),
    ("model", LogisticRegression(max_iter=1_000, random_state=42)),
])

tree = Pipeline([
    ("prepare", preprocess),
    ("model", DecisionTreeClassifier(
        max_depth=4,
        min_samples_leaf=18,
        random_state=42,
    )),
])

_ = logistic.fit(X_train, y_train)
_ = tree.fit(X_train, y_train)""",
        ),
        (
            "code",
            """from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score,
)

threshold = 0.40
logistic_probability = logistic.predict_proba(X_test)[:, 1]
tree_probability = tree.predict_proba(X_test)[:, 1]
logistic_prediction = (logistic_probability >= threshold).astype(int)
tree_prediction = (tree_probability >= threshold).astype(int)

def evaluate_classifier(y_true, prediction, probability):
    return {
        "accuracy": accuracy_score(y_true, prediction),
        "precision": precision_score(y_true, prediction, zero_division=0),
        "recall": recall_score(y_true, prediction, zero_division=0),
        "f1": f1_score(y_true, prediction, zero_division=0),
        "roc_auc": roc_auc_score(y_true, probability),
    }

pd.DataFrame({
    "logistic regression": evaluate_classifier(y_test, logistic_prediction, logistic_probability),
    "decision tree": evaluate_classifier(y_test, tree_prediction, tree_probability),
}).T""",
        ),
        (
            "markdown",
            """At the selected threshold, the model with higher recall finds more
churners but may also create more false alerts. F1 balances precision and recall
with equal weight; that weighting is a reporting choice, not a universal
business objective.""",
        ),
        (
            "markdown",
            """## Check split sensitivity with cross-validation

A single holdout result can be lucky. The following cells refit the full
Pipeline in five stratified folds and report the mean and standard deviation of
ROC AUC. This is a stability check, not a replacement for keeping one untouched
confirmation set.""",
        ),
        (
            "code",
            """from sklearn.model_selection import StratifiedKFold, cross_validate

fold_protocol = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

def cv_auc(model):
    score = cross_validate(model, X, y, cv=fold_protocol, scoring="roc_auc")["test_score"]
    return pd.Series({"mean_auc": score.mean(), "std_auc": score.std(), "folds": len(score)})

pd.DataFrame({
    "logistic regression": cv_auc(logistic),
    "decision tree": cv_auc(tree),
}).T""",
        ),
        (
            "code",
            """confusion = confusion_matrix(y_test, logistic_prediction, labels=[0, 1])
pd.DataFrame(
    confusion,
    index=["Actual stay", "Actual churn"],
    columns=["Predicted stay", "Predicted churn"],
)""",
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
            """from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import numpy as np

X = df.drop(columns="price_hkd_m")
y = df["price_hkd_m"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

numeric = ["living_area_sqm", "rooms", "building_age", "distance_to_centre_km"]
categorical = ["condition", "neighborhood"]
preprocess = ColumnTransformer([
    ("numeric", StandardScaler(), numeric),
    ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
])""",
        ),
        (
            "markdown",
            """The linear model is the interpretable baseline. The forest receives
the identical transformed features and split; only the estimator changes.""",
        ),
        (
            "code",
            """linear = Pipeline([("prepare", preprocess), ("model", LinearRegression())])
forest = Pipeline([
    ("prepare", preprocess),
    ("model", RandomForestRegressor(
        n_estimators=250,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=1,
    )),
])

_ = linear.fit(X_train, y_train)
_ = forest.fit(X_train, y_train)""",
        ),
        (
            "code",
            """def evaluate_regressor(model):
    prediction = model.predict(X_test)
    return {
        "MAE": mean_absolute_error(y_test, prediction),
        "RMSE": mean_squared_error(y_test, prediction) ** 0.5,
        "R2": r2_score(y_test, prediction),
    }

pd.DataFrame({
    "linear regression": evaluate_regressor(linear),
    "random forest": evaluate_regressor(forest),
}).T""",
        ),
        (
            "markdown",
            """Both models see the same holdout rows. RMSE is retained next to MAE
because it penalises large pricing errors more heavily. The random forest is a
useful comparison, but its extra flexibility is not evidence of extra value.""",
        ),
        (
            "markdown",
            """## Check fold-to-fold stability

Five-fold cross-validation on the training-plus-holdout rows shows how much the
result depends on one particular holdout. Each fold refits its own preprocessing
pipeline.""",
        ),
        (
            "code",
            """from sklearn.model_selection import KFold, cross_validate

folds = KFold(n_splits=5, shuffle=True, random_state=42)
scoring = {
    "mae": "neg_mean_absolute_error",
    "rmse": "neg_root_mean_squared_error",
}

def cv_regression(model):
    scores = cross_validate(model, X, y, cv=folds, scoring=scoring)
    return {
        "MAE mean": -scores["test_mae"].mean(),
        "MAE sd": scores["test_mae"].std(),
        "RMSE mean": -scores["test_rmse"].mean(),
        "RMSE sd": scores["test_rmse"].std(),
    }

pd.DataFrame({
    "linear regression": cv_regression(linear),
    "random forest": cv_regression(forest),
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
            """from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import numpy as np

train = df.iloc[:-12].copy()
test = df.iloc[-12:].copy()

# Baseline: same month last year.
seasonal_naive = train["demand"].iloc[-12:].to_numpy()
y_test = test["demand"].to_numpy()

train[["month", "demand"]].tail(2)""",
        ),
        (
            "markdown",
            """The seasonal naive forecast repeats the corresponding demand values
from the previous year. It is a strong operational baseline because it preserves
an annual pattern without estimating any parameters.""",
        ),
        (
            "code",
            """# A small trend-plus-seasonality regression.
def design_matrix(t):
    return np.column_stack([
        t,
        np.sin(2 * np.pi * t / 12),
        np.cos(2 * np.pi * t / 12),
        np.sin(2 * np.pi * t / 6),
        np.cos(2 * np.pi * t / 6),
    ])

train_t = np.arange(len(train), dtype=float)
future_t = np.arange(len(train), len(train) + len(test), dtype=float)
seasonal_model = LinearRegression().fit(design_matrix(train_t), train["demand"])
seasonal_linear = np.maximum(seasonal_model.predict(design_matrix(future_t)), 0)""",
        ),
        (
            "markdown",
            """The regression uses elapsed time plus two sine-cosine pairs. It can
carry a slow trend and repeating seasonal effects, but it has no information from
the final twelve months during fitting.""",
        ),
        (
            "code",
            """def forecast_metrics(prediction):
    safe = np.where(np.abs(y_test) < 1e-9, np.nan, y_test)
    return {
        "MAE": mean_absolute_error(y_test, prediction),
        "MAPE_pct": np.nanmean(np.abs((safe - prediction) / safe)) * 100,
    }

pd.DataFrame({
    "seasonal naive": forecast_metrics(seasonal_naive),
    "seasonal linear": forecast_metrics(seasonal_linear),
}).T""",
        ),
        (
            "markdown",
            """The split is chronological: 48 months train the model and the final
12 months remain untouched until evaluation. The seasonal-naive forecast uses
the corresponding months from the previous year rather than copying the latest
value.""",
        ),
        (
            "markdown",
            """## Repeat the forecast across rolling origins

One twelve-month holdout is a narrow test. The next cell moves the forecast
origin forward and evaluates three separate twelve-month windows. This remains a
small teaching sample, but it shows how to inspect forecast stability over time.""",
        ),
        (
            "code",
            """def rolling_forecasts(cutoff):
    train_window = df.iloc[:cutoff].copy()
    test_window = df.iloc[cutoff:cutoff + 12].copy()
    horizon = len(test_window)
    naive = train_window["demand"].iloc[-12:].to_numpy()

    train_t = np.arange(len(train_window), dtype=float)
    future_t = np.arange(len(train_window), len(train_window) + horizon, dtype=float)
    model = LinearRegression().fit(
        design_matrix(train_t),
        train_window["demand"],
    )
    linear_forecast = np.maximum(model.predict(design_matrix(future_t)), 0)
    actual = test_window["demand"].to_numpy()
    return {
        "naive_MAE": mean_absolute_error(actual, naive),
        "linear_MAE": mean_absolute_error(actual, linear_forecast),
    }

pd.DataFrame(
    {f"origin_{cutoff}": rolling_forecasts(cutoff) for cutoff in [24, 36, 48]}
).T""",
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
