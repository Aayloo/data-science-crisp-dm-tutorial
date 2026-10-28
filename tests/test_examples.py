from __future__ import annotations

from tutorial.examples import run_churn_example, run_demand_example, run_housing_example


def test_churn_example_produces_valid_metrics():
    result = run_churn_example()
    assert 0 <= result.logistic_metrics["accuracy"] <= 1
    assert 0 <= result.logistic_metrics["recall"] <= 1
    assert set(result.confusion) == {
        "true_negative",
        "false_positive",
        "false_negative",
        "true_positive",
    }


def test_housing_example_improves_on_a_naive_scale():
    result = run_housing_example()
    assert result.forest_metrics["mae"] > 0
    assert result.forest_metrics["rmse"] >= result.forest_metrics["mae"]
    assert 0 < result.forest_metrics["r2"] <= 1


def test_demand_forecast_has_one_prediction_per_holdout_month():
    result = run_demand_example()
    assert len(result.test) == 12
    assert len(result.seasonal_naive) == 12
    assert len(result.seasonal_linear) == 12
    assert result.seasonal_linear_metrics["mae"] > 0
