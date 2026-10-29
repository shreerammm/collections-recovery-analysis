
from pathlib import Path
import pandas as pd

folder = Path.cwd()

# Candidate primary keys to inspect
checks = {
    "borrowers.csv": ["borrower_id"],
    "accounts.csv": ["account_id", "borrower_id"],
    "agents.csv": ["agent_id", "employee_code"],
    "calls.csv": ["call_id", "account_id"],
    "call_attempts.csv": ["attempt_id", "call_id"],
    "call_dispositions.csv": ["disposition_id", "call_id"],
    "payments.csv": ["payment_id", "payment_reference"],
    "whatsapp_events.csv": ["whatsapp_event_id", "message_id"],
    "sms_events.csv": ["sms_event_id", "message_id"],
    "promises_to_pay.csv": ["ptp_id", "account_id"],
    "account_status_history.csv": ["history_id"],
    "daily_targeting.csv": ["target_id"],
    "field_visits.csv": ["visit_id"],
    "agent_sessions.csv": ["session_id"],
    "complaints.csv": ["complaint_id"],
}

for filename, columns in checks.items():
    path = folder / filename

    if not path.exists():
        print(f"\nMISSING FILE: {filename}")
        continue

    df = pd.read_csv(path, low_memory=False)
    print(f"\n{'=' * 60}\n{filename} — {len(df):,} rows")

    for col in columns:
        if col not in df.columns:
            continue

        nonmissing = df[col].dropna()
        duplicated = nonmissing.duplicated(keep=False)

        print(
            f"{col}: missing={df[col].isna().sum():,}, "
            f"repeated nonmissing values={duplicated.sum():,}"
        )

        if duplicated.any():
            examples = nonmissing[duplicated].unique()[:5]
            print(f"  Example repeated values: {list(examples)}")

# Check account-to-borrower relationships
print(f"\n{'=' * 60}\nACCOUNT / BORROWER LINK CHECK")

accounts = pd.read_csv(folder / "accounts.csv", low_memory=False)
borrowers = pd.read_csv(folder / "borrowers.csv", low_memory=False)

known_borrowers = set(borrowers["borrower_id"].dropna())
account_borrowers = accounts["borrower_id"]

missing_links = account_borrowers.isna().sum()
unknown_links = (
    account_borrowers.notna()
    & ~account_borrowers.isin(known_borrowers)
).sum()

print(f"Accounts with missing borrower ID: {missing_links:,}")
print(f"Accounts linked to unknown borrower IDs: {unknown_links:,}")

print("\nInspection complete. No files were modified.")
