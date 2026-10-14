# Project Requirements Notes

## Project identity

- **Project title:** Customer Segmentation & Churn Pattern Analytics in European Banking
- **Internship domain:** Data Analyst Intern
- **Portal assignment date:** 10 October 2026
- **Portal deadline:** 10 January 2027
- **Project type:** Descriptive and diagnostic customer-churn analytics with an interactive Streamlit dashboard
- **Primary business question:** Which customer segments are most exposed to churn, what characteristics are associated with churn, and where should retention efforts be focused?
- **Current scope:** Customer-level banking data, segmentation, churn comparison, KPI reporting, recommendations, and dashboard delivery
- **Not explicitly required:** Machine-learning prediction, causal inference, real-time data, or production deployment

## 1. What the project brief means

### Background and context

The brief frames customer churn as a business problem rather than only a classification problem. When a customer leaves a bank:

1. **Lifetime value decreases:** the bank loses future deposits, product usage, fees, and relationship value.
2. **Acquisition costs increase:** replacing an existing customer usually costs more than retaining one.
3. **Revenue becomes less stable:** a larger or less predictable churn base makes planning harder.

The brief says that banks may know the overall churn rate but still lack **granular segmentation insights**. Therefore, our work must go beyond one headline percentage. We need to compare churn rates and churn volumes across meaningful customer groups.

The three questions in the brief translate into:

- **Who is most likely to churn?** Calculate churn rates for every relevant segment, while also reporting each segment's customer count.
- **How does churn differ by country, age, and financial profile?** Compare geography, age, credit score, balance, salary, products, activity, and tenure.
- **Is churn concentrated among high-value or low-value customers?** Define a transparent high-value rule, identify churned high-value customers, and quantify the balance exposure. Do not call balance loss actual bank revenue unless revenue data exists.

### Problem statement

The brief identifies three operational difficulties:

- **Identifying high-risk segments:** a bank cannot target retention effectively without knowing which groups have above-average churn.
- **Understanding geographic and demographic differences:** country, age, and gender may show different churn patterns and require different interventions.
- **Quantifying the financial profile of churners:** churners should be compared by balance, salary, products, credit score, and activity—not only counted.

The phrase “generic, reactive, and inefficient” means the final recommendations must be specific and evidence-based. Every recommendation should name a segment, show the supporting KPI, and explain a possible retention action.

## 2. Exact project objectives translated into analysis tasks

### Primary objective 1: Measure overall churn rate

Formula:

`overall_churn_rate = sum(Exited) / count(valid_customers)`

Because `Exited` is a binary target, the sum represents the number of churned customers when values are validated as 0 and 1. Report both:

- churned-customer count;
- retained-customer count;
- total-customer count; and
- churn rate as a percentage.

### Primary objective 2: Identify churn distribution across customer segments

For each segment, report two different measures:

- **Segment churn rate:** `churned customers in segment / all customers in segment`.
- **Churn contribution:** `churned customers in segment / all churned customers`.

These must not be confused. A small segment can have the highest churn rate but contribute few churners; a large segment can have a moderate rate but contain most churned customers.

### Primary objective 3: Compare churn across European regions

The dataset lists France, Spain, and Germany. For each geography, show:

- customer count;
- churned count;
- retained count;
- churn rate;
- share of all churners;
- average or median balance; and
- average or median activity, products, and credit score.

Use counts alongside percentages so a small country group is not over-interpreted.

### Secondary objective 1: Understand high-value customer churn

The data has no explicit customer-value or revenue column. We must therefore define high value using a documented proxy. A practical first definition is:

`high_value = Balance above the 75th percentile of positive balances`

We should also show a sensitivity view using the median positive balance or another business-approved threshold. The final report must call the result **balance exposure** or **customer-value proxy exposure**, not confirmed revenue loss.

### Secondary objective 2: Evaluate engagement and tenure patterns

Engagement is represented by `IsActiveMember`, a binary snapshot. Tenure is represented by the number of years with the bank. We will compare:

- active versus inactive customer counts and churn rates;
- new, mid-term, and long-term tenure groups;
- the interaction of activity and tenure; and
- churn rates for inactive customers within each geography or age group.

The dataset is not longitudinal, so “engagement drop” cannot prove that a customer's activity fell over time. It is an inactivity-versus-churn indicator.

