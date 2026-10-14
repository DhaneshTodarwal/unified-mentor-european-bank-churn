"""Generate the research paper and stakeholder summary from computed outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analysis import clean_and_prepare, compute_kpis, group_churn, load_dataset


SOURCE_PATH = ROOT / "data" / "European_Bank.csv"
REPORT_DIR = ROOT / "reports"
REPORT_DATE = "14 October 2026"
DATASET_URL = "https://drive.google.com/file/d/1TpMEWG4De0sD_P7_VJ7HtjT_89jlJHpQ/view?usp=drive_link"


def pct(value: float) -> str:
    return "n.a." if pd.isna(value) else f"{value:.1%}"


def number(value: float) -> str:
    return f"{value:,.0f}"


def amount(value: float) -> str:
    return f"{value:,.2f}"


def markdown_table(table: pd.DataFrame, columns: list[str], labels: dict[str, str] | None = None) -> str:
    labels = labels or {}
    display = table[columns].copy()
    display = display.rename(columns=labels)
    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    rows = [header, separator]
    for _, row in display.iterrows():
        rows.append("| " + " | ".join(str(value) for value in row.tolist()) + " |")
    return "\n".join(rows)


def format_segment_table(table: pd.DataFrame, category: str) -> str:
    display = table.copy()
    display[category] = display[category].astype(str)
    display["churn_rate"] = display["churn_rate"].map(pct)
    display["churn_contribution"] = display["churn_contribution"].map(pct)
    display["risk_index"] = display["risk_index"].map(lambda value: "n.a." if pd.isna(value) else f"{value:.0f}")
    return markdown_table(
        display,
        [category, "customers", "churned", "retained", "churn_rate", "churn_contribution", "risk_index"],
        {
            category: "Segment",
            "customers": "Customers",
            "churned": "Churned",
            "retained": "Retained",
            "churn_rate": "Churn rate",
            "churn_contribution": "Share of churners",
            "risk_index": "Risk index",
        },
    )


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    raw = load_dataset(SOURCE_PATH)
    prepared, metadata = clean_and_prepare(raw)
    kpis = compute_kpis(prepared)
    geography = group_churn(prepared, "Geography")
    age = group_churn(prepared, "AgeGroup")
    tenure = group_churn(prepared, "TenureGroup")
    gender = group_churn(prepared, "Gender")
    credit = group_churn(prepared, "CreditScoreBand")
    balance = group_churn(prepared, "BalanceSegment")
    activity = group_churn(prepared, "ActivityStatus")
    products = group_churn(prepared, "NumOfProducts")
    high_value = group_churn(prepared, "HighValueFlag")
    geography_age = group_churn(prepared, ["Geography", "AgeGroup"])

    high_value_threshold = metadata["thresholds"]["high_value_balance_threshold_75th_percentile"]
    median_positive_balance = metadata["thresholds"]["median_positive_balance"]
    germany = geography.loc[geography["Geography"].eq("Germany")].iloc[0]
    inactive = activity.loc[activity["ActivityStatus"].eq("Inactive")].iloc[0]
    active = activity.loc[activity["ActivityStatus"].eq("Active")].iloc[0]
    top_age = age.sort_values("churn_rate", ascending=False).iloc[0]
    top_geo_age = geography_age.sort_values("churn_rate", ascending=False).iloc[0]
    high_value_row = high_value.loc[high_value["HighValueFlag"].eq(True)].iloc[0]
    other_value_row = high_value.loc[high_value["HighValueFlag"].eq(False)].iloc[0]

    validation_json = json.dumps(metadata, indent=2, default=str)
    paper = f"""# Customer Segmentation & Churn Pattern Analytics in European Banking

**Unified Mentor Data Analyst Internship Project**  
**Analysis date:** {REPORT_DATE}  
**Source file:** [European_Bank.csv]({DATASET_URL})

## Abstract

This project analyzes 10,000 European banking customer records to understand churn patterns across geography, demographics, tenure, activity, credit score, products, and account balance. The overall churn rate is **{pct(kpis['overall_churn_rate'])}**. Germany has the highest country-level churn rate at **{pct(germany['churn_rate'])}**, while customers aged 46–59 have the highest age-group churn rate at **{pct(top_age['churn_rate'])}**. Inactive customers churn at **{pct(inactive['churn_rate'])}**, compared with **{pct(active['churn_rate'])}** for active customers. The analysis also identifies high-balance customers using a transparent top-quartile proxy and measures potential balance exposure without incorrectly treating it as confirmed revenue loss.

The deliverables are a reproducible analysis, an interactive Streamlit dashboard, this research paper, and an executive summary. Findings describe associations in a customer snapshot; they do not establish causality.

