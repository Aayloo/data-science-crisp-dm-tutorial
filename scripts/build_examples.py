"""Generate datasets, run every case, and write static site artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tutorial.data import write_datasets
from tutorial.examples import run_churn_example, run_demand_example, run_housing_example
from tutorial.plots import (
    save_churn_confusion,
    save_churn_threshold,
    save_demand_forecast,
    save_housing_prediction,
    save_missingness,
    save_model_comparison,
)


def main() -> None:
    data_paths = write_datasets(ROOT / "data")
    churn = run_churn_example()
    housing = run_housing_example()
    demand = run_demand_example()

    save_churn_confusion(churn, ROOT / "assets" / "img" / "churn-confusion.png")
    save_missingness(churn, ROOT / "assets" / "img" / "missing-values.png")
    save_churn_threshold(churn, ROOT / "assets" / "img" / "churn-thresholds.png")
    save_model_comparison(churn, ROOT / "assets" / "img" / "model-comparison.png")
    save_housing_prediction(housing, ROOT / "assets" / "img" / "housing-predictions.png")
    save_demand_forecast(demand, ROOT / "assets" / "img" / "demand-forecast.png")

    results = {
        "data": {
            "churn_rows": int(len(churn.data)),
            "churn_rate": round(float(churn.data["churned"].mean()), 4),
            "housing_rows": int(len(housing.data)),
            "demand_months": int(len(demand.data)),
        },
        "churn": {
            "threshold": churn.threshold,
            "logistic": churn.logistic_metrics,
            "tree": churn.tree_metrics,
            "confusion": churn.confusion,
        },
        "housing": {
            "linear": housing.linear_metrics,
            "forest": housing.forest_metrics,
        },
        "demand": {
            "train_months": int(len(demand.train)),
            "test_months": int(len(demand.test)),
            "seasonal_naive": demand.seasonal_naive_metrics,
            "seasonal_linear": demand.seasonal_linear_metrics,
        },
        "generated_files": {
            "datasets": {name: str(path.relative_to(ROOT)) for name, path in data_paths.items()},
            "figures": [
                "assets/img/churn-confusion.png",
                "assets/img/missing-values.png",
                "assets/img/churn-thresholds.png",
                "assets/img/model-comparison.png",
                "assets/img/housing-predictions.png",
                "assets/img/demand-forecast.png",
            ],
        },
    }

    json_path = ROOT / "assets" / "data" / "results.json"
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    js_path = ROOT / "assets" / "data" / "results.js"
    js_path.write_text(
        "window.TUTORIAL_RESULTS = "
        + json.dumps(results, indent=2, ensure_ascii=False)
        + ";\n",
        encoding="utf-8",
    )

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