### Secondary objective 3: Support strategic planning and marketing decisions

Recommendations should be tied to findings. Examples of recommendation categories—not conclusions in advance—include:

- targeted retention outreach for above-average-risk segments;
- re-engagement campaigns for inactive customers;
- product-bundling or relationship review for customers with unusual product counts;
- high-balance customer service or loyalty interventions; and
- country- or age-specific communication strategies.

We must not claim that a variable causes churn. The analysis is observational and identifies associations.

## 3. Dataset fields and how each field will be used

| Field | Meaning in brief | Analytical treatment |
|---|---|---|
| `CustomerId` | Unique customer identifier | Use for uniqueness checks and row identification only. Do not expose it in public dashboard tables. |
| `Surname` | Customer surname | Potentially identifying and not analytically necessary. Remove from modeling/EDA and do not display. |
| `CreditScore` | Customer creditworthiness | Validate numeric range and missing values; compare score distributions by churn; create a documented score band. |
| `Geography` | France, Spain, or Germany | Main geographic dimension; validate allowed values and compare churn rate and churn contribution. |
| `Gender` | Male or Female | Demographic comparison; report carefully and avoid causal or stereotypical conclusions. |
| `Age` | Customer age | Validate plausible values; create mutually exclusive age bands and compare churn. |
| `Tenure` | Years with the bank | Validate non-negative values; create tenure groups and compare churn with activity and products. |
| `Balance` | Account balance | Check non-negative values; separate zero-balance customers; use positive-balance thresholds for value segmentation. |
| `NumOfProducts` | Number of bank products | Validate integer-like values; investigate one-product and multi-product behavior; check unusual values. |
| `HasCrCard` | Credit-card ownership indicator | Validate as binary; compare card ownership and churn, without assuming card ownership causes retention. |
| `IsActiveMember` | Activity indicator | Validate as binary; use active/inactive churn rates and an inactivity-risk indicator. |
| `EstimatedSalary` | Estimated annual salary | Compare distributions and bands by churn; treat as an estimated profile variable, not observed income. |
| `Exited` | Churn indicator/target | Validate as binary 0/1; this is the outcome used for all churn-rate calculations. |

### Expected row grain

The expected row grain is **one row per customer**. We must verify that `CustomerId` is unique. If duplicate IDs exist, we must investigate before calculating any KPI; otherwise customers could be counted twice.

## 4. Required data validation and cleaning

Before analysis, create a validation report with:

- row count and column count;
- duplicate `CustomerId` count;
- missing values by column;
- distinct values for categorical and binary fields;
- numeric minimum, maximum, mean, median, and selected percentiles;
- invalid or unexpected geography/gender values;
- binary-value violations in `HasCrCard`, `IsActiveMember`, and `Exited`;
- negative balances, salaries, ages, or tenure values;
- impossible or suspicious product counts; and
- the final number of rows retained and the reason for every exclusion.

Cleaning rules:

1. Remove or quarantine duplicate customer records after investigation.
2. Treat `CustomerId` as an identifier, not a numeric measure.
3. Remove `Surname` from analysis because it is unnecessary personal data.
4. Convert categorical columns to consistent text/category types.
5. Convert binary fields to integer or Boolean only after validating their values.
6. Do not silently replace invalid values with zero.
7. Document all missing-value decisions.
8. Preserve a raw dataset copy and create a separate cleaned dataset.

## 5. Segmentation design

The portal gives the dimensions but not all thresholds. We must document the thresholds before producing final numbers.

### Geography

- France
- Spain
- Germany

No additional geography should be invented. If an unexpected country appears, flag it as a data-quality issue.

### Age

The portal lists `<30`, `30–45`, `46–60`, and `60+`. The last two ranges overlap at age 60 if read literally. To make the groups mutually exclusive, use this provisional rule:

- `<30`: age below 30
- `30–45`: 30 through 45
- `46–59`: 46 through 59
- `60+`: 60 and above

Document this interpretation in the report. If the mentor requires the literal label “46–60,” use `61+` for the final group instead and record the decision.

### Credit score bands

The portal names Low, Medium, and High but gives no cutoffs. Proposed provisional cutoffs for a standard credit-score interpretation:

- Low: below 580
- Medium: 580–669
- High: 670 or above

Before final submission, check the dataset's actual range and record these thresholds. If the score is not a standard FICO-like score, use dataset tertiles or mentor-approved cutoffs instead.

