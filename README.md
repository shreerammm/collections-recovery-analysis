# Collections Recovery Analysis

## Project Overview

This project investigates the claim that collections recovery improved by 11% month-on-month. It includes data-quality checks, a Golden Payments Dataset workflow, monthly payment analysis, SQL queries, a targeting strategy investigation, and a dashboard.

## Dataset Notes

The challenge dataset intentionally includes duplicate records, missing values, inconsistent identifiers, conflicting timestamps, multiple time zones, late-arriving events, legacy codes, and inconsistent campaign definitions.

Raw datasets are excluded from Git using `.gitignore`. Generated CSV outputs are also excluded by default to avoid publishing row-level records without review.

## Project Structure

- `src/` — Python analysis scripts
- `sql/` — SQL analysis queries
- `notebooks/` — Jupyter analysis notebook
- `dashboard/` — Streamlit dashboard
- `quality_reports/` — Data-quality report
- `reports/` — Findings, executive summary, charts, and architecture diagram
- `.gitignore` — Excludes raw CSVs and temporary files

## Running the Project

Run commands from the project root in a Python environment with the required dependencies installed.

Build the Golden Payments Dataset:

```powershell
python .\src\build_golden_dataset.py
```

Run the SQL analysis:

```powershell
python .\src\run_sql.py
```

Analyze monthly recovery trends:

```powershell
python .\src\analyze_recovery_trend.py
```

Analyze targeting:

```powershell
python .\src\analyze_targeting_strategy.py
```

Launch the dashboard:

```powershell
streamlit run .\dashboard\app.py
```

## Key Finding

March 2026 showed an 11.11% month-on-month increase in gross successful payment amount. This isolated increase does not establish a sustained improvement in the overall recovery rate.

A defensible recovery-rate claim requires a defined denominator, treatment of reversals, comparable reporting periods, and reliable payment and account attribution. August 2026 contains partial-month data and should not be compared directly with a full month.

## Limitations

The targeting analysis is exploratory. A payment associated with a targeted account does not prove the targeting action caused the payment. Data-quality anomalies require investigation before drawing stronger conclusions.

## Deliverables

- Golden Dataset build script
- SQL analysis
- Jupyter notebook
- Data-quality report
- Statistical findings
- Counterfactual targeting strategy
- Executive summary
- Monthly trend charts
- Streamlit dashboard
- Architecture diagram
