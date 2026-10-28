"""Publication-style charts for the tutorial website."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score

from .examples import ChurnRun, DemandRun, HousingRun


PALETTE = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "vermillion": "#D55E00",
    "pink": "#CC79A7",
    "sky": "#56B4E9",
    "ink": "#17324d",
    "muted": "#5f6f83",
    "grid": "#d6dde1",
    "paper": "#fbfcf8",
}

plt.rcParams.update(
    {
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        "axes.grid": True,
        "grid.color": PALETTE["grid"],
        "grid.linewidth": 0.55,
        "grid.alpha": 0.75,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "legend.frameon": False,
        "lines.linewidth": 1.4,
        "lines.markersize": 4,
    }
)


def _style_axes(ax: plt.Axes) -> None:
    ax.set_facecolor(PALETTE["paper"])
    ax.grid(axis="y", color=PALETTE["grid"], linewidth=0.55, alpha=0.75)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#9fb0bd")
    ax.tick_params(colors=PALETTE["muted"], labelsize=9)
    ax.xaxis.label.set_color(PALETTE["ink"])
    ax.yaxis.label.set_color(PALETTE["ink"])


def save_churn_confusion(result: ChurnRun, output_path: str | Path) -> Path:
    matrix = np.array(
        [
            [result.confusion["true_negative"], result.confusion["false_positive"]],
            [result.confusion["false_negative"], result.confusion["true_positive"]],
        ]
    )
    fig, ax = plt.subplots(figsize=(6.6, 5.3), facecolor=PALETTE["paper"])
    image = ax.imshow(matrix, cmap="YlGnBu")
    for row in range(2):
        for column in range(2):
            value = matrix[row, column]
            color = "white" if value > matrix.max() * 0.55 else PALETTE["ink"]
            ax.text(column, row, f"{value:,}", ha="center", va="center", fontsize=18, color=color)
    ax.set_xticks([0, 1], labels=["Stay", "Churn"])
    ax.set_yticks([0, 1], labels=["Stay", "Churn"])
    ax.set_xlabel("Predicted outcome")
    ax.set_ylabel("Actual outcome")
    ax.set_title(
        "Figure A1 | Churn confusion matrix",
        loc="left",
        color=PALETTE["ink"],
        fontsize=12,
        pad=14,
    )
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="Customers")
    fig.text(
        0.01,
        0.01,
        "Source: synthetic tutorial data; logistic regression at a 0.40 threshold.",
        color=PALETTE["muted"],
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=300, bbox_inches="tight", facecolor=PALETTE["paper"])
    plt.close(fig)
    return target


def save_housing_prediction(result: HousingRun, output_path: str | Path) -> Path:
    fig, ax = plt.subplots(figsize=(7.5, 5.4), facecolor=PALETTE["paper"])
    _style_axes(ax)
    ax.scatter(
        result.y_test,
        result.forest_predictions,
        s=24,
        color=PALETTE["blue"],
        alpha=0.62,
        edgecolor="white",
        linewidth=0.4,
        label="Random forest",
    )
    minimum = min(result.y_test.min(), result.forest_predictions.min())
    maximum = max(result.y_test.max(), result.forest_predictions.max())
    ax.plot(
        [minimum, maximum],
        [minimum, maximum],
        color=PALETTE["vermillion"],
        linewidth=1.2,
        label="Perfect prediction",
    )
    ax.set_xlabel("Actual price (HKD million)")
    ax.set_ylabel("Predicted price (HKD million)")
    ax.set_title(
        "Figure B1 | Actual vs predicted house prices",
        loc="left",
        color=PALETTE["ink"],
        fontsize=12,
        pad=14,
    )
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    fig.text(
        0.01,
        0.01,
        "Source: synthetic tutorial data; 20% holdout set.",
        color=PALETTE["muted"],
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=300, bbox_inches="tight", facecolor=PALETTE["paper"])
    plt.close(fig)
    return target


def save_demand_forecast(result: DemandRun, output_path: str | Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.3, 5.2), facecolor=PALETTE["paper"])
    _style_axes(ax)
    ax.plot(result.train["month"], result.train["demand"], color=PALETTE["ink"], linewidth=1.45, label="Training data")
    ax.plot(
        result.test["month"],
        result.test["demand"],
        color=PALETTE["ink"],
        linewidth=1.45,
        linestyle="--",
        label="Actual holdout",
    )
    ax.plot(
        result.test["month"],
        result.seasonal_naive,
        color=PALETTE["orange"],
        linewidth=1.8,
        label="Seasonal naive",
    )
    ax.plot(
        result.test["month"],
        result.seasonal_linear,
        color=PALETTE["green"],
        linewidth=2.0,
        label="Seasonal linear",
    )
    ax.axvline(result.test["month"].iloc[0], color=PALETTE["grid"], linewidth=1)
    ax.set_ylabel("Monthly demand")
    ax.set_title(
        "Figure C1 | Forecast comparison on the final 12 months",
        loc="left",
        color=PALETTE["ink"],
        fontsize=12,
        pad=14,
    )
    ax.legend(frameon=False, ncol=2, loc="upper left", fontsize=9)
    fig.text(
        0.01,
        0.01,
        "Source: synthetic tutorial data; chronological split with no future information.",
        color=PALETTE["muted"],
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=300, bbox_inches="tight", facecolor=PALETTE["paper"])
    plt.close(fig)
    return target


def save_missingness(result: ChurnRun, output_path: str | Path) -> Path:
    """Visualise which fields require data-quality decisions."""
    missing = result.data.isna().mean().mul(100).sort_values()
    missing = missing[missing > 0]
    fig, ax = plt.subplots(figsize=(7.2, 3.8), facecolor=PALETTE["paper"])
    ax.barh(
        [name.replace("_", " ").title() for name in missing.index],
        missing.to_numpy(),
        color=PALETTE["sky"],
        edgecolor="white",
    )
    for row, value in enumerate(missing):
        ax.text(value + 0.05, row, f"{value:.1f}%", va="center", color=PALETTE["muted"], fontsize=9)
    ax.set_xlim(0, max(2.5, missing.max() * 1.25))
    ax.set_xlabel("Missing values (%)")
    ax.set_title(
        "Figure A0 | Missing values by field",
        loc="left",
        color=PALETTE["ink"],
        fontsize=12,
        pad=14,
    )
    ax.grid(axis="x", color=PALETTE["grid"], linewidth=0.55, alpha=0.75)
    ax.grid(axis="y", visible=False)
    fig.text(
        0.01,
        0.01,
        "Source: synthetic customer-churn dataset; one row is one customer.",
        color=PALETTE["muted"],
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=300, bbox_inches="tight", facecolor=PALETTE["paper"])
    plt.close(fig)
    return target


def save_churn_threshold(result: ChurnRun, output_path: str | Path) -> Path:
    """Show the precision-recall trade-off as the decision threshold changes."""
    thresholds = np.arange(0.10, 0.91, 0.025)
    precision = [
        precision_score(result.y_test, (result.logistic_probability >= t).astype(int), zero_division=0)
        for t in thresholds
    ]
    recall = [
        recall_score(result.y_test, (result.logistic_probability >= t).astype(int), zero_division=0)
        for t in thresholds
    ]
    f1 = [
        f1_score(result.y_test, (result.logistic_probability >= t).astype(int), zero_division=0)
        for t in thresholds
    ]
    fig, ax = plt.subplots(figsize=(7.6, 4.4), facecolor=PALETTE["paper"])
    _style_axes(ax)
    ax.plot(thresholds, precision, color=PALETTE["blue"], label="Precision")
    ax.plot(thresholds, recall, color=PALETTE["vermillion"], linestyle="--", label="Recall")
    ax.plot(thresholds, f1, color=PALETTE["green"], linestyle="-.", label="F1")
    ax.axvline(result.threshold, color=PALETTE["muted"], linewidth=1, linestyle=":")
    ax.text(
        result.threshold + 0.015,
        0.06,
        "selected threshold",
        color=PALETTE["muted"],
        fontsize=8,
    )
    ax.set_xlim(0.1, 0.9)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Classification threshold")
    ax.set_ylabel("Score")
    ax.set_title(
        "Figure A2 | Metric trade-offs across thresholds",
        loc="left",
        color=PALETTE["ink"],
        fontsize=12,
        pad=14,
    )
    ax.legend(loc="best")
    fig.text(
        0.01,
        0.01,
        "Source: tutorial calculations on the synthetic churn holdout set.",
        color=PALETTE["muted"],
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=300, bbox_inches="tight", facecolor=PALETTE["paper"])
    plt.close(fig)
    return target


def save_model_comparison(result: ChurnRun, output_path: str | Path) -> Path:
    """Compare holdout classification metrics for the baseline and tree."""
    labels = ["Accuracy", "Precision", "Recall", "F1"]
    logistic = np.array(
        [
            result.logistic_metrics["accuracy"],
            result.logistic_metrics["precision"],
            result.logistic_metrics["recall"],
            result.logistic_metrics["f1"],
        ]
    )
    tree = np.array(
        [
            result.tree_metrics["accuracy"],
            result.tree_metrics["precision"],
            result.tree_metrics["recall"],
            result.tree_metrics["f1"],
        ]
    )
    positions = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(7.6, 4.2), facecolor=PALETTE["paper"])
    _style_axes(ax)
    ax.bar(positions - width / 2, logistic, width, color=PALETTE["blue"], label="Logistic regression")
    ax.bar(positions + width / 2, tree, width, color=PALETTE["orange"], label="Decision tree")
    ax.set_xticks(positions, labels)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title(
        "Figure A3 | Baseline and tree model compared on one holdout split",
        loc="left",
        color=PALETTE["ink"],
        fontsize=12,
        pad=14,
    )
    ax.legend(loc="upper right")
    fig.text(
        0.01,
        0.01,
        "Source: tutorial calculations; both models use the same train/test split.",
        color=PALETTE["muted"],
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=300, bbox_inches="tight", facecolor=PALETTE["paper"])
    plt.close(fig)
    return target
