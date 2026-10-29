
from pathlib import Path
import pandas as pd

root = Path.cwd()
data_dir = root / "data_staging"
out_dir = root / "quality_reports"
out_dir.mkdir(exist_ok=True)

payments = pd.read_csv(data_dir / "payments.csv", low_memory=False)
accounts = pd.read_csv(data_dir / "accounts.csv", low_memory=False)
status_history = pd.read_csv(
    data_dir / "account_status_history.csv", low_memory=False
)

def show_date_range(df, column, label):
    dates = pd.to_datetime(df[column], errors="coerce", utc=True)
    print(f"\n--- {label}: {column} ---")
    print("Rows:", len(df))
    print("Unparseable or missing dates:", int(dates.isna().sum()))
    print("Earliest date:", dates.min())
    print("Latest date:", dates.max())

# 1. Check the date coverage.
show_date_range(payments, "event_at", "Payments")
show_date_range(accounts, "opened_at", "Accounts")
show_date_range(status_history, "event_at", "Account status history")

# 2. Inspect payment statuses before deciding what counts as a recovery.
print("\n--- Payment status counts ---")
print(
    payments["payment_status"]
    .fillna("<MISSING>")
    .value_counts(dropna=False)
    .to_string()
)

# 3. Inspect payment amounts and possible invalid values.
amounts = pd.to_numeric(payments["amount"], errors="coerce")

print("\n--- Payment amount checks ---")
print("Amounts that cannot be parsed:", int(amounts.isna().sum()))
print("Zero or negative amounts:", int((amounts <= 0).sum()))
print("Positive amount total (all statuses):", round(
    amounts[amounts > 0].sum(), 2
))
print("Amount summary:")
print(amounts.describe().to_string())

# 4. Check payment identifiers and repeated IDs.
print("\n--- Payment ID checks ---")
print("Rows:", len(payments))
print("Distinct payment IDs:", payments["payment_id"].nunique())
print("Missing payment IDs:", int(payments["payment_id"].isna().sum()))
print(
    "Rows with repeated payment IDs:",
    int(payments["payment_id"].duplicated(keep=False).sum())
)
print(
    "Rows with missing payment references:",
    int(payments["payment_reference"].isna().sum())
)

# 5. Check account ID quality and payment-to-account linkage.
account_ids = set(accounts["account_id"].dropna())
payment_account = payments["account_id"]
unmatched_mask = (
    payment_account.notna() & ~payment_account.isin(account_ids)
)

print("\n--- Payment-to-account linkage ---")
print("Accounts rows:", len(accounts))
print("Distinct account IDs:", accounts["account_id"].nunique())
print("Missing account IDs in accounts:", int(accounts["account_id"].isna().sum()))
print("Payments with missing account ID:", int(payment_account.isna().sum()))
print("Payments linked to unknown account IDs:", int(unmatched_mask.sum()))
print(
    "Distinct unknown account IDs:",
    payment_account[unmatched_mask].nunique()
)

# 6. Inspect account status and delinquency coverage.
for column in ["status", "risk_segment", "loan_type", "timezone"]:
    if column in accounts.columns:
        print(f"\n--- Account {column} counts ---")
        print(accounts[column].fillna("<MISSING>").value_counts().head(25).to_string())

for column in ["dpd", "outstanding_amount", "principal_amount"]:
    if column in accounts.columns:
        values = pd.to_numeric(accounts[column], errors="coerce")
        print(f"\n--- Account {column} summary ---")
        print("Unparseable or missing:", int(values.isna().sum()))
        print(values.describe().to_string())

# 7. Monthly payment summary by status.
# This is exploratory only; do not yet label any status as successful.
payments["event_month"] = pd.to_datetime(
    payments["event_at"], errors="coerce", utc=True
).dt.strftime("%Y-%m")

payments["amount_numeric"] = pd.to_numeric(
    payments["amount"], errors="coerce"
)

monthly = (
    payments.groupby(["event_month", "payment_status"], dropna=False)
    .agg(
        payment_rows=("payment_id", "size"),
        distinct_payment_ids=("payment_id", "nunique"),
        distinct_accounts=("account_id", "nunique"),
        amount_total=("amount_numeric", "sum"),
    )
    .reset_index()
    .sort_values(["event_month", "payment_status"])
)

monthly.to_csv(out_dir / "monthly_payments_by_status.csv", index=False)

print("\n--- Monthly payments by status (first 40 rows) ---")
print(monthly.head(40).to_string(index=False))

# Save account status history event counts for later temporal analysis.
history_summary = (
    status_history.groupby("status", dropna=False)
    .size()
    .reset_index(name="event_count")
    .sort_values("event_count", ascending=False)
)
history_summary.to_csv(
    out_dir / "account_status_history_status_counts.csv", index=False
)

print("\nReports saved in:", out_dir.resolve())
