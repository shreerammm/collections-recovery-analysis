
from pathlib import Path
import pandas as pd

root = Path.cwd()
data_dir = root / "data_staging"
out_dir = root / "quality_reports"
out_dir.mkdir(exist_ok=True)

targets = pd.read_csv(data_dir / "daily_targeting.csv")
campaigns = pd.read_csv(data_dir / "campaigns.csv")

targets["target_date"] = pd.to_datetime(
    targets["target_date"], errors="coerce", utc=True
)
for col in ["start_at", "end_at"]:
    campaigns[col] = pd.to_datetime(
        campaigns[col], errors="coerce", utc=True
    )

df = targets.merge(
    campaigns[
        ["campaign_id", "campaign_name", "strategy_version",
         "start_at", "end_at", "channel"]
    ],
    on="campaign_id",
    how="left",
    validate="many_to_one"
)

# Compare calendar dates, matching the previous check.
target_day = df["target_date"].dt.normalize()
start_day = df["start_at"].dt.normalize()
end_day = df["end_at"].dt.normalize()

df["date_issue"] = "WITHIN_WINDOW"
df.loc[
    df["target_date"].isna()
    | df["start_at"].isna()
    | df["end_at"].isna(),
    "date_issue"
] = "MISSING_DATE"

df.loc[
    target_day < start_day,
    "date_issue"
] = "BEFORE_CAMPAIGN_START"

df.loc[
    target_day > end_day,
    "date_issue"
] = "AFTER_CAMPAIGN_END"

print("--- Date issue counts ---")
print(df["date_issue"].value_counts(dropna=False).to_string())

print("\n--- Date issue by strategy version ---")
print(pd.crosstab(
    df["strategy_version"],
    df["date_issue"]
).to_string())

print("\n--- Campaigns with most date issues ---")
by_campaign = df.groupby(
    ["campaign_id", "campaign_name", "strategy_version",
     "start_at", "end_at"],
    dropna=False
).agg(
    targeting_rows=("target_id", "size"),
    date_issues=("date_issue", lambda s: (s != "WITHIN_WINDOW").sum()),
    before_start=("date_issue", lambda s: (s == "BEFORE_CAMPAIGN_START").sum()),
    after_end=("date_issue", lambda s: (s == "AFTER_CAMPAIGN_END").sum())
).reset_index()

by_campaign["issue_pct"] = (
    100 * by_campaign["date_issues"] / by_campaign["targeting_rows"]
)
by_campaign = by_campaign.sort_values(
    ["date_issues", "targeting_rows"], ascending=False
)

print(by_campaign.head(20).to_string(index=False))
by_campaign.to_csv(out_dir / "campaign_date_issue_summary.csv", index=False)

print("\nSaved:", (out_dir / "campaign_date_issue_summary.csv").resolve())
