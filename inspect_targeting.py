
from pathlib import Path
import pandas as pd

root = Path.cwd()
data_dir = root / "data_staging"
out_dir = root / "quality_reports"
out_dir.mkdir(exist_ok=True)

targeting = pd.read_csv(
    data_dir / "daily_targeting.csv", low_memory=False
)
campaigns = pd.read_csv(
    data_dir / "campaigns.csv", low_memory=False
)

# Parse dates.
targeting["target_date"] = pd.to_datetime(
    targeting["target_date"], errors="coerce", utc=True
)
targeting["target_month"] = targeting["target_date"].dt.strftime("%Y-%m")

for col in ["start_at", "end_at"]:
    campaigns[col] = pd.to_datetime(
        campaigns[col], errors="coerce", utc=True
    )

print("--- Targeting date coverage ---")
print("Rows:", len(targeting))
print("Distinct target IDs:", targeting["target_id"].nunique())
print("Distinct accounts targeted:", targeting["account_id"].nunique())
print("Distinct campaigns used:", targeting["campaign_id"].nunique())
print("Missing target dates:", int(targeting["target_date"].isna().sum()))
print("Earliest target date:", targeting["target_date"].min())
print("Latest target date:", targeting["target_date"].max())

print("\n--- Targeting status counts ---")
print(targeting["status"].fillna("<MISSING>").value_counts().to_string())

print("\n--- Targeting priority counts ---")
print(targeting["priority"].fillna("<MISSING>").value_counts().to_string())

print("\n--- Recommended channel counts ---")
print(
    targeting["recommended_channel"]
    .fillna("<MISSING>").value_counts().to_string()
)

# Monthly activity: rows and distinct targeted accounts.
monthly_targeting = (
    targeting.groupby("target_month", dropna=False)
    .agg(
        targeting_rows=("target_id", "size"),
        distinct_targeted_accounts=("account_id", "nunique"),
        distinct_campaigns=("campaign_id", "nunique"),
    )
    .reset_index()
    .sort_values("target_month")
)
monthly_targeting.to_csv(
    out_dir / "monthly_targeting_summary.csv", index=False
)

print("\n--- Monthly targeting summary ---")
print(monthly_targeting.to_string(index=False))

# Strategy and targeting definitions.
print("\n--- Campaign strategy definitions ---")
print("Campaign rows:", len(campaigns))
print("Distinct campaign IDs:", campaigns["campaign_id"].nunique())
print(
    campaigns[
        ["campaign_id", "campaign_name", "channel", "strategy_version",
         "start_at", "target_definition", "end_at"]
    ].head(30).to_string(index=False)
)

campaigns.to_csv(out_dir / "campaigns_for_review.csv", index=False)

# Find campaign IDs used in targeting but absent from the campaign table.
known_campaigns = set(campaigns["campaign_id"].dropna())
unknown_mask = (
    targeting["campaign_id"].notna()
    & ~targeting["campaign_id"].isin(known_campaigns)
)

print("\n--- Campaign linkage ---")
print("Target rows with missing campaign ID:",
      int(targeting["campaign_id"].isna().sum()))
print("Target rows with unknown campaign ID:",
      int(unknown_mask.sum()))

# Check whether the same account is targeted multiple times on the same day.
repeat_target = targeting.duplicated(
    subset=["account_id", "target_date"], keep=False
)
print("\n--- Repeated account/day targeting ---")
print("Rows sharing account and target date:", int(repeat_target.sum()))
print("Distinct accounts with repeated target dates:",
      targeting.loc[repeat_target, "account_id"].nunique())

targeting.loc[repeat_target].sort_values(
    ["account_id", "target_date"]
).to_csv(out_dir / "repeated_account_day_targets.csv", index=False)

print("\nReports saved to:", out_dir.resolve())
