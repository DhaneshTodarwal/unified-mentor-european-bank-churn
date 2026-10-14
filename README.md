# Customer Segmentation & Churn Pattern Analytics in European Banking

This project implements the Unified Mentor Data Analyst internship assignment using the linked `European_Bank.csv` dataset.

## Project outputs

- `src/analysis.py`: reusable validation, cleaning, segmentation, KPI, and churn-table logic
- `scripts/build_analysis_outputs.py`: reproducible output and chart generation
- `app.py`: interactive Streamlit dashboard
- `reports/research_paper.md`: detailed research paper
- `output/pdf/European_Banking_Churn_Research_Paper.pdf`: submission-ready PDF research paper
- `reports/executive_summary.md`: stakeholder summary
- `outputs/`: validation report, KPI tables, segment tables, and charts
- `submission/FEEDBACK_VIDEO_SCRIPT.md`: script and recording checklist for the required feedback video
- `submission/SUBMISSION_CHECKLIST.md`: four portal URL requirements and access rules

## Run the analysis

```bash
python3 scripts/build_analysis_outputs.py
```

The script reads `data/European_Bank.csv`, writes the prepared analysis data to `data/processed/`, and creates tables/charts under `outputs/`.

## Run the dashboard

Install the dependencies from `requirements.txt`, then run:

```bash
streamlit run app.py
```

## Submission preparation

The Unified Mentor portal requires four HTTPS URLs: a GitHub repository, a research-paper link, a live deployed dashboard link, and a project-feedback video link. Google Drive is suitable for the research-paper PDF and an optional backup ZIP, but it is not a live deployment host for the Streamlit dashboard.

## Definitions

The portal brief does not specify every threshold. The project uses documented provisional definitions:

- Age: `<30`, `30–45`, `46–59`, `60+`
- Credit score: Low `<580`, Medium `580–669`, High `670+`
- Tenure: New `0–2`, Mid-term `3–6`, Long-term `7+`
- High-value proxy: positive balance at or above the 75th percentile of positive balances

Balance exposure is not reported as actual revenue loss because the dataset has no revenue or profit field.