### Tenure groups

The portal names New, Mid-term, and Long-term but gives no cutoffs. Proposed provisional rule:

- New: 0–2 years
- Mid-term: 3–6 years
- Long-term: 7 or more years

Also show tenure as a numeric variable so the chosen bands do not hide the underlying pattern.

### Balance segments

Proposed transparent rule:

- Zero-balance: `Balance == 0`
- Low-balance: positive balance at or below the median of positive balances
- High-balance: positive balance above the median of positive balances

For the high-value analysis, use a stricter top-quartile definition and label it clearly. This avoids calling every customer above the median “premium.”

## 6. Analysis methodology required by the portal

### Step 1: Data ingestion and validation

Load the dataset, inspect schema, verify the one-row-per-customer assumption, and generate the validation report before making charts.

### Step 2: Data cleaning and preparation

Remove `Surname`, standardize categorical values, validate binary fields, handle missing records, and create the derived segmentation columns.

### Step 3: Customer segmentation design

Create reusable fields such as:

- `AgeGroup`
- `CreditScoreBand`
- `TenureGroup`
- `BalanceSegment`
- `HighValueFlag`
- `ActivityStatus`

Keep the definitions in one configuration section so the dashboard and report use the same rules.

### Step 4: Churn distribution analysis

Produce:

- overall churn summary;
- churn rates by every major segment;
- churn contribution by segment;
- churned versus retained profile comparisons; and
- segment counts and confidence/context notes for small groups.

### Step 5: Comparative demographic analysis

Produce:

- gender churn comparison;
- geography-by-age heatmap or matrix;
- financial-profile comparisons by churn status; and
- interaction views such as geography × activity or age × tenure.

### Step 6: High-value customer churn analysis

Identify high-balance/high-value proxy customers, calculate their churn rate, count churned high-value customers, and calculate balance exposure:

`balance_exposure = sum(Balance for churned high_value customers)`

Do not present this as confirmed lost revenue. Also compare salary and balance patterns to avoid treating balance alone as complete customer value.

## 7. KPI definitions

| KPI | Recommended definition | Required guardrail |
|---|---|---|
| Overall Churn Rate | Total churned customers / total valid customers | Show numerator and denominator. |
| Segment Churn Rate | Churned customers in segment / all customers in segment | Include segment size. |
| High-Value Churn Ratio | Churned high-value customers / all high-value customers | State the high-value threshold. |
| Geographic Risk Index | Segment churn rate / overall churn rate × 100 | 100 = average risk; above 100 = above-average risk. |
| Engagement Drop Indicator | Inactive-customer churn rate compared with active-customer churn rate | Explain that this is a snapshot, not a time-series drop. |

Additional useful supporting KPIs:

- total customers;
- churned customers;
- retained customers;
- churn contribution;
- average/median balance of churners;
- balance exposure among churners;
- inactive-customer share; and
- high-value customer share.

## 8. Streamlit dashboard specification

### Required core modules

1. **Overall churn summary:** headline KPIs, churn versus retained chart, and short interpretation.
2. **Geography-wise churn visualization:** country counts, churn rates, and geographic risk index.
3. **Age and tenure comparison:** age/tenure charts, cross-tabs, and interaction filters.
4. **High-value customer churn explorer:** high-value definition, churn rate, counts, balance exposure, and profile breakdown.

### Required user capabilities

- segment filters;
- dynamic KPI updates when filters change;
- drill-down views from summary to segment; and
- clear labels showing whether a number is a rate, count, contribution, or index.

### Recommended dashboard layout

- Sidebar: geography, gender, age group, tenure group, activity status, credit band, balance segment, and high-value toggle.
- Page 1: executive overview.
- Page 2: geography and demographic analysis.
- Page 3: tenure, activity, products, and financial profile.
- Page 4: high-value churn and balance exposure.
- Footer or methodology panel: definitions, thresholds, data limitations, and last-refresh information.

The dashboard should not expose names, surnames, customer IDs, or row-level personal information. Use aggregated tables and charts.

## 9. Research paper structure

Recommended sections:

