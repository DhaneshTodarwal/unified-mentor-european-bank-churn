"""Create reproducible analysis outputs and charts from the source CSV."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analysis import (
    clean_and_prepare,
    compute_kpis,
    group_churn,
    kpis_as_dataframe,
    load_dataset,
)


SOURCE_PATH = ROOT / "data" / "European_Bank.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"

sns.set_theme(style="whitegrid", context="notebook")


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def save_group_table(prepared: pd.DataFrame, columns: list[str], filename: str) -> pd.DataFrame:
    table = group_churn(prepared, columns)
    table.to_csv(OUTPUT_DIR / filename, index=False)
    return table


def save_bar_chart(table: pd.DataFrame, category: str, filename: str, title: str) -> None:
    plot_table = table.copy()
    plot_table[category] = plot_table[category].astype(str)
    plot_table = plot_table.sort_values("churn_rate", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    sns.barplot(data=plot_table, x="churn_rate", y=category, color="#1f77b4", ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Churn rate")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0%}"))
    for patch, rate in zip(ax.patches, plot_table["churn_rate"]):
        ax.text(
            patch.get_width() + 0.005,
            patch.get_y() + patch.get_height() / 2,
            f"{rate:.1%}",
            va="center",
            fontsize=9,
        )
    fig.tight_layout()
    fig.savefig(CHART_DIR / filename, dpi=160)
    plt.close(fig)


def save_stacked_status_chart(prepared: pd.DataFrame) -> None:
    status = prepared["ChurnStatus"].value_counts().reindex(["Retained", "Churned"], fill_value=0)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(status.index, status.values, color=["#4c78a8", "#e45756"])
    ax.set_title("Customer retention status")
    ax.set_ylabel("Customers")
    for bar, value in zip(bars, status.values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + max(status.values) * 0.015, f"{value:,}", ha="center")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "retention_status.png", dpi=160)
    plt.close(fig)


def save_age_geography_heatmap(prepared: pd.DataFrame) -> None:
    table = prepared.pivot_table(
        index="AgeGroup",
        columns="Geography",
        values="Exited",
        aggfunc="mean",
        observed=False,
    )
    table = table.reindex(index=["<30", "30–45", "46–59", "60+"])
    fig, ax = plt.subplots(figsize=(8, 4.8))
    sns.heatmap(table, annot=True, fmt=".1%", cmap="Blues", vmin=0, vmax=max(0.01, float(table.max().max())), ax=ax)
    ax.set_title("Churn rate by age group and geography")
    ax.set_xlabel("Geography")
    ax.set_ylabel("Age group")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "age_geography_heatmap.png", dpi=160)
    plt.close(fig)


def save_high_value_chart(prepared: pd.DataFrame) -> None:
    table = group_churn(prepared, "HighValueFlag")
    table["HighValueFlag"] = table["HighValueFlag"].map({True: "High-value proxy", False: "Other customers"}).fillna(table["HighValueFlag"].astype(str))
    table = table.sort_values("churn_rate")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=table, x="churn_rate", y="HighValueFlag", color="#f58518", ax=ax)
    ax.set_title("Churn rate for high-value proxy customers")
    ax.set_xlabel("Churn rate")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "high_value_churn.png", dpi=160)
    plt.close(fig)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    raw = load_dataset(SOURCE_PATH)
    prepared, metadata = clean_and_prepare(raw)
    kpis = compute_kpis(prepared)

    # Keep the source identifier for internal reproducibility, but never retain
    # surname in the processed analysis file or expose identifiers in charts.
    prepared.drop(columns=["Surname"], errors="ignore").to_csv(
        PROCESSED_DIR / "european_bank_prepared.csv", index=False
    )
    save_json(OUTPUT_DIR / "validation_report.json", metadata)
    save_json(OUTPUT_DIR / "kpis.json", kpis)
    kpis_as_dataframe(kpis).to_csv(OUTPUT_DIR / "kpis.csv", index=False)

    tables = {
        "geography": save_group_table(prepared, ["Geography"], "churn_by_geography.csv"),
        "gender": save_group_table(prepared, ["Gender"], "churn_by_gender.csv"),
        "age": save_group_table(prepared, ["AgeGroup"], "churn_by_age_group.csv"),
        "tenure": save_group_table(prepared, ["TenureGroup"], "churn_by_tenure_group.csv"),
        "credit": save_group_table(prepared, ["CreditScoreBand"], "churn_by_credit_band.csv"),
        "balance": save_group_table(prepared, ["BalanceSegment"], "churn_by_balance_segment.csv"),
        "activity": save_group_table(prepared, ["ActivityStatus"], "churn_by_activity.csv"),
        "products": save_group_table(prepared, ["NumOfProducts"], "churn_by_products.csv"),
        "high_value": save_group_table(prepared, ["HighValueFlag"], "churn_by_high_value.csv"),
    }
    tables["geography_age"] = group_churn(prepared, ["Geography", "AgeGroup"])
    tables["geography_age"].to_csv(OUTPUT_DIR / "churn_by_geography_age.csv", index=False)

    save_stacked_status_chart(prepared)
    save_bar_chart(tables["geography"], "Geography", "geography_churn.png", "Churn rate by geography")
    save_bar_chart(tables["age"], "AgeGroup", "age_churn.png", "Churn rate by age group")
    save_bar_chart(tables["tenure"], "TenureGroup", "tenure_churn.png", "Churn rate by tenure group")
    save_bar_chart(tables["activity"], "ActivityStatus", "activity_churn.png", "Churn rate by activity status")
    save_age_geography_heatmap(prepared)
    save_high_value_chart(prepared)

    print(json.dumps({"kpis": kpis, "metadata": metadata}, indent=2, default=str))


if __name__ == "__main__":
    main()
