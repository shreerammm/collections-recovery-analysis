
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data_staging"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

# Load payment data
payments = pd.read_csv(DATA / "payments.csv", low_memory=False)
payments["event_at"] = pd.to_datetime(
    payments["event_at"], errors="coerce", utc=True
)
payments["amount"] = pd.to_numeric(
    payments["amount"], errors="coerce"
)

payments["month"] = payments["event_at"].dt.to_period("M").astype(str)

# Keep all statuses visible; do not count failed, pending or reversed
# transactions as successful recovery.
print("\nPayment status counts:")
print(payments["payment_status"].value_counts(dropna=False).to_string())

# Summary of successful gross payment amounts.
# This is NOT yet a net recovery rate.
success = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
].copy()

monthly = success.groupby("month").agg(
    successful_rows=("payment_id", "size"),
    distinct_payment_ids=("payment_id", "nunique"),
    distinct_accounts=("account_id", "nunique"),
    gross_success_amount=("amount", "sum")
).reset_index().sort_values("month")

monthly["amount_change_pct"] = (
    monthly["gross_success_amount"].pct_change() * 100
)
monthly["payment_id_change_pct"] = (
    monthly["distinct_payment_ids"].pct_change() * 100
)
monthly["account_change_pct"] = (
    monthly["distinct_accounts"].pct_change() * 100
)

monthly.to_csv(REPORTS / "monthly_recovery_analysis.csv", index=False)

print("\nMonthly successful payment analysis:")
print(monthly.round(2).to_string(index=False))

# Summarize data limitations for the report.
quality = {
    "payment_rows": len(payments),
    "missing_payment_references": int(payments["payment_reference"].isna().sum()),
    "duplicate_payment_id_rows": int(
        payments.duplicated("payment_id", keep=False).sum()
    ),
    "missing_event_dates": int(payments["event_at"].isna().sum()),
    "missing_or_invalid_amounts": int(payments["amount"].isna().sum()),
}

quality_df = pd.DataFrame(
    [{"check": key, "value": value} for key, value in quality.items()]
)
quality_df.to_csv(REPORTS / "payment_quality_summary.csv", index=False)

print("\nPayment quality summary:")
print(quality_df.to_string(index=False))

print(f"\nReports saved in: {REPORTS}")
print(
    "Important: gross successful amounts are descriptive only. "
    "They do not prove an 11% improvement in recovery rate."
)
