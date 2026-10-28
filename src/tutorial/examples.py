"""Executable case studies for the CRISP-DM tutorial."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from .data import generate_churn_data, generate_demand_data, generate_housing_data


@dataclass
class ChurnRun:
    data: pd.DataFrame
    threshold: float
    logistic_metrics: dict[str, float | int]
    tree_metrics: dict[str, float | int]
    confusion: dict[str, int]


@dataclass
class HousingRun:
    data: pd.DataFrame
    test_index: pd.Index
    y_test: np.ndarray
    linear_predictions: np.ndarray
    forest_predictions: np.ndarray
    linear_metrics: dict[str, float]
    forest_metrics: dict[str, float]


@dataclass
class DemandRun:
    data: pd.DataFrame
    train: pd.DataFrame
    test: pd.DataFrame
    seasonal_naive: np.ndarray
    seasonal_linear: np.ndarray
    seasonal_naive_metrics: dict[str, float]
    seasonal_linear_metrics: dict[str, float]


def _classification_metrics(y_true: np.ndarray, probability: np.ndarray, threshold: float) -> dict:
    prediction = (probability >= threshold).astype(int)
    return {
        "accuracy": round(float(accuracy_score(y_true, prediction)), 4),
        "precision": round(float(precision_score(y_true, prediction, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, prediction, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, prediction, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, probability)), 4),
    }


def _regression_metrics(y_true: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    return {
        "mae": round(float(mean_absolute_error(y_true, prediction)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, prediction))), 4),
        "r2": round(float(r2_score(y_true, prediction)), 4),
    }


def run_churn_example(seed: int = 42, threshold: float = 0.40) -> ChurnRun:
    """Run a small classification comparison for the churn case."""
    frame = generate_churn_data(seed=seed)
    features = frame.drop(columns="churned")
    target = frame["churned"]
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.25,
        random_state=seed,
        stratify=target,
    )

    numeric = ["tenure_months", "monthly_charge", "support_calls", "usage_hours"]
    categorical = ["contract", "autopay", "region"]
    preprocess = ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("encode", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
        ]
    )

    logistic = Pipeline(
        [
            ("prepare", preprocess),
            ("model", LogisticRegression(max_iter=1_000, random_state=seed)),
        ]
    )
    tree = Pipeline(
        [
            ("prepare", preprocess),
            (
                "model",
                DecisionTreeClassifier(max_depth=4, min_samples_leaf=18, random_state=seed),
            ),
        ]
    )

    logistic.fit(x_train, y_train)
    tree.fit(x_train, y_train)
    logistic_probability = logistic.predict_proba(x_test)[:, 1]
    tree_probability = tree.predict_proba(x_test)[:, 1]
    logistic_prediction = (logistic_probability >= threshold).astype(int)

    matrix = confusion_matrix(y_test, logistic_prediction, labels=[0, 1])
    return ChurnRun(
        data=frame,
        threshold=threshold,
        logistic_metrics=_classification_metrics(y_test.to_numpy(), logistic_probability, threshold),
        tree_metrics=_classification_metrics(y_test.to_numpy(), tree_probability, threshold),
        confusion={
            "true_negative": int(matrix[0, 0]),
            "false_positive": int(matrix[0, 1]),
            "false_negative": int(matrix[1, 0]),
            "true_positive": int(matrix[1, 1]),
        },
    )


def _housing_preprocessor(numeric: list[str], categorical: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        [
            ("numeric", StandardScaler(), numeric),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
        ]
    )


def run_housing_example(seed: int = 42) -> HousingRun:
    """Run a linear baseline against a random-forest comparison."""
    frame = generate_housing_data(seed=seed)
    features = frame.drop(columns="price_hkd_m")
    target = frame["price_hkd_m"]
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.20,
        random_state=seed,
    )

    numeric = ["living_area_sqm", "rooms", "building_age", "distance_to_centre_km"]
    categorical = ["condition", "neighborhood"]
    preprocess = _housing_preprocessor(numeric, categorical)
    linear = Pipeline(
        [("prepare", preprocess), ("model", LinearRegression())]
    )
    forest = Pipeline(
        [
            ("prepare", preprocess),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=250,
                    min_samples_leaf=3,
                    random_state=seed,
                    n_jobs=1,
                ),
            ),
        ]
    )
    linear.fit(x_train, y_train)
    forest.fit(x_train, y_train)
    linear_predictions = linear.predict(x_test)
    forest_predictions = forest.predict(x_test)

    return HousingRun(
        data=frame,
        test_index=y_test.index,
        y_test=y_test.to_numpy(),
        linear_predictions=linear_predictions,
        forest_predictions=forest_predictions,
        linear_metrics=_regression_metrics(y_test.to_numpy(), linear_predictions),
        forest_metrics=_regression_metrics(y_test.to_numpy(), forest_predictions),
    )


def _percentage_error(y_true: np.ndarray, prediction: np.ndarray) -> float:
    safe_true = np.where(np.abs(y_true) < 1e-9, np.nan, y_true)
    mape = np.nanmean(np.abs((safe_true - prediction) / safe_true)) * 100
    return round(float(mape), 3)


def run_demand_example(seed: int = 42, test_months: int = 12) -> DemandRun:
    """Compare seasonal naive and seasonal-linear forecasts."""
    frame = generate_demand_data(seed=seed)
    split = len(frame) - test_months
    train = frame.iloc[:split].copy()
    test = frame.iloc[split:].copy()

    previous_year = train["demand"].iloc[-12:].to_numpy()
    seasonal_naive = np.resize(previous_year, test_months)

    train_t = np.arange(len(train), dtype=float)
    future_t = np.arange(len(train), len(train) + test_months, dtype=float)

    def design_matrix(t_values: np.ndarray) -> np.ndarray:
        return np.column_stack(
            [
                t_values,
                np.sin(2 * np.pi * t_values / 12),
                np.cos(2 * np.pi * t_values / 12),
                np.sin(2 * np.pi * t_values / 6),
                np.cos(2 * np.pi * t_values / 6),
            ]
        )

    seasonal_model = LinearRegression()
    seasonal_model.fit(design_matrix(train_t), train["demand"].to_numpy())
    seasonal_linear = np.maximum(seasonal_model.predict(design_matrix(future_t)), 0)
    y_test = test["demand"].to_numpy()

    return DemandRun(
        data=frame,
        train=train,
        test=test,
        seasonal_naive=seasonal_naive,
        seasonal_linear=seasonal_linear,
        seasonal_naive_metrics={
            "mae": round(float(mean_absolute_error(y_test, seasonal_naive)), 3),
            "mape": _percentage_error(y_test, seasonal_naive),
        },
        seasonal_linear_metrics={
            "mae": round(float(mean_absolute_error(y_test, seasonal_linear)), 3),
            "mape": _percentage_error(y_test, seasonal_linear),
        },
    )
