# Collections Recovery Analysis

## Project Overview

This project investigates the claim that collections recovery improved by 11% month-on-month using a dataset containing 17 relational tables.

The analysis builds a Golden Payments Dataset, assesses data quality, analyzes monthly successful payments, investigates targeting inconsistencies, and proposes a counterfactual targeting strategy.

## Dataset Notes

The challenge dataset intentionally contains:
- Duplicate rows and payment events
- Missing values and inconsistent identifiers
- Conflicting timestamps and multiple time zones
- Late-arriving events and schema versions
- Legacy disposition codes
- Multiple agent identifiers and conflicting agent attributes
- Inconsistent campaign definitions and overwritten-style status history

These issues are documented as data-quality risks and are not automatically assumed to be invalid business records.

## Project Structure

- `data_staging/` — staged source datasets
- `data_rejected_review/` — records flagged for review
- `src/` — Python analysis scripts
- `sql/` — SQL queries for recovery and quality analysis
- `notebooks/` — exploratory analysis notebook
- `quality_reports/` — data-quality checks and SQL outputs
- `reports/` — Golden Dataset, statistical findings, charts, and executive summary
- `dashboard/` — Streamlit dashboard

## How to Run

Run commands from the project root in the VS Code terminal.

Build the Golden Dataset:

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

Analyze targeting strategy:

```powershell
python .\src\analyze_targeting_strategy.py
```

Launch the dashboard:

```powershell
streamlit run .\dashboard\app.py
```

If a required Python package is missing, install it in your active project environment before rerunning the command.

## Key Finding

March 2026 recorded an 11.11% month-on-month increase in gross successful payment amount. This isolated increase does not establish a sustained improvement in recovery performance.

A defensible recovery-rate claim requires a clearly defined denominator, treatment of reversals and payment attribution, comparable reporting periods, and reliable account and agent identities. August 2026 contains only partial-month data and should not be compared directly with a full month.

## Limitations

Targeting and payment analyses are exploratory. A payment linked to a targeted account does not establish that the targeting action caused the payment. Campaign-date, channel, identity, and relationship anomalies require further investigation.

## Main Deliverables

- Golden Payments Dataset and quality summary
- Data-quality report and SQL query outputs
- Monthly recovery analysis and statistical findings
- Counterfactual targeting strategy
- Executive summary
- Monthly trend charts
- Interactive dashboard
- Architecture diagram
