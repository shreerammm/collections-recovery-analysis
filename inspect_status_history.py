
from pathlib import Path
import pandas as pd

root = Path.cwd()
data_dir = root / "data_staging"
out_dir = root / "quality_reports"
out_dir.mkdir(exist_ok=True)

history = pd.read_csv(
    data_dir / "account_status_history.csv",
    low_memory=False
)
accounts = pd.read_csv(
    data_dir / "accounts.csv",
    low_memory=False
)

history["event_at"] = pd.to_datetime(
    history["event_at"], errors="coerce", utc=True
)
history["recorded_at"] = pd.to_datetime(
    history["recorded_at"], errors="coerce", utc=True
)
history["event_month"] = history["event_at"].dt.strftime("%Y-%m")

# 1. All recorded status values.
print("--- History status counts ---")
print(
    history["status"].fillna("<MISSING>")
    .value_counts(dropna=False).to_string()
)

# 2. Monthly activity by status.
monthly = (
    history.groupby(["event_month", "status"], dropna=False)
    .agg(
        history_rows=("history_id", "size"),
        distinct_accounts=("account_id", "nunique"),
        distinct_borrowers=("borrower_id", "nunique"),
        distinct_agents=("changed_by", "nunique"),
        distinct_sources=("source", "nunique"),
    )
    .reset_index()
    .sort_values(["event_month", "status"])
)
monthly.to_csv(out_dir / "monthly_status_history.csv", index=False)

print("\n--- Monthly status history ---")
print(monthly.to_string(index=False))

# 3. Check for repeated history IDs and multiple events at the same
# timestamp for the same account.
print("\n--- History key checks ---")
print("History rows:", len(history))
print("Distinct history IDs:", history["history_id"].nunique())
print("Distinct account IDs:", history["account_id"].nunique())
print("Missing account IDs:", int(history["account_id"].isna().sum()))

same_time = history.duplicated(
    subset=["account_id", "event_at"], keep=False
)
print(
    "Rows sharing account_id and event_at:",
    int(same_time.sum())
)

# 4. Show the most recent history events for a small sample of accounts.
ordered = history.sort_values(["account_id", "event_at"])
sample_ids = ordered["account_id"].dropna().drop_duplicates().head(10)
sample = ordered[ordered["account_id"].isin(sample_ids)]

sample.to_csv(out_dir / "sample_account_status_timelines.csv", index=False)

print("\n--- Sample status timelines (first 40 rows) ---")
print(
    sample[
        ["account_id", "event_at", "status", "changed_by",
         "source", "recorded_at"]
    ].head(40).to_string(index=False)
)

# 5. Compare latest history status with the current account status.
latest = (
    ordered.dropna(subset=["account_id"])
    .drop_duplicates(subset=["account_id"], keep="last")
    [["account_id", "status", "event_at"]]
    .rename(columns={
        "status": "latest_history_status",
        "event_at": "latest_history_event_at"
    })
)

comparison = accounts[["account_id", "status"]].merge(
    latest, on="account_id", how="left"
)
comparison["status_matches"] = (
    comparison["status"] == comparison["latest_history_status"]
)
comparison.to_csv(
    out_dir / "current_vs_latest_history_status.csv", index=False
)

print("\n--- Current status vs. latest history ---")
print("Accounts:", len(comparison))
print("Accounts without history match:", int(
    comparison["latest_history_status"].isna().sum()
))
print("Status matches:", int(comparison["status_matches"].sum()))
print("Status mismatches:", int(
    (~comparison["status_matches"]).sum()
    - comparison["latest_history_status"].isna().sum()
))

print("\nReports saved to:", out_dir.resolve())
