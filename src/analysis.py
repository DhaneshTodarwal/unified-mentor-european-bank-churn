"""Data preparation and KPI logic for the European banking churn project.

The portal brief does not provide all segmentation thresholds. The defaults in
this module are explicit, reusable assumptions and are returned in metadata so
that the dashboard and written deliverables can show them consistently.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


PORTAL_COLUMNS = [
    "CustomerId",
    "Surname",
    "CreditScore",
    "Geography",
    "Gender",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Exited",
]

OPTIONAL_SOURCE_COLUMNS = ["Year"]
NUMERIC_COLUMNS = [
    "CustomerId",
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Exited",
]
BINARY_COLUMNS = ["HasCrCard", "IsActiveMember", "Exited"]
EXPECTED_GEOGRAPHIES = ["France", "Spain", "Germany"]
EXPECTED_GENDERS = ["Female", "Male"]

AGE_LABELS = ["<30", "30–45", "46–59", "60+"]
CREDIT_LABELS = ["Low (<580)", "Medium (580–669)", "High (670+)"]
TENURE_LABELS = ["New (0–2)", "Mid-term (3–6)", "Long-term (7+)"]
BALANCE_LABELS = ["Zero-balance", "Low-balance", "High-balance", "Missing"]

GROUP_METRIC_COLUMNS = [
    "customers",
    "churned",
    "retained",
    "churn_rate",
    "churn_contribution",
    "risk_index",
]


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Load the source CSV without changing source values."""

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Dataset not found: {source}")
    return pd.read_csv(source)


def _to_python(value: Any) -> Any:
    """Convert numpy scalars to JSON/report-friendly Python values."""

    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def _value_counts_dict(series: pd.Series) -> dict[str, int]:
    return {str(key): int(value) for key, value in series.value_counts(dropna=False).items()}


def profile_source(df: pd.DataFrame) -> dict[str, Any]:
    """Return a source-data quality profile before cleaning."""

    missing = {str(key): int(value) for key, value in df.isna().sum().items()}
    duplicate_ids = int(df["CustomerId"].duplicated(keep=False).sum()) if "CustomerId" in df else None
    unexpected_geographies = []
    if "Geography" in df:
        unexpected_geographies = sorted(
            set(df["Geography"].dropna().astype(str).str.strip()) - set(EXPECTED_GEOGRAPHIES)
        )
    unexpected_genders = []
    if "Gender" in df:
        unexpected_genders = sorted(
            set(df["Gender"].dropna().astype(str).str.strip()) - set(EXPECTED_GENDERS)
        )
    binary_values = {
        column: _value_counts_dict(df[column])
        for column in BINARY_COLUMNS
        if column in df
    }
    numeric_summary = {}
    for column in NUMERIC_COLUMNS:
        if column in df:
            numeric = pd.to_numeric(df[column], errors="coerce")
            numeric_summary[column] = {
                "min": _to_python(numeric.min()),
                "max": _to_python(numeric.max()),
                "mean": _to_python(numeric.mean()),
                "median": _to_python(numeric.median()),
            }
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": [str(column) for column in df.columns],
        "missing_by_column": missing,
        "duplicate_customer_id_rows": duplicate_ids,
        "unexpected_geographies": unexpected_geographies,
        "unexpected_genders": unexpected_genders,
        "binary_value_counts": binary_values,
        "numeric_summary": numeric_summary,
    }


