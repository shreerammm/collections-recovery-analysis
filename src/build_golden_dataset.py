
from pathlib import Path
import pandas as pd

# Project locations
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data_staging"
OUTPUT = ROOT / "reports"

OUTPUT.mkdir(exist_ok=True)

# Load staged data
payments = pd.read_csv(DATA / "payments.csv")
accounts = pd.read_csv(DATA / "accounts.csv")

# Standardise column names
payments.columns = payments.columns.str.strip().str.lower()
accounts.columns = accounts.columns.str.strip().str.lower()

# Flag repeated payment IDs; don't delete them automatically
payments["payment_id_duplicate"] = payments.duplicated(
    subset=["payment_id"], keep=False
)

# Convert dates and amounts safely
payments["event_at"] = pd.to_datetime(
    payments["event_at"], errors="coerce", utc=True
)
payments["amount"] = pd.to_numeric(
    payments["amount"], errors="coerce"
)

# Keep all payment statuses for transparent analysis
payments["payment_status"] = (
    payments["payment_status"].astype("string").str.strip().str.upper()
)

# Select useful account columns to avoid duplicate column names
account_columns = [
    column for column in [
        "account_id",
        "borrower_id",
        "loan_type",
        "risk_segment",
        "account_status",
        "dpd",
        "outstanding_balance",
        "principal_amount",
        "timezone",
        "opened_at",
    ]
    if column in accounts.columns
]

account_lookup = accounts[account_columns].copy()

# Join payments to accounts; retain unmatched payments for review
golden = payments.merge(
    account_lookup,
    on="account_id",
    how="left",
    validate="many_to_one",
    indicator=True,
)

golden["account_match_status"] = golden["_merge"].map({
    "both": "MATCHED",
    "left_only": "UNMATCHED_ACCOUNT",
})

golden = golden.drop(columns=["_merge"])

# Flag missing key fields
golden["missing_payment_reference"] = (
    golden["payment_reference"].isna()
    | golden["payment_reference"].astype("string").str.strip().eq("")
)

golden["invalid_amount"] = (
    golden["amount"].isna() | (golden["amount"] <= 0)
)

# Save dataset
output_file = OUTPUT / "golden_payments_dataset.csv"
golden.to_csv(output_file, index=False)

# Save a small quality summary
summary = pd.DataFrame({
    "metric": [
        "payment_rows",
        "repeated_payment_id_rows",
        "missing_payment_references",
        "invalid_amount_rows",
        "unmatched_account_rows",
    ],
    "value": [
        len(golden),
        int(golden["payment_id_duplicate"].sum()),
        int(golden["missing_payment_reference"].sum()),
        int(golden["invalid_amount"].sum()),
        int((golden["account_match_status"] == "UNMATCHED_ACCOUNT").sum()),
    ],
})

summary.to_csv(OUTPUT / "golden_dataset_quality_summary.csv", index=False)

print("Golden dataset created successfully.")
print(f"Dataset: {output_file}")
print(f"Rows: {len(golden):,}")
print("\nQuality summary:")
print(summary.to_string(index=False))
