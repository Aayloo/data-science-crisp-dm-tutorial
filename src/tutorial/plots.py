"""Publication-style charts for the tutorial website."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .examples import ChurnRun, DemandRun, HousingRun


INK = "#17324d"
MUTED = "#64748b"
GRID = "#d9e2e8"
TEAL = "#0f766e"
BLUE = "#2563a6"
AMBER = "#b7791f"
PAPER = "#fbfcf8"
RED = "#b42318"


def _style_axes(ax: plt.Axes) -> None:
    ax.set_facecolor(PAPER)
    ax.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#9fb0bd")
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)


def save_churn_confusion(result: ChurnRun, output_path: str | Path) -> Path:
    matrix = np.array(
        [
            [result.confusion["true_negative"], result.confusion["false_positive"]],
            [result.confusion["false_negative"], result.confusion["true_positive"]],
        ]
    )
    fig, ax = plt.subplots(figsize=(6.6, 5.3), facecolor=PAPER)
    image = ax.imshow(matrix, cmap="YlGnBu")
    for row in range(2):
        for column in range(2):
            value = matrix[row, column]
            color = "white" if value > matrix.max() * 0.55 else INK
            ax.text(column, row, f"{value:,}", ha="center", va="center", fontsize=18, color=color)
    ax.set_xticks([0, 1], labels=["Stay", "Churn"])
    ax.set_yticks([0, 1], labels=["Stay", "Churn"])
    ax.set_xlabel("Predicted outcome")
    ax.set_ylabel("Actual outcome")
    ax.set_title("Churn confusion matrix", loc="left", color=INK, fontsize=14, pad=14)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="Customers")
    fig.text(0.01, 0.01, "Synthetic data · Logistic Regression · threshold = 0.40", color=MUTED, fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    return target


def save_housing_prediction(result: HousingRun, output_path: str | Path) -> Path:
    fig, ax = plt.subplots(figsize=(7.5, 5.4), facecolor=PAPER)
    _style_axes(ax)
    ax.scatter(
        result.y_test,
        result.forest_predictions,
        s=24,
        color=TEAL,
        alpha=0.62,
        edgecolor="white",
        linewidth=0.4,
        label="Random forest",
    )
    minimum = min(result.y_test.min(), result.forest_predictions.min())
    maximum = max(result.y_test.max(), result.forest_predictions.max())
    ax.plot([minimum, maximum], [minimum, maximum], color=RED, linewidth=1.2, label="Perfect prediction")
    ax.set_xlabel("Actual price (HKD million)")
    ax.set_ylabel("Predicted price (HKD million)")
    ax.set_title("Actual vs predicted house prices", loc="left", color=INK, fontsize=14, pad=14)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    fig.text(0.01, 0.01, "Synthetic data · 20% holdout set", color=MUTED, fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    return target


def save_demand_forecast(result: DemandRun, output_path: str | Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.3, 5.2), facecolor=PAPER)
    _style_axes(ax)
    ax.plot(result.train["month"], result.train["demand"], color=INK, linewidth=1.6, label="Training data")
    ax.plot(result.test["month"], result.test["demand"], color=INK, linewidth=1.6, linestyle="--", label="Actual holdout")
    ax.plot(result.test["month"], result.seasonal_naive, color=AMBER, linewidth=1.8, label="Seasonal naive")
    ax.plot(result.test["month"], result.seasonal_linear, color=TEAL, linewidth=2.0, label="Seasonal linear")
    ax.axvline(result.test["month"].iloc[0], color=GRID, linewidth=1)
    ax.set_ylabel("Monthly demand")
    ax.set_title("Forecast comparison on the final 12 months", loc="left", color=INK, fontsize=14, pad=14)
    ax.legend(frameon=False, ncol=2, loc="upper left", fontsize=9)
    fig.text(0.01, 0.01, "Synthetic data · chronological split · no future information", color=MUTED, fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    return target