1. Title and author information
2. Executive abstract
3. Background and business context
4. Problem statement
5. Objectives and research questions
6. Dataset and data dictionary
7. Data validation and cleaning
8. Segmentation definitions
9. KPI definitions
10. Exploratory data analysis
11. Churn distribution findings
12. Demographic and geography findings
13. High-value customer and balance-exposure findings
14. Recommendations for retention strategy
15. Limitations and ethical considerations
16. Conclusion
17. Appendix with formulas, additional charts, and reproducibility details

Every major finding should include the relevant count, rate, denominator, and segment definition.

## 10. Executive summary for government stakeholders

This deliverable should be non-technical and decision-oriented. It should explain:

- why customer churn matters for banking stability and consumer service;
- which regions or customer groups show above-average churn;
- whether inactive or high-balance customers are disproportionately affected;
- what interventions are supported by the data;
- what should be monitored in future data collection; and
- what the analysis cannot prove.

Because the dataset is customer-level and observational, avoid presenting recommendations as regulatory conclusions. Use terms such as “associated with,” “observed pattern,” and “potential exposure.”

## 11. Important limitations and interpretation rules

- The data appears to be a customer snapshot, not a time series. We cannot measure month-by-month churn or prove that activity dropped before exit.
- There is no revenue, profit, fee, transaction, complaint, service-quality, or product-name field. Balance exposure is not actual revenue loss.
- The dataset does not prove that a variable causes churn.
- Segment rates can be unstable for small groups; always show counts and consider a minimum-size warning.
- Gender and geography comparisons should be descriptive and respectful, not stereotypes.
- “European banking” describes the project context and geography field; do not claim that the data represents all European banks.
- The research paper, dashboard, and executive summary must use the same cleaned data, thresholds, and KPI formulas.
- Any number shown in the dashboard must be reproducible from the dataset and filter state.

## 12. Acceptance checklist

### Data

- [ ] Raw dataset preserved
- [ ] Cleaned dataset created
- [ ] Duplicate and missing-value checks completed
- [ ] Binary and categorical values validated
- [ ] Derived segmentation rules documented
- [ ] Surname excluded from analysis and display

### Analysis

- [ ] Overall churn rate calculated
- [ ] Segment churn rates calculated
- [ ] Churn contribution calculated
- [ ] Churned versus retained comparison completed
- [ ] Geography and age interaction completed
- [ ] Activity and tenure analysis completed
- [ ] High-value churn analysis completed
- [ ] Balance exposure clearly separated from revenue claims
- [ ] Recommendations tied to measured evidence

### Dashboard

- [ ] Four required modules implemented
- [ ] Filters work
- [ ] KPIs update dynamically
- [ ] Drill-down views work
- [ ] No row-level personal information exposed
- [ ] Methodology and limitations visible
- [ ] Dashboard tested with all filters and empty/small selections

### Submission package

- [ ] Research paper
- [ ] Streamlit application and requirements file
- [ ] Executive summary
- [ ] README with run instructions
- [ ] Cleaned dataset or documented data-access instructions
- [ ] Screenshots or demo link if required
- [ ] Final quality review completed

## 13. Open decisions to resolve before final numbers

1. Confirm the actual dataset file, row count, and schema.
2. Confirm credit-score thresholds with the mentor or document the proposed thresholds.
3. Confirm tenure thresholds.
4. Confirm whether high value should be top-quartile balance, median positive balance, or another business rule.
5. Confirm what the portal means by “revenue risk,” since revenue is not present in the supplied fields.
6. Confirm the expected research-paper format and page length.
7. Confirm whether the Streamlit app must be hosted or whether source code and screenshots are enough.
8. Confirm whether the executive summary must use a government-policy framing or simply a formal stakeholder style.

## 14. First implementation sequence

1. Download or obtain the dataset from the portal's **Access Dataset** link.
2. Save an untouched raw copy and inspect the file format.
3. Generate a data-quality report and data dictionary.
4. Create the cleaned dataset and derived segmentation fields.
5. Build a baseline analysis notebook/script with the KPI formulas.
6. Create the core charts and identify the strongest findings.
7. Build the Streamlit dashboard from the same analysis functions.
8. Write the research paper and executive summary from verified results.
9. Run the acceptance checklist and prepare the final submission package.

## Working interpretation

This is an end-to-end portfolio analytics project. Our goal is not merely to make charts; it is to produce a reproducible decision tool that explains **where churn is concentrated, which customers represent the greatest potential exposure, and what retention actions are justified by the evidence**.