## 1. Background and business context

Customer churn creates three business pressures for retail banks:

- lower future customer lifetime value;
- higher replacement and acquisition costs; and
- less stable revenue and relationship planning.

The project brief asks for segmentation-driven analysis rather than one overall churn percentage. The business questions are:

1. Which customer groups are most likely to churn?
2. How does churn differ across countries, age groups, and financial profiles?
3. Is churn concentrated among high-value or low-value customers?

## 2. Problem statement and objectives

Banks may have customer-level data but still lack practical answers about high-risk segments, geographic and demographic differences, and the financial profile of churned customers. This project addresses that gap through reproducible segmentation and KPI analysis.

### Primary objectives

- Measure the overall churn rate.
- Identify churn distribution across customer segments.
- Compare churn behavior across France, Spain, and Germany.

### Secondary objectives

- Understand churn among high-value customers.
- Evaluate engagement and tenure patterns.
- Support targeted retention and marketing decisions.

## 3. Dataset and data quality

The linked source file contains **{len(raw):,} rows and {len(raw.columns)} columns**. The portal brief lists the customer fields and the source file contains one additional field, `Year`. All records have `Year = 2025`, so it is retained as source metadata but not used for time-series analysis.

### Validation results

| Check | Result |
| --- | --- |
| Source rows | {len(raw):,} |
| Final analysis rows | {len(prepared):,} |
| Duplicate customer IDs | {metadata['source_profile']['duplicate_customer_id_rows']:,} rows |
| Missing values in core fields | {metadata['rows_with_missing_core_fields_removed']:,} rows |
| Invalid binary values | None detected |
| Unexpected geographies | None detected |
| Unexpected genders | None detected |
| Year coverage | 2025 only |

The source is analytically usable without row removal. `Surname` is excluded from analysis because it is not needed and may identify customers. `CustomerId` is used for uniqueness validation and is not displayed in the dashboard.

## 4. Analytical methodology

### Data preparation

1. Load the raw CSV and preserve an untouched copy.
2. Convert numeric fields to numeric types and normalize text fields.
3. Validate the one-row-per-customer assumption.
4. Validate the binary fields `HasCrCard`, `IsActiveMember`, and `Exited`.
5. Exclude `Surname` from analytical outputs.
6. Create reusable segmentation fields.

### Segmentation definitions

The portal names several groups but does not provide all cutoffs. The project therefore uses documented provisional definitions:

- **Age:** `<30`, `30–45`, `46–59`, `60+`. The portal's written `46–60` and `60+` ranges overlap at age 60, so the implementation uses 46–59 and 60+ to make groups mutually exclusive.
- **Credit score:** Low `<580`, Medium `580–669`, High `670+`.
- **Tenure:** New `0–2`, Mid-term `3–6`, Long-term `7+` years.
- **Balance:** zero-balance, low-balance, and high-balance. Positive balances are split at their median of {amount(median_positive_balance)}.
- **High-value proxy:** positive balance at or above the 75th percentile of positive balances, {amount(high_value_threshold)}.

### KPI formulas

- Overall churn rate = churned customers / all valid customers.
- Segment churn rate = churned customers in segment / all customers in segment.
- Churn contribution = churned customers in segment / all churned customers.
- Geographic risk index = segment churn rate / overall churn rate × 100.
- High-value churn ratio = churned high-value customers / all high-value customers.
- Balance exposure = sum of balances for churned high-value customers.

Churn rate and churn contribution are different measures. Every table reports counts alongside percentages so small segments are not over-interpreted.

## 5. Results and findings

### 5.1 Overall churn

The dataset contains **{number(kpis['total_customers'])} customers**, of whom **{number(kpis['churned_customers'])} exited** and **{number(kpis['retained_customers'])} remained**. The overall churn rate is **{pct(kpis['overall_churn_rate'])}**.

### 5.2 Geography

{format_segment_table(geography, 'Geography')}

Germany is the highest-risk geography with a churn rate of **{pct(germany['churn_rate'])}** and a risk index of **{germany['risk_index']:.0f}**. Germany contributes **{pct(germany['churn_contribution'])}** of all churned customers. France has the largest customer population, but its churn rate is much lower than Germany's.

### 5.3 Age

{format_segment_table(age, 'AgeGroup')}

The 46–59 group is the strongest age-related signal: **{number(top_age['churned'])} of {number(top_age['customers'])} customers churned**, a rate of **{pct(top_age['churn_rate'])}**. The group contributes **{pct(top_age['churn_contribution'])}** of all churners. Customers under 30 have the lowest observed churn rate.

### 5.4 Geography and age interaction