def _require_columns(df: pd.DataFrame) -> None:
    missing = [column for column in PORTAL_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required portal columns: {missing}")


def _make_segment_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    prepared = df.copy()

    prepared["AgeGroup"] = pd.cut(
        prepared["Age"],
        bins=[-np.inf, 29, 45, 59, np.inf],
        labels=AGE_LABELS,
        right=True,
        include_lowest=True,
    )
    prepared["CreditScoreBand"] = pd.cut(
        prepared["CreditScore"],
        bins=[-np.inf, 579, 669, np.inf],
        labels=CREDIT_LABELS,
        right=True,
        include_lowest=True,
    )
    prepared["TenureGroup"] = pd.cut(
        prepared["Tenure"],
        bins=[-np.inf, 2, 6, np.inf],
        labels=TENURE_LABELS,
        right=True,
        include_lowest=True,
    )

    positive_balances = prepared.loc[prepared["Balance"] > 0, "Balance"].dropna()
    median_positive_balance = float(positive_balances.median()) if len(positive_balances) else None
    high_value_threshold = float(positive_balances.quantile(0.75)) if len(positive_balances) else None

    balance_conditions = [
        prepared["Balance"].isna(),
        prepared["Balance"].le(0),
        prepared["Balance"].gt(0)
        & prepared["Balance"].le(median_positive_balance if median_positive_balance is not None else -1),
        prepared["Balance"].gt(median_positive_balance if median_positive_balance is not None else -1),
    ]
    prepared["BalanceSegment"] = np.select(
        balance_conditions,
        ["Missing", "Zero-balance", "Low-balance", "High-balance"],
        default="Missing",
    )

    if high_value_threshold is None:
        prepared["HighValueFlag"] = False
    else:
        prepared["HighValueFlag"] = prepared["Balance"].ge(high_value_threshold) & prepared["Balance"].gt(0)
    prepared["ActivityStatus"] = prepared["IsActiveMember"].map({1: "Active", 0: "Inactive"})
    prepared["ChurnStatus"] = prepared["Exited"].map({1: "Churned", 0: "Retained"})

    thresholds = {
        "age_groups": {
            "<30": "Age < 30",
            "30–45": "30 <= Age <= 45",
            "46–59": "46 <= Age <= 59",
            "60+": "Age >= 60",
        },
        "credit_score_bands": {
            "Low (<580)": "CreditScore < 580",
            "Medium (580–669)": "580 <= CreditScore <= 669",
            "High (670+)": "CreditScore >= 670",
        },
        "tenure_groups": {
            "New (0–2)": "Tenure <= 2",
            "Mid-term (3–6)": "3 <= Tenure <= 6",
            "Long-term (7+)": "Tenure >= 7",
        },
        "median_positive_balance": median_positive_balance,
        "high_value_balance_threshold_75th_percentile": high_value_threshold,
    }
    return prepared, thresholds


def clean_and_prepare(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Validate, clean, and enrich the dataset for analysis.

    The returned metadata records what was found and what was removed. The
    cleaning rules are deliberately conservative: the target and core fields
    must be valid, while the source profile preserves the quality evidence.
    """

    _require_columns(df)
    source_profile = profile_source(df)
    prepared = df.copy()

    for column in NUMERIC_COLUMNS:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce")
    for column in ["Surname", "Geography", "Gender"]:
        prepared[column] = prepared[column].astype("string").str.strip()

    invalid_binary_rows = {
        column: int((prepared[column].notna() & ~prepared[column].isin([0, 1])).sum())
        for column in BINARY_COLUMNS
    }
    invalid_category_rows = {
        "Geography": int((prepared["Geography"].notna() & ~prepared["Geography"].isin(EXPECTED_GEOGRAPHIES)).sum()),
        "Gender": int((prepared["Gender"].notna() & ~prepared["Gender"].isin(EXPECTED_GENDERS)).sum()),
    }

    duplicate_rows_removed = int(prepared["CustomerId"].duplicated(keep="first").sum())
    prepared = prepared.drop_duplicates(subset=["CustomerId"], keep="first").copy()

    core_fields = [
        "CustomerId",
        "CreditScore",
        "Geography",
        "Gender",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
        "Exited",
    ]
    missing_core_rows = int(prepared[core_fields].isna().any(axis=1).sum())
    prepared = prepared.dropna(subset=core_fields).copy()

    valid_binary_mask = prepared[BINARY_COLUMNS].isin([0, 1]).all(axis=1)
    valid_category_mask = prepared["Geography"].isin(EXPECTED_GEOGRAPHIES) & prepared["Gender"].isin(EXPECTED_GENDERS)
    invalid_rows_removed = int((~(valid_binary_mask & valid_category_mask)).sum())
    prepared = prepared.loc[valid_binary_mask & valid_category_mask].copy()

    prepared, thresholds = _make_segment_columns(prepared)
    metadata = {
        "source_profile": source_profile,
        "rows_after_duplicate_removal": int(len(df) - duplicate_rows_removed),
        "duplicate_rows_removed": duplicate_rows_removed,
        "rows_with_missing_core_fields_removed": missing_core_rows,
        "invalid_binary_rows_detected": invalid_binary_rows,
        "invalid_category_rows_detected": invalid_category_rows,
        "invalid_rows_removed_after_core_validation": invalid_rows_removed,
        "final_rows": int(len(prepared)),
        "final_columns": [str(column) for column in prepared.columns],
        "thresholds": thresholds,
        "extra_source_columns": [column for column in df.columns if column not in PORTAL_COLUMNS],
    }
    return prepared.reset_index(drop=True), metadata


def group_churn(df: pd.DataFrame, group_columns: str | Iterable[str]) -> pd.DataFrame:
    """Calculate count, rate, contribution, and relative-risk metrics by group."""

    if isinstance(group_columns, str):
        group_columns = [group_columns]
    group_columns = list(group_columns)
    missing = [column for column in group_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Grouping columns not found: {missing}")

    work = df.dropna(subset=group_columns + ["Exited"]).copy()
    total_churned = float(work["Exited"].sum())
    overall_rate = float(work["Exited"].mean()) if len(work) else 0.0
    if not len(work):
        return pd.DataFrame(columns=group_columns + GROUP_METRIC_COLUMNS)

    grouped = (
        work.groupby(group_columns, observed=False, dropna=False)["Exited"]
        .agg(customers="size", churned="sum")
        .reset_index()
    )
    grouped = grouped.loc[grouped["customers"].gt(0)].copy()
    grouped["churned"] = grouped["churned"].astype(int)
    grouped["retained"] = grouped["customers"] - grouped["churned"]
    grouped["churn_rate"] = grouped["churned"] / grouped["customers"]
    grouped["churn_contribution"] = np.where(
        total_churned > 0,
        grouped["churned"] / total_churned,
        np.nan,
    )
    grouped["risk_index"] = np.where(
        overall_rate > 0,
        grouped["churn_rate"] / overall_rate * 100,
        np.nan,
    )
    return grouped[group_columns + GROUP_METRIC_COLUMNS].sort_values(
        ["churn_rate", "customers"], ascending=[False, False]
    ).reset_index(drop=True)


def compute_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Return dashboard and report KPIs for a prepared customer table."""

    if len(df) == 0:
        raise ValueError("Cannot compute KPIs for an empty dataset")

    total = int(len(df))
    churned = int(df["Exited"].sum())
    retained = total - churned
    overall_rate = churned / total

    high_value = df["HighValueFlag"].astype(bool)
    high_value_total = int(high_value.sum())
    high_value_churned = int(df.loc[high_value, "Exited"].sum())
    high_value_rate = high_value_churned / high_value_total if high_value_total else np.nan
    balance_exposure = float(df.loc[high_value & df["Exited"].eq(1), "Balance"].sum())

    inactive = df["IsActiveMember"].eq(0)
    active = df["IsActiveMember"].eq(1)
    inactive_rate = float(df.loc[inactive, "Exited"].mean()) if inactive.any() else np.nan
    active_rate = float(df.loc[active, "Exited"].mean()) if active.any() else np.nan
    engagement_lift = inactive_rate / active_rate if active_rate and not np.isnan(active_rate) else np.nan

    return {
        "total_customers": total,
        "churned_customers": churned,
        "retained_customers": retained,
        "overall_churn_rate": overall_rate,
        "high_value_customers": high_value_total,
        "high_value_churned_customers": high_value_churned,
        "high_value_churn_rate": high_value_rate,
        "balance_exposure_high_value_churners": balance_exposure,
        "inactive_customers": int(inactive.sum()),
        "inactive_churn_rate": inactive_rate,
        "active_churn_rate": active_rate,
        "inactive_to_active_churn_rate_ratio": engagement_lift,
    }


def kpis_as_dataframe(kpis: dict[str, Any]) -> pd.DataFrame:
    """Convert KPI dictionary into a readable name/value table."""

    labels = {
        "total_customers": "Total customers",
        "churned_customers": "Churned customers",
        "retained_customers": "Retained customers",
        "overall_churn_rate": "Overall churn rate",
        "high_value_customers": "High-value customers",
        "high_value_churned_customers": "Churned high-value customers",
        "high_value_churn_rate": "High-value churn rate",
        "balance_exposure_high_value_churners": "Balance exposure of churned high-value customers",
        "inactive_customers": "Inactive customers",
        "inactive_churn_rate": "Inactive-customer churn rate",
        "active_churn_rate": "Active-customer churn rate",
        "inactive_to_active_churn_rate_ratio": "Inactive-to-active churn-rate ratio",
    }
    return pd.DataFrame(
        [{"KPI": labels.get(key, key), "Value": value} for key, value in kpis.items()]
    )
