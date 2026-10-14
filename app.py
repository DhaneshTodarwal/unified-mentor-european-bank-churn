"""Streamlit dashboard for customer segmentation and churn analytics."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from matplotlib.ticker import FuncFormatter

from src.analysis import clean_and_prepare, compute_kpis, group_churn, load_dataset


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "European_Bank.csv"

st.set_page_config(
    page_title="European Banking Churn Analytics",
    page_icon="📊",
    layout="wide",
)

sns.set_theme(style="whitegrid", context="notebook")


@st.cache_data
def get_data() -> tuple[pd.DataFrame, dict]:
    raw = load_dataset(DATA_PATH)
    return clean_and_prepare(raw)


def rate(value: float) -> str:
    return "n.a." if pd.isna(value) else f"{value:.1%}"


def amount(value: float) -> str:
    return "n.a." if pd.isna(value) else f"{value:,.2f}"


def churn_bar(table: pd.DataFrame, category: str, title: str, color: str = "#1f77b4"):
    plot_table = table.copy()
    plot_table[category] = plot_table[category].astype(str)
    plot_table = plot_table.sort_values("churn_rate", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    sns.barplot(data=plot_table, x="churn_rate", y=category, color=color, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Churn rate")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0%}"))
    fig.tight_layout()
    return fig


def show_group_table(data: pd.DataFrame, columns: str | list[str], title: str) -> None:
    table = group_churn(data, columns).copy()
    if table.empty:
        st.info("No data is available for the current filters.")
        return
    st.subheader(title)
    display = table.copy()
    for column in ["churn_rate", "churn_contribution"]:
        display[column] = display[column].map(rate)
    display["risk_index"] = display["risk_index"].map(lambda value: "n.a." if pd.isna(value) else f"{value:.0f}")
    st.dataframe(display, use_container_width=True, hide_index=True)


st.title("Customer Segmentation & Churn Pattern Analytics")
st.caption("European banking customer churn analysis | Source data year: 2025")

try:
    prepared, metadata = get_data()
except Exception as exc:  # pragma: no cover - shown to the dashboard user
    st.error(f"The dataset could not be loaded: {exc}")
    st.stop()

st.sidebar.header("Segment filters")


def select_values(label: str, column: str) -> list[str]:
    values = sorted(prepared[column].dropna().astype(str).unique().tolist())
    return st.sidebar.multiselect(label, values, default=values)


geographies = select_values("Geography", "Geography")
genders = select_values("Gender", "Gender")
age_groups = select_values("Age group", "AgeGroup")
tenure_groups = select_values("Tenure group", "TenureGroup")
credit_bands = select_values("Credit score band", "CreditScoreBand")
balance_segments = select_values("Balance segment", "BalanceSegment")
activity_status = select_values("Activity status", "ActivityStatus")
product_values = st.sidebar.multiselect(
    "Number of products",
    sorted(prepared["NumOfProducts"].dropna().astype(int).unique().tolist()),
    default=sorted(prepared["NumOfProducts"].dropna().astype(int).unique().tolist()),
)
high_value_choice = st.sidebar.radio("High-value proxy", ["All customers", "High-value only", "Other customers"])

filtered = prepared.copy()
for column, selected in [
    ("Geography", geographies),
    ("Gender", genders),
    ("AgeGroup", age_groups),
    ("TenureGroup", tenure_groups),
    ("CreditScoreBand", credit_bands),
    ("BalanceSegment", balance_segments),
    ("ActivityStatus", activity_status),
]:
    filtered = filtered[filtered[column].astype(str).isin(selected)]
filtered = filtered[filtered["NumOfProducts"].isin(product_values)]
if high_value_choice == "High-value only":
    filtered = filtered[filtered["HighValueFlag"]]
elif high_value_choice == "Other customers":
    filtered = filtered[~filtered["HighValueFlag"]]

if filtered.empty:
    st.warning("The current filter combination returns no customers. Adjust the sidebar selections.")
    st.stop()

kpis = compute_kpis(filtered)
overall_kpis = compute_kpis(prepared)

st.info(
    "Rates are calculated using the filtered customer population. The Geographic Risk Index is the segment churn rate divided by the overall churn rate, with 100 representing average risk."
)

metric_cols = st.columns(5)
metric_cols[0].metric("Customers", f"{kpis['total_customers']:,}")
metric_cols[1].metric("Churned", f"{kpis['churned_customers']:,}")
metric_cols[2].metric("Churn rate", rate(kpis["overall_churn_rate"]))
metric_cols[3].metric("High-value churn", rate(kpis["high_value_churn_rate"]))
metric_cols[4].metric("Balance exposure", amount(kpis["balance_exposure_high_value_churners"]))

tab_overview, tab_segments, tab_high_value, tab_method = st.tabs(
    ["Overview", "Segments", "High-value customers", "Methodology"]
)

with tab_overview:
    left, right = st.columns(2)
    with left:
        status = filtered["ChurnStatus"].value_counts().reindex(["Retained", "Churned"], fill_value=0)
        fig, ax = plt.subplots(figsize=(7, 4.4))
        bars = ax.bar(status.index, status.values, color=["#4c78a8", "#e45756"])
        ax.set_ylabel("Customers")
        ax.set_title("Retention status")
        for bar, value in zip(bars, status.values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + max(status.values) * 0.02, f"{value:,}", ha="center")
        fig.tight_layout()
        st.pyplot(fig, clear_figure=True)
    with right:
        show_group_table(filtered, "Geography", "Geography risk summary")

    st.subheader("Overall versus filtered population")
    comparison = pd.DataFrame(
        {
            "Population": ["All customers", "Current filters"],
            "Customers": [overall_kpis["total_customers"], kpis["total_customers"]],
            "Churned": [overall_kpis["churned_customers"], kpis["churned_customers"]],
            "Churn rate": [rate(overall_kpis["overall_churn_rate"]), rate(kpis["overall_churn_rate"])],
            "Inactive churn rate": [rate(overall_kpis["inactive_churn_rate"]), rate(kpis["inactive_churn_rate"])],
        }
    )
    st.dataframe(comparison, use_container_width=True, hide_index=True)

with tab_segments:
    geography_col, age_col = st.columns(2)
    with geography_col:
        geography_table = group_churn(filtered, "Geography")
        if not geography_table.empty:
            st.pyplot(churn_bar(geography_table, "Geography", "Churn by geography"), clear_figure=True)
    with age_col:
        age_table = group_churn(filtered, "AgeGroup")
        if not age_table.empty:
            st.pyplot(churn_bar(age_table, "AgeGroup", "Churn by age group", "#59a14f"), clear_figure=True)
    show_group_table(filtered, "TenureGroup", "Tenure-group churn")
    show_group_table(filtered, "CreditScoreBand", "Credit-score-band churn")
    show_group_table(filtered, "BalanceSegment", "Balance-segment churn")
    show_group_table(filtered, ["Geography", "AgeGroup"], "Geography and age interaction")

with tab_high_value:
    threshold = metadata["thresholds"]["high_value_balance_threshold_75th_percentile"]
    st.write(f"High-value proxy definition: positive balance at or above the 75th percentile ({amount(threshold)}).")
    high_value_table = group_churn(filtered, "HighValueFlag")
    if not high_value_table.empty:
        high_value_table["HighValueFlag"] = high_value_table["HighValueFlag"].map(
            {True: "High-value proxy", False: "Other customers"}
        )
        st.pyplot(churn_bar(high_value_table, "HighValueFlag", "High-value proxy churn", "#f58518"), clear_figure=True)
    st.metric("Potential balance exposure among churned high-value customers", amount(kpis["balance_exposure_high_value_churners"]))
    st.caption("This is balance exposure, not confirmed bank revenue loss. The dataset has no revenue or profit field.")

with tab_method:
    st.subheader("Definitions used in this dashboard")
    st.json(metadata["thresholds"])
    st.markdown(
        """
        **Data protection:** `Surname` is excluded from the analysis and no row-level customer information is displayed.\n\n
        **Engagement limitation:** `IsActiveMember` is a snapshot indicator. It does not prove that activity dropped over time.\n\n
        **Causality limitation:** the analysis identifies associations and segments. It does not prove that a variable causes churn.\n\n
        **Source quality:** the source file contains 10,000 rows, no missing values, no duplicate customer IDs, and valid binary fields after validation.
        """
    )
    st.subheader("Current filtered records")
    st.write(f"{len(filtered):,} customers match the current filters.")