{markdown_table(
    geography_age.assign(
        churn_rate=geography_age['churn_rate'].map(pct),
        churn_contribution=geography_age['churn_contribution'].map(pct),
        risk_index=geography_age['risk_index'].map(lambda value: f"{value:.0f}"),
    ),
    ['Geography', 'AgeGroup', 'customers', 'churned', 'churn_rate', 'churn_contribution', 'risk_index'],
    {'Geography': 'Geography', 'AgeGroup': 'Age group', 'customers': 'Customers', 'churned': 'Churned', 'churn_rate': 'Churn rate', 'churn_contribution': 'Share of churners', 'risk_index': 'Risk index'},
)}

The highest interaction segment is **{top_geo_age['Geography']} customers aged {top_geo_age['AgeGroup']}**, with a churn rate of **{pct(top_geo_age['churn_rate'])}** ({number(top_geo_age['churned'])} churners from {number(top_geo_age['customers'])} customers). This segment should be checked for operational causes before a retention campaign is designed.

### 5.5 Engagement and tenure

{format_segment_table(activity, 'ActivityStatus')}

Inactive customers churn at **{pct(inactive['churn_rate'])}**, compared with **{pct(active['churn_rate'])}** among active customers. The inactive-to-active churn-rate ratio is **{kpis['inactive_to_active_churn_rate_ratio']:.2f}×**. Inactive customers account for **{pct(inactive['churn_contribution'])}** of all churners.

{format_segment_table(tenure, 'TenureGroup')}

Tenure differences are comparatively modest. New customers have a churn rate of approximately **{pct(tenure.loc[tenure['TenureGroup'].eq('New (0–2)'),'churn_rate'].iloc[0])}**, while long-term customers are at approximately **{pct(tenure.loc[tenure['TenureGroup'].eq('Long-term (7+)'),'churn_rate'].iloc[0])}**. Tenure should therefore be considered together with activity, geography, and age rather than used alone.

### 5.6 Demographic and credit-profile comparisons

**Gender**

{format_segment_table(gender, 'Gender')}

Female customers show a higher observed churn rate than male customers in this dataset. This is a descriptive difference, not evidence that gender causes churn. Recommendations should focus on the associated customer characteristics, not demographic stereotypes.

**Credit score**

{format_segment_table(credit, 'CreditScoreBand')}

Credit score has a smaller gradient than geography, age, activity, and product count. The low-score band is above the overall churn rate, but the difference is not sufficient by itself to explain churn.

### 5.7 Balance and high-value customers

{format_segment_table(balance, 'BalanceSegment')}

Zero-balance customers have lower churn than positive-balance customers. Positive balance should not automatically be interpreted as customer value because the dataset does not include fees, profitability, or product revenue.

{format_segment_table(high_value.assign(HighValueFlag=high_value['HighValueFlag'].map({True: 'High-value proxy', False: 'Other customers'})), 'HighValueFlag')}

There are **{number(kpis['high_value_customers'])} high-value proxy customers**. Their churn rate is **{pct(high_value_row['churn_rate'])}**, compared with **{pct(other_value_row['churn_rate'])}** for other customers. Churned high-value customers represent potential balance exposure of **{amount(kpis['balance_exposure_high_value_churners'])}** in the dataset's balance units. This is not confirmed lost revenue.

### 5.8 Number of products

{format_segment_table(products, 'NumOfProducts')}

Product count is a strong observed discriminator. Customers with four products have a 100% churn rate, but the group contains only 60 customers. Customers with three products also show very high churn, while the two-product group has the lowest rate. These values should be validated with the mentor because product counts of three and four may represent a data or business-process issue rather than a stable causal pattern.

## 6. Recommendations

The recommendations below are directly connected to the observed patterns:

1. **Prioritize Germany for retention diagnostics.** Germany has the highest churn rate and risk index. Review product mix, service interactions, and inactive-customer share in that country before deploying a country-specific campaign.
2. **Create a focused 46–59 retention segment.** This age group has the highest churn across the overall dataset and within each geography. Use tailored relationship reviews rather than generic messaging.
3. **Run an inactivity re-engagement program.** Inactive customers churn at roughly 1.88 times the active-customer rate. Prioritize inactive customers in high-risk geography-age combinations.
4. **Investigate three- and four-product customers.** Their churn rates are extreme, but the groups are small. Confirm whether these product counts represent product closures, data quality issues, or genuinely unstable relationships.
5. **Protect high-balance relationships.** High-value proxy customers have slightly higher churn and meaningful balance exposure. Use balance as a prioritization signal, not as a complete customer-value measure.
6. **Track segment rates and counts together.** Retention teams should monitor churn rate, churner volume, risk index, and potential balance exposure for every campaign.

