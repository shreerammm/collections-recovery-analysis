
from pathlib import Path
import pandas as pd

root = Path.cwd()
data_dir = root / "data_staging"
out_dir = root / "quality_reports"
out_dir.mkdir(exist_ok=True)

targets = pd.read_csv(data_dir / "daily_targeting.csv", low_memory=False)
campaigns = pd.read_csv(data_dir / "campaigns.csv", low_memory=False)

targets["target_date"] = pd.to_datetime(
    targets["target_date"], errors="coerce", utc=True
)
campaigns["start_at"] = pd.to_datetime(
    campaigns["start_at"], errors="coerce", utc=True
)
campaigns["end_at"] = pd.to_datetime(
    campaigns["end_at"], errors="coerce", utc=True
)

# Join campaign metadata to each targeting record.
df = targets.merge(
    campaigns[
        ["campaign_id", "channel", "strategy_version",
         "start_at", "end_at", "target_definition"]
    ],
    on="campaign_id",
    how="left",
    validate="many_to_one",
    indicator=True
)

# Compare calendar dates, avoiding false mismatches from time-of-day.
target_day = df["target_date"].dt.normalize()
start_day = df["start_at"].dt.normalize()
end_day = df["end_at"].dt.normalize()

df["outside_campaign_dates"] = (
    df["start_at"].isna()
    | df["end_at"].isna()
    | (target_day < start_day)
    | (target_day > end_day)
)

# MIXED is treated as a possible multi-channel campaign, not an automatic mismatch.
df["channel_mismatch"] = (
    df["channel"].notna()
    & df["recommended_channel"].notna()
    & (df["channel"] != "MIXED")
    & (df["channel"] != df["recommended_channel"])
)

print("--- Campaign date alignment ---")
print("Target rows:", len(df))
print("Rows outside campaign dates:", int(df["outside_campaign_dates"].sum()))
print("Rows with missing campaign metadata:", int((df["_merge"] != "both").sum()))

print("\n--- Channel alignment ---")
print("Rows with channel mismatch:", int(df["channel_mismatch"].sum()))
print("\nCampaign vs recommended channel:")
print(pd.crosstab(
    df["channel"].fillna("<MISSING>"),
    df["recommended_channel"].fillna("<MISSING>")
).to_string())

print("\n--- Out-of-date targeting examples ---")
print(df.loc[
    df["outside_campaign_dates"],
    ["target_id", "account_id", "campaign_id", "target_date",
     "start_at", "end_at", "channel", "recommended_channel"]
].head(20).to_string(index=False))

print("\n--- Mismatch counts by strategy version ---")
print(df.groupby("strategy_version", dropna=False).agg(
    targeting_rows=("target_id", "size"),
    outside_campaign_dates=("outside_campaign_dates", "sum"),
    channel_mismatches=("channel_mismatch", "sum")
).to_string())

df.to_csv(out_dir / "targeting_campaign_alignment.csv", index=False)
print("\nSaved:", (out_dir / "targeting_campaign_alignment.csv").resolve())
