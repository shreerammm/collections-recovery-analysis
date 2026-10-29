
from pathlib import Path
import pandas as pd

folder = Path.cwd()

checks = {
    "borrowers.csv": "borrower_id",
    "agents.csv": "agent_id",
    "calls.csv": "call_id",
    "payments.csv": "payment_id",
    "whatsapp_events.csv": "whatsapp_event_id",
}

for filename, key in checks.items():
    path = folder / filename
    df = pd.read_csv(path, low_memory=False)

    print(f"\n{'=' * 60}")
    print(f"FILE: {filename}")
    print(f"Total rows: {len(df):,}")

    counts = df[key].value_counts(dropna=True)
    repeated = counts[counts > 1]

    print(f"Distinct nonmissing IDs: {df[key].nunique():,}")
    print(f"IDs appearing more than once: {len(repeated):,}")
    print(f"Rows with repeated IDs: {int(repeated.sum()):,}")
    print(f"Excess rows beyond first occurrence: "
          f"{int((repeated - 1).sum()):,}")

    duplicate_rows = df[df[key].isin(repeated.index)]
    if not duplicate_rows.empty:
        # Count IDs whose records differ in at least one other column.
        comparison_cols = [c for c in df.columns if c != key]
        differing_groups = 0

        for _, group in duplicate_rows.groupby(key):
            if len(group[comparison_cols].drop_duplicates()) > 1:
                differing_groups += 1

        print(f"Repeated-ID groups with differing records: "
              f"{differing_groups:,}")

print("\nAudit complete. No source data was modified.")