## 7. Dashboard design

The Streamlit application implements the portal requirements through:

- an overall churn summary;
- geography-wise churn visualization;
- age and tenure comparisons;
- credit, balance, activity, and product tables;
- a high-value customer explorer;
- filters for all major segments;
- dynamic KPI updates; and
- geography-age drill-down analysis.

The dashboard excludes surnames and does not display row-level customer records.

## 8. Limitations and ethical considerations

- All rows are from 2025, so the dataset does not support time-series churn analysis.
- There is no revenue, profit, transaction, complaint, service-quality, or product-name field.
- Balance exposure is a proxy, not actual revenue loss.
- The data is observational and does not establish causality.
- Small groups, especially three- and four-product customers, require caution.
- Demographic and geographic comparisons must not be converted into stereotypes or automatic adverse decisions.
- The dashboard should support human review and targeted investigation, not automatically deny service or pricing.

## 9. Conclusion

The most important observed churn signals are geography, age, activity status, and number of products. Germany and the 46–59 age group have the strongest segment-level risk, inactive customers account for most churners, and high-value customers show meaningful potential balance exposure. The resulting dashboard and written deliverables provide a reproducible starting point for retention analysis while clearly separating observed associations from unsupported causal or revenue claims.

## Appendix: reproducibility

Run the following commands from the project root:

```bash
python3 scripts/build_analysis_outputs.py
python3 -m unittest discover -s tests -v
streamlit run app.py
```

The source data is preserved under `data/`, the prepared internal analysis data is under `data/processed/`, and computed tables/charts are under `outputs/`.
"""

    summary = f"""# Executive Summary: European Banking Customer Churn

**Project:** Customer Segmentation & Churn Pattern Analytics in European Banking  
**Analysis date:** {REPORT_DATE}  
**Dataset:** 10,000 customer records from the Unified Mentor project link

## Decision summary

The dataset's overall churn rate is **{pct(kpis['overall_churn_rate'])}**. Retention priorities should begin with Germany, customers aged 46–59, inactive customers, and unusual high-product-count groups. High-balance customers should receive relationship-protection attention because churned high-value proxy customers represent balance exposure of **{amount(kpis['balance_exposure_high_value_churners'])}** in the dataset's balance units.

## Key findings

| Area | Finding | Action implication |
| --- | --- | --- |
| Overall | {number(kpis['churned_customers'])} of {number(kpis['total_customers'])} customers churned ({pct(kpis['overall_churn_rate'])}). | Use this as the baseline for all segment comparisons. |
| Geography | Germany churned at {pct(germany['churn_rate'])}, versus {pct(geography.loc[geography['Geography'].eq('France'),'churn_rate'].iloc[0])} in France and {pct(geography.loc[geography['Geography'].eq('Spain'),'churn_rate'].iloc[0])} in Spain. | Prioritize Germany for root-cause investigation. |
| Age | The 46–59 group churned at {pct(top_age['churn_rate'])}. | Design a focused retention journey for this group. |
| Activity | Inactive customers churned at {pct(inactive['churn_rate'])}; active customers churned at {pct(active['churn_rate'])}. | Prioritize re-engagement of inactive customers. |
| Products | Three- and four-product groups have unusually high churn, with small populations. | Validate product lifecycle and data quality before acting. |
| High-value proxy | High-value proxy churn is {pct(high_value_row['churn_rate'])}; potential balance exposure is {amount(kpis['balance_exposure_high_value_churners'])}. | Protect high-balance relationships, but do not label balance as revenue. |

## Recommended sequence

1. Investigate Germany's customer experience, product mix, and inactivity pattern.
2. Build a retention list for inactive customers in high-risk geography-age segments.
3. Validate the three- and four-product records with business owners.
4. Create a high-balance relationship-review workflow.
5. Monitor churn rate, churn contribution, risk index, and balance exposure together.

## Important qualifications

The dataset is a 2025 customer snapshot. It does not include revenue, profit, transactions, complaints, service interactions, or product names. The analysis identifies associations and prioritization signals; it does not prove causes or forecast future churn. Balance exposure is not confirmed revenue loss.

The dashboard and research paper use the same cleaning rules, segmentation definitions, KPI formulas, and source file.
"""

    (REPORT_DIR / "research_paper.md").write_text(paper, encoding="utf-8")
    (REPORT_DIR / "executive_summary.md").write_text(summary, encoding="utf-8")
    print(f"Wrote {REPORT_DIR / 'research_paper.md'}")
    print(f"Wrote {REPORT_DIR / 'executive_summary.md'}")


if __name__ == "__main__":
    main()
