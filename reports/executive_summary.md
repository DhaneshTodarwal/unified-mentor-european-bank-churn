# Executive Summary: European Banking Customer Churn

**Project:** Customer Segmentation & Churn Pattern Analytics in European Banking  
**Analysis date:** 14 October 2026  
**Dataset:** 10,000 customer records from the Unified Mentor project link

## Decision summary

The dataset's overall churn rate is **20.4%**. Retention priorities should begin with Germany, customers aged 46–59, inactive customers, and unusual high-product-count groups. High-balance customers should receive relationship-protection attention because churned high-value proxy customers represent balance exposure of **58,714,368.09** in the dataset's balance units.

## Key findings

| Area | Finding | Action implication |
| --- | --- | --- |
| Overall | 2,037 of 10,000 customers churned (20.4%). | Use this as the baseline for all segment comparisons. |
| Geography | Germany churned at 32.4%, versus 16.2% in France and 16.7% in Spain. | Prioritize Germany for root-cause investigation. |
| Age | The 46–59 group churned at 51.1%. | Design a focused retention journey for this group. |
| Activity | Inactive customers churned at 26.9%; active customers churned at 14.3%. | Prioritize re-engagement of inactive customers. |
| Products | Three- and four-product groups have unusually high churn, with small populations. | Validate product lifecycle and data quality before acting. |
| High-value proxy | High-value proxy churn is 23.0%; potential balance exposure is 58,714,368.09. | Protect high-balance relationships, but do not label balance as revenue. |

## Recommended sequence

1. Investigate Germany's customer experience, product mix, and inactivity pattern.
2. Build a retention list for inactive customers in high-risk geography-age segments.
3. Validate the three- and four-product records with business owners.
4. Create a high-balance relationship-review workflow.
5. Monitor churn rate, churn contribution, risk index, and balance exposure together.

## Important qualifications

The dataset is a 2025 customer snapshot. It does not include revenue, profit, transactions, complaints, service interactions, or product names. The analysis identifies associations and prioritization signals; it does not prove causes or forecast future churn. Balance exposure is not confirmed revenue loss.

The dashboard and research paper use the same cleaning rules, segmentation definitions, KPI formulas, and source file.
