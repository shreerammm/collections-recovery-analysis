
from pathlib import Path
import pandas as pd

root = Path.cwd()
data_dir = root / "data_staging"
report_dir = root / "quality_reports"
report_dir.mkdir(exist_ok=True)

if not data_dir.exists():
    raise FileNotFoundError(
        "data_staging folder not found. Open the dataset folder in VS Code first."
    )

# Load the staged CSV files.
tables = {}
for file in data_dir.glob("*.csv"):
    tables[file.stem] = pd.read_csv(file, low_memory=False)

# 1. Missing values in every column.
missing_rows = []

for table_name, df in tables.items():
    for column in df.columns:
        missing_rows.append({
            "table": table_name,
            "column": column,
            "row_count": len(df),
            "missing_count": int(df[column].isna().sum()),
            "missing_percent": round(
                df[column].isna().mean() * 100, 2
            ),
        })

missing_report = pd.DataFrame(missing_rows)
missing_report.to_csv(
    report_dir / "missing_values.csv", index=False
)

# 2. Check whether important identifiers are unique.
key_columns = {
    "accounts": ["account_id"],
    "borrowers": ["borrower_id"],
    "agents": ["agent_id", "employee_code"],
    "calls": ["call_id"],
    "call_attempts": ["attempt_id"],
    "call_dispositions": ["disposition_id"],
    "payments": ["payment_id", "payment_reference"],
    "whatsapp_events": ["whatsapp_event_id"],
    "sms_events": ["sms_event_id"],
    "promises_to_pay": ["ptp_id"],
    "account_status_history": ["history_id"],
    "daily_targeting": ["target_id"],
    "field_visits": ["visit_id"],
    "agent_sessions": ["session_id"],
    "complaints": ["complaint_id"],
}

key_rows = []

for table_name, columns in key_columns.items():
    if table_name not in tables:
        continue

    df = tables[table_name]

    for column in columns:
        if column not in df.columns:
            continue

        key_rows.append({
            "table": table_name,
            "column": column,
            "total_rows": len(df),
            "missing_values": int(df[column].isna().sum()),
            "distinct_nonmissing_values": int(
                df[column].nunique()
            ),
            "rows_with_repeated_values": int(
                df[column].duplicated(keep=False).sum()
            ),
            "unique_nonmissing_values": bool(
                df[column].dropna().is_unique
            ),
        })

key_report = pd.DataFrame(key_rows)
key_report.to_csv(report_dir / "key_checks.csv", index=False)

# 3. Check whether IDs in child tables exist in parent tables.
relationship_specs = [
    ("accounts", "borrower_id", "borrowers", "borrower_id"),
    ("calls", "account_id", "accounts", "account_id"),
    ("calls", "borrower_id", "borrowers", "borrower_id"),
    ("payments", "account_id", "accounts", "account_id"),
    ("payments", "borrower_id", "borrowers", "borrower_id"),
    ("call_attempts", "account_id", "accounts", "account_id"),
    ("call_attempts", "borrower_id", "borrowers", "borrower_id"),
    ("call_dispositions", "account_id", "accounts", "account_id"),
    ("promises_to_pay", "account_id", "accounts", "account_id"),
    ("field_visits", "account_id", "accounts", "account_id"),
    ("daily_targeting", "account_id", "accounts", "account_id"),
]

relationship_rows = []

for child_table, child_col, parent_table, parent_col in relationship_specs:
    if child_table not in tables or parent_table not in tables:
        continue

    child = tables[child_table]
    parent = tables[parent_table]

    if child_col not in child.columns or parent_col not in parent.columns:
        continue

    parent_ids = set(parent[parent_col].dropna())
    child_ids = child[child_col]

    missing_id_count = int(child_ids.isna().sum())
    unknown_mask = child_ids.notna() & ~child_ids.isin(parent_ids)

    relationship_rows.append({
        "child_table": child_table,
        "child_column": child_col,
        "parent_table": parent_table,
        "parent_column": parent_col,
        "child_rows": len(child),
        "missing_child_ids": missing_id_count,
        "ids_not_found_in_parent": int(unknown_mask.sum()),
    })

relationship_report = pd.DataFrame(relationship_rows)
relationship_report.to_csv(
    report_dir / "relationship_checks.csv", index=False
)

print("Quality checks completed.")
print(f"Reports saved to: {report_dir.resolve()}")

print("\nLargest missing-value issues:")
print(
    missing_report[missing_report["missing_count"] > 0]
    .sort_values("missing_count", ascending=False)
    .head(15).to_string(index=False)
)

print("\nIdentifier checks needing investigation:")
print(
    key_report[
        (key_report["rows_with_repeated_values"] > 0)
        | (key_report["missing_values"] > 0)
    ].to_string(index=False)
)

print("\nRelationship checks with missing or unmatched IDs:")
print(
    relationship_report[
        (relationship_report["missing_child_ids"] > 0)
        | (relationship_report["ids_not_found_in_parent"] > 0)
    ].to_string(index=False)
)
