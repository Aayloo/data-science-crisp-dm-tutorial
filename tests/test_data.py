from __future__ import annotations

import pandas as pd

from tutorial.data import generate_churn_data, generate_demand_data, generate_housing_data


def test_churn_data_is_reproducible_and_has_missing_values():
    first = generate_churn_data(seed=7)
    second = generate_churn_data(seed=7)
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 1_200
    assert 0.15 < first["churned"].mean() < 0.55
    assert first["monthly_charge"].isna().sum() > 0


def test_housing_data_has_expected_shape():
    frame = generate_housing_data(seed=7)
    assert len(frame) == 900
    assert frame["price_hkd_m"].min() >= 0.8
    assert set(frame["condition"]).issubset({"Fair", "Good", "Excellent"})


def test_demand_data_is_chronological():
    frame = generate_demand_data(seed=7)
    assert frame["month"].is_monotonic_increasing
    assert len(frame) == 60
    assert (frame["demand"] > 0).all()
