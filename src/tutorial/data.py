"""Deterministic synthetic data used by the tutorial cases."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_churn_data(n_rows: int = 1_200, seed: int = 42) -> pd.DataFrame:
    """Create a small, reproducible customer-churn dataset."""
    rng = np.random.default_rng(seed)

    tenure = rng.integers(1, 73, n_rows)
    monthly_charge = np.clip(rng.normal(72, 20, n_rows), 20, 160)
    support_calls = rng.poisson(2.2, n_rows)
    usage_hours = np.clip(rng.normal(22, 8, n_rows), 1, 55)
    contract = rng.choice(
        ["Month-to-month", "One year", "Two year"],
        size=n_rows,
        p=[0.56, 0.29, 0.15],
    )
    autopay = rng.choice(["Yes", "No"], size=n_rows, p=[0.48, 0.52])
    region = rng.choice(["East", "North", "South", "West"], size=n_rows)

    logit = (
        -1.7
        - 0.026 * tenure
        + 0.018 * monthly_charge
        + 0.28 * support_calls
        - 0.012 * usage_hours
        + 0.85 * (contract == "Month-to-month")
        + 0.42 * (autopay == "No")
        + np.where(region == "North", 0.18, 0.0)
        + rng.normal(0, 0.75, n_rows)
    )
    churn_probability = 1 / (1 + np.exp(-logit))
    churned = rng.binomial(1, churn_probability)

    frame = pd.DataFrame(
        {
            "tenure_months": tenure,
            "monthly_charge": monthly_charge,
            "support_calls": support_calls,
            "usage_hours": usage_hours,
            "contract": contract,
            "autopay": autopay,
            "region": region,
            "churned": churned,
        }
    )

    # Missing values make the data-preparation lesson concrete.
    frame.loc[rng.choice(n_rows, size=18, replace=False), "monthly_charge"] = np.nan
    frame.loc[rng.choice(n_rows, size=9, replace=False), "autopay"] = None
    return frame


def generate_housing_data(n_rows: int = 900, seed: int = 42) -> pd.DataFrame:
    """Create a reproducible housing dataset with a nonlinear price process."""
    rng = np.random.default_rng(seed)

    living_area = rng.normal(105, 30, n_rows).clip(45, 230)
    rooms = np.clip(np.round(1 + living_area / 48 + rng.normal(0, 0.5, n_rows)), 1, 7)
    age = rng.integers(0, 51, n_rows)
    distance_km = np.clip(rng.gamma(2.4, 3.0, n_rows), 0.4, 28)
    condition = rng.choice(["Fair", "Good", "Excellent"], size=n_rows, p=[0.2, 0.58, 0.22])
    neighborhood = rng.choice(
        ["Central", "Harbour", "Suburban", "New town"],
        size=n_rows,
        p=[0.2, 0.2, 0.35, 0.25],
    )

    neighbourhood_effect = pd.Series(neighborhood).map(
        {"Central": 2.0, "Harbour": 1.3, "Suburban": 0.0, "New town": -0.8}
    ).to_numpy()
    condition_effect = pd.Series(condition).map(
        {"Fair": -0.6, "Good": 0.0, "Excellent": 0.8}
    ).to_numpy()

    price = (
        1.0
        + 0.034 * living_area
        + 0.42 * rooms
        - 0.012 * age
        - 0.065 * distance_km
        + neighbourhood_effect
        + condition_effect
        + 0.00008 * living_area**2
        + rng.normal(0, 0.38, n_rows)
    )

    return pd.DataFrame(
        {
            "living_area_sqm": living_area.round(1),
            "rooms": rooms.astype(int),
            "building_age": age,
            "distance_to_centre_km": distance_km.round(2),
            "condition": condition,
            "neighborhood": neighborhood,
            "price_hkd_m": np.maximum(price, 0.8).round(3),
        }
    )


def generate_demand_data(months: int = 60, seed: int = 42) -> pd.DataFrame:
    """Create a reproducible monthly demand series with trend and seasonality."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2021-01-01", periods=months, freq="MS")
    t = np.arange(months)
    seasonal = 12 * np.sin(2 * np.pi * t / 12) + 7 * np.cos(2 * np.pi * t / 12)
    annual_modulation = 5 * np.sin(2 * np.pi * t / 24)
    demand = (
        120
        + 1.15 * t
        + seasonal
        + annual_modulation
        + rng.normal(0, 5.5, months)
    )
    return pd.DataFrame({"month": dates, "demand": np.maximum(demand, 1).round(1)})


def write_datasets(output_dir: str | Path) -> dict[str, Path]:
    """Generate and save all tutorial datasets."""
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    paths = {
        "churn": target / "customer_churn.csv",
        "housing": target / "housing_prices.csv",
        "demand": target / "monthly_demand.csv",
    }
    generate_churn_data().to_csv(paths["churn"], index=False)
    generate_housing_data().to_csv(paths["housing"], index=False)
    generate_demand_data().to_csv(paths["demand"], index=False)
    return paths
