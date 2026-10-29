
from pathlib import Path
import pandas as pd

root = Path.cwd()
data_dir = root / "data_staging"
out_dir = root / "quality_reports"
out_dir.mkdir(exist_ok=True)

payments = pd.read_csv(data_dir / "payments.csv", low_memory=False)

payments["event_at"] = pd.to_datetime(
    payments["event_at"], errors="coerce", utc=True
)
payments["amount"] = pd.to_numeric(
    payments["amount"], errors="coerce"
)
payments["event_month"] = payments["event_at"].dt.strftime("%Y-%m")

# A. Investigate repeated payment IDs before treating each row as a transaction.
repeated_mask = payments["payment_id"].duplicated(keep=False)
repeated_payments = payments.loc[repeated_mask].sort_values(
    ["payment_id", "event_at"]
)
repeated_payments.to_csv(
    out_dir / "repeated_payment_id_details.csv", index=False
)

print("--- Repeated payment IDs ---")
print("Rows with a repeated payment ID:", int(repeated_mask.sum()))
print(
    "Distinct repeated payment IDs:",
    repeated_payments["payment_id"].nunique()
)

if not repeated_payments.empty:
    id_audit = (
        repeated_payments.groupby("payment_id", dropna=False)
        .agg(
            row_count=("payment_id", "size"),
            distinct_dates=("event_at", "nunique"),
            distinct_statuses=("payment_status", "nunique"),
            distinct_amounts=("amount", "nunique"),
            distinct_accounts=("account_id", "nunique"),
            statuses=("payment_status", lambda s: "|".join(
                sorted(s.dropna().astype(str).unique())
            )),
        )
        .reset_index()
    )
    id_audit.to_csv(
        out_dir / "repeated_payment_id_summary.csv", index=False
    )
    print("\nRepeated IDs with different statuses, amounts, or accounts:")
    print(
        id_audit[
            (id_audit["distinct_statuses"] > 1)
            | (id_audit["distinct_amounts"] > 1)
            | (id_audit["distinct_accounts"] > 1)
        ].head(20).to_string(index=False)
    )

# B. Monthly summary by status: retain all statuses for transparency.
monthly_status = (
    payments.groupby(["event_month", "payment_status"], dropna=False)
    .agg(
        payment_rows=("payment_id", "size"),
        distinct_payment_ids=("payment_id", "nunique"),
        distinct_accounts=("account_id", "nunique"),
        amount_total=("amount", "sum"),
    )
    .reset_index()
    .sort_values(["event_month", "payment_status"])
)
monthly_status.to_csv(
    out_dir / "monthly_payment_status_baseline.csv", index=False
)

# C. Focus on SUCCESS records, with raw and distinct-ID measures side by side.
success = payments[
    payments["payment_status"].astype(str).str.upper().eq("SUCCESS")
].copy()

monthly_success = (
    success.groupby("event_month")
    .agg(
        successful_rows=("payment_id", "size"),
        distinct_payment_ids=("payment_id", "nunique"),
        distinct_accounts=("account_id", "nunique"),
        successful_amount_sum=("amount", "sum"),
        average_successful_row_amount=("amount", "mean"),
    )
    .reset_index()
    .sort_values("event_month")
)

monthly_success["amount_change_percent"] = (
    monthly_success["successful_amount_sum"].pct_change() * 100
)
monthly_success["distinct_payment_id_change_percent"] = (
    monthly_success["distinct_payment_ids"].pct_change() * 100
)
monthly_success["distinct_account_change_percent"] = (
    monthly_success["distinct_accounts"].pct_change() * 100
)

monthly_success.to_csv(
    out_dir / "monthly_successful_payment_baseline.csv", index=False
)

print("\n--- Monthly SUCCESS baseline ---")
print(monthly_success.round(2).to_string(index=False))

print("\n--- Coverage warning ---")
print("First payment date:", payments["event_at"].min())
print("Last payment date:", payments["event_at"].max())
print(
    "August is partial:",
    bool((payments["event_at"].dt.month == 8).any())
)

print("\nReports saved to:", out_dir.resolve())
