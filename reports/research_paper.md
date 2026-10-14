# Customer Segmentation & Churn Pattern Analytics in European Banking

**Unified Mentor Data Analyst Internship Project**  
**Analysis date:** 14 October 2026  
**Source file:** [European_Bank.csv](https://drive.google.com/file/d/1TpMEWG4De0sD_P7_VJ7HtjT_89jlJHpQ/view?usp=drive_link)

## Abstract

This project analyzes 10,000 European banking customer records to understand churn patterns across geography, demographics, tenure, activity, credit score, products, and account balance. The overall churn rate is **20.4%**. Germany has the highest country-level churn rate at **32.4%**, while customers aged 46–59 have the highest age-group churn rate at **51.1%**. Inactive customers churn at **26.9%**, compared with **14.3%** for active customers. The analysis also identifies high-balance customers using a transparent top-quartile proxy and measures potential balance exposure without incorrectly treating it as confirmed revenue loss.

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

The linked source file contains **10,000 rows and 14 columns**. The portal brief lists the customer fields and the source file contains one additional field, `Year`. All records have `Year = 2025`, so it is retained as source metadata but not used for time-series analysis.

### Validation results

| Check | Result |
| --- | --- |
| Source rows | 10,000 |
| Final analysis rows | 10,000 |
| Duplicate customer IDs | 0 rows |
| Missing values in core fields | 0 rows |
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
- **Balance:** zero-balance, low-balance, and high-balance. Positive balances are split at their median of 119,839.69.
- **High-value proxy:** positive balance at or above the 75th percentile of positive balances, 139,512.29.

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

The dataset contains **10,000 customers**, of whom **2,037 exited** and **7,963 remained**. The overall churn rate is **20.4%**.

### 5.2 Geography

| Segment | Customers | Churned | Retained | Churn rate | Share of churners | Risk index |
| --- | --- | --- | --- | --- | --- | --- |
| Germany | 2509 | 814 | 1695 | 32.4% | 40.0% | 159 |
| Spain | 2477 | 413 | 2064 | 16.7% | 20.3% | 82 |
| France | 5014 | 810 | 4204 | 16.2% | 39.8% | 79 |

Germany is the highest-risk geography with a churn rate of **32.4%** and a risk index of **159**. Germany contributes **40.0%** of all churned customers. France has the largest customer population, but its churn rate is much lower than Germany's.

### 5.3 Age

| Segment | Customers | Churned | Retained | Churn rate | Share of churners | Risk index |
| --- | --- | --- | --- | --- | --- | --- |
| 46–59 | 1585 | 810 | 775 | 51.1% | 39.8% | 251 |
| 60+ | 526 | 147 | 379 | 27.9% | 7.2% | 137 |
| 30–45 | 6248 | 956 | 5292 | 15.3% | 46.9% | 75 |
| <30 | 1641 | 124 | 1517 | 7.6% | 6.1% | 37 |

The 46–59 group is the strongest age-related signal: **810 of 1,585 customers churned**, a rate of **51.1%**. The group contributes **39.8%** of all churners. Customers under 30 have the lowest observed churn rate.

### 5.4 Geography and age interaction

| Geography | Age group | Customers | Churned | Churn rate | Share of churners | Risk index |
| --- | --- | --- | --- | --- | --- | --- |
| Germany | 46–59 | 492 | 331 | 67.3% | 16.2% | 330 |
| France | 46–59 | 706 | 321 | 45.5% | 15.8% | 223 |
| Germany | 60+ | 123 | 51 | 41.5% | 2.5% | 204 |
| Spain | 46–59 | 387 | 158 | 40.8% | 7.8% | 200 |
| Germany | 30–45 | 1522 | 385 | 25.3% | 18.9% | 124 |
| France | 60+ | 274 | 68 | 24.8% | 3.3% | 122 |
| Spain | 60+ | 129 | 28 | 21.7% | 1.4% | 107 |
| Germany | <30 | 372 | 47 | 12.6% | 2.3% | 62 |
| Spain | 30–45 | 1558 | 195 | 12.5% | 9.6% | 61 |
| France | 30–45 | 3168 | 376 | 11.9% | 18.5% | 58 |
| Spain | <30 | 403 | 32 | 7.9% | 1.6% | 39 |
| France | <30 | 866 | 45 | 5.2% | 2.2% | 26 |

The highest interaction segment is **Germany customers aged 46–59**, with a churn rate of **67.3%** (331 churners from 492 customers). This segment should be checked for operational causes before a retention campaign is designed.

### 5.5 Engagement and tenure

| Segment | Customers | Churned | Retained | Churn rate | Share of churners | Risk index |
| --- | --- | --- | --- | --- | --- | --- |
| Inactive | 4849 | 1302 | 3547 | 26.9% | 63.9% | 132 |
| Active | 5151 | 735 | 4416 | 14.3% | 36.1% | 70 |

Inactive customers churn at **26.9%**, compared with **14.3%** among active customers. The inactive-to-active churn-rate ratio is **1.88×**. Inactive customers account for **63.9%** of all churners.

| Segment | Customers | Churned | Retained | Churn rate | Share of churners | Risk index |
| --- | --- | --- | --- | --- | --- | --- |
| New (0–2) | 2496 | 528 | 1968 | 21.2% | 25.9% | 104 |
| Mid-term (3–6) | 3977 | 821 | 3156 | 20.6% | 40.3% | 101 |
| Long-term (7+) | 3527 | 688 | 2839 | 19.5% | 33.8% | 96 |

Tenure differences are comparatively modest. New customers have a churn rate of approximately **21.2%**, while long-term customers are at approximately **19.5%**. Tenure should therefore be considered together with activity, geography, and age rather than used alone.

### 5.6 Demographic and credit-profile comparisons

**Gender**

| Segment | Customers | Churned | Retained | Churn rate | Share of churners | Risk index |
| --- | --- | --- | --- | --- | --- | --- |
| Female | 4543 | 1139 | 3404 | 25.1% | 55.9% | 123 |
| Male | 5457 | 898 | 4559 | 16.5% | 44.1% | 81 |

Female customers show a higher observed churn rate than male customers in this dataset. This is a descriptive difference, not evidence that gender causes churn. Recommendations should focus on the associated customer characteristics, not demographic stereotypes.

**Credit score**

| Segment | Customers | Churned | Retained | Churn rate | Share of churners | Risk index |
| --- | --- | --- | --- | --- | --- | --- |
| Low (<580) | 2362 | 520 | 1842 | 22.0% | 25.5% | 108 |
| Medium (580–669) | 3331 | 685 | 2646 | 20.6% | 33.6% | 101 |
| High (670+) | 4307 | 832 | 3475 | 19.3% | 40.8% | 95 |

Credit score has a smaller gradient than geography, age, activity, and product count. The low-score band is above the overall churn rate, but the difference is not sufficient by itself to explain churn.

### 5.7 Balance and high-value customers

| Segment | Customers | Churned | Retained | Churn rate | Share of churners | Risk index |
| --- | --- | --- | --- | --- | --- | --- |
| High-balance | 3191 | 771 | 2420 | 24.2% | 37.8% | 119 |
| Low-balance | 3192 | 766 | 2426 | 24.0% | 37.6% | 118 |
| Zero-balance | 3617 | 500 | 3117 | 13.8% | 24.5% | 68 |

Zero-balance customers have lower churn than positive-balance customers. Positive balance should not automatically be interpreted as customer value because the dataset does not include fees, profitability, or product revenue.

| Segment | Customers | Churned | Retained | Churn rate | Share of churners | Risk index |
| --- | --- | --- | --- | --- | --- | --- |
| High-value proxy | 1596 | 367 | 1229 | 23.0% | 18.0% | 113 |
| Other customers | 8404 | 1670 | 6734 | 19.9% | 82.0% | 98 |

There are **1,596 high-value proxy customers**. Their churn rate is **23.0%**, compared with **19.9%** for other customers. Churned high-value customers represent potential balance exposure of **58,714,368.09** in the dataset's balance units. This is not confirmed lost revenue.

### 5.8 Number of products

| Segment | Customers | Churned | Retained | Churn rate | Share of churners | Risk index |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | 60 | 60 | 0 | 100.0% | 2.9% | 491 |
| 3 | 266 | 220 | 46 | 82.7% | 10.8% | 406 |
| 1 | 5084 | 1409 | 3675 | 27.7% | 69.2% | 136 |
| 2 | 4590 | 348 | 4242 | 7.6% | 17.1% | 37 |

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
