
from pathlib import Path
import pandas as pd

root = Path.cwd()
data_dir = root / "data_staging"
out_dir = root / "quality_reports"
out_dir.mkdir(exist_ok=True)

def load(name):
    return pd.read_csv(data_dir / f"{name}.csv", low_memory=False)

def profile_repeated_ids(df, id_col, attributes, label):
    """Summarize IDs that repeat and whether their attributes conflict."""
    available = [c for c in attributes if c in df.columns]

    grouped = df.groupby(id_col, dropna=False).agg(
        row_count=(id_col, "size"),
        **{
            f"{col}_distinct": (col, "nunique")
            for col in available
        }
    ).reset_index()

    grouped = grouped[grouped["row_count"] > 1].copy()

    conflict_cols = [f"{col}_distinct" for col in available]
    if conflict_cols:
        grouped["has_attribute_conflict"] = (
            grouped[conflict_cols].gt(1).any(axis=1)
        )
    else:
        grouped["has_attribute_conflict"] = False

    grouped.to_csv(out_dir / f"{label}_repeated_ids.csv", index=False)

    print(f"\n--- {label}: repeated ID summary ---")
    print(f"IDs appearing multiple times: {len(grouped):,}")
    print(
        "Repeated IDs with conflicting attributes: "
        f"{int(grouped['has_attribute_conflict'].sum()):,}"
    )
    print("Largest repeated-ID groups:")
    print(
        grouped.sort_values("row_count", ascending=False)
        .head(10).to_string(index=False)
    )

# A. Borrower IDs: do repeated IDs have conflicting details?
borrowers = load("borrowers")
profile_repeated_ids(
    borrowers,
    "borrower_id",
    ["name", "phone", "email", "city", "state", "created_at"],
    "borrowers"
)

# B. Agent IDs: do repeated IDs point to different employees or attributes?
agents = load("agents")
profile_repeated_ids(
    agents,
    "agent_id",
    ["employee_code", "agent_name", "vendor_id", "team",
     "status", "joined_at"],
    "agents"
)

# Also check whether employee codes map to multiple agent IDs.
employee_map = (
    agents.groupby("employee_code", dropna=False)
    .agg(
        row_count=("employee_code", "size"),
        distinct_agent_ids=("agent_id", "nunique"),
        distinct_names=("agent_name", "nunique"),
        distinct_vendors=("vendor_id", "nunique"),
    )
    .reset_index()
)
employee_map = employee_map[
    (employee_map["distinct_agent_ids"] > 1)
    | (employee_map["distinct_names"] > 1)
    | (employee_map["distinct_vendors"] > 1)
]
employee_map.to_csv(out_dir / "employee_code_conflicts.csv", index=False)

print("\n--- Employee code conflicts ---")
print(f"Conflicting employee codes: {len(employee_map):,}")
print(employee_map.head(10).to_string(index=False))

# C. Check distinct unmatched borrower IDs in key tables.
borrower_ids = set(borrowers["borrower_id"].dropna())

relationship_tables = [
    "accounts", "calls", "call_attempts", "payments",
    "call_dispositions", "promises_to_pay", "field_visits",
    "complaints", "sms_events", "whatsapp_events",
    "account_status_history"
]

unmatched_summary = []

for table_name in relationship_tables:
    path = data_dir / f"{table_name}.csv"
    if not path.exists():
        continue

    df = pd.read_csv(path, low_memory=False)
    if "borrower_id" not in df.columns:
        continue

    ids = df["borrower_id"]
    unmatched_mask = ids.notna() & ~ids.isin(borrower_ids)
    unmatched_ids = ids[unmatched_mask].nunique()

    unmatched_summary.append({
        "table": table_name,
        "rows": len(df),
        "missing_borrower_id_rows": int(ids.isna().sum()),
        "rows_with_unmatched_borrower_id": int(unmatched_mask.sum()),
        "distinct_unmatched_borrower_ids": int(unmatched_ids),
    })

    # Save a small sample of unmatched IDs for investigation.
    sample = (
        df.loc[unmatched_mask, ["borrower_id"]]
        .drop_duplicates()
        .head(20)
    )
    sample.to_csv(
        out_dir / f"{table_name}_unmatched_borrower_sample.csv",
        index=False
    )

unmatched_df = pd.DataFrame(unmatched_summary)
unmatched_df.to_csv(
    out_dir / "unmatched_borrower_summary.csv", index=False
)

print("\n--- Unmatched borrower IDs ---")
print(unmatched_df.to_string(index=False))

print(f"\nDetailed reports saved in: {out_dir.resolve()}")
