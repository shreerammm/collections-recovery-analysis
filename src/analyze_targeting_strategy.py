
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data_staging"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

# Load data
targeting = pd.read_csv(DATA / "daily_targeting.csv")
campaigns = pd.read_csv(DATA / "campaigns.csv")
payments = pd.read_csv(DATA / "payments.csv")
accounts = pd.read_csv(DATA / "accounts.csv")

# Standardise column names
for df in [targeting, campaigns, payments, accounts]:
    df.columns = df.columns.str.strip().str.lower()

# Parse dates and amounts
targeting["target_date"] = pd.to_datetime(
    targeting["target_date"], errors="coerce", utc=True
)
campaigns["start_at"] = pd.to_datetime(
    campaigns["start_at"], errors="coerce", utc=True
)
campaigns["end_at"] = pd.to_datetime(
    campaigns["end_at"], errors="coerce", utc=True
)

# Check the raw campaign date boundaries before classifying records
print("\nCAMPAIGN DATE RANGE CHECK")
print("Campaign start:", campaigns["start_at"].min())
print("Campaign end:", campaigns["end_at"].max())
print("Targeting date:", targeting["target_date"].min(),
      "to", targeting["target_date"].max())
payments["event_at"] = pd.to_datetime(
    payments["event_at"], errors="coerce", utc=True
)
payments["amount"] = pd.to_numeric(
    payments["amount"], errors="coerce"
)
payments["payment_status"] = (
    payments["payment_status"].astype("string").str.strip().str.upper()
)

# 1. Examine campaign date alignment

# 1. Examine campaign date alignment at calendar-date level
aligned = targeting.merge(
    campaigns[
        ["campaign_id", "start_at", "end_at", "channel", "strategy_version"]
    ],
    on="campaign_id",
    how="left",
    validate="many_to_one",
)

# Compare dates rather than timestamps because target_date is a daily date.
aligned["target_day"] = aligned["target_date"].dt.strftime("%Y-%m-%d")
aligned["campaign_start_day"] = aligned["start_at"].dt.strftime("%Y-%m-%d")
aligned["campaign_end_day"] = aligned["end_at"].dt.strftime("%Y-%m-%d")

aligned["date_alignment"] = "UNKNOWN_CAMPAIGN_OR_DATE"

valid = (
    aligned["target_day"].notna()
    & aligned["campaign_start_day"].notna()
    & aligned["campaign_end_day"].notna()
)

aligned.loc[
    valid & (aligned["target_day"] < aligned["campaign_start_day"]),
    "date_alignment",
] = "BEFORE_START"

aligned.loc[
    valid & (aligned["target_day"] > aligned["campaign_end_day"]),
    "date_alignment",
] = "AFTER_END"

aligned.loc[
    valid
    & (aligned["target_day"] >= aligned["campaign_start_day"])
    & (aligned["target_day"] <= aligned["campaign_end_day"]),
    "date_alignment",
] = "WITHIN_WINDOW"

date_summary = (
    aligned.groupby("date_alignment", dropna=False)
    .size()
    .rename("targeting_rows")
    .reset_index()
)
date_summary["percentage"] = (
    date_summary["targeting_rows"] / len(aligned) * 100
)
date_summary.to_csv(REPORTS / "targeting_date_alignment.csv", index=False)


# 2. Summarise targeting by recommended channel
channel_col = "recommended_channel"
if channel_col in aligned.columns:
    channel_summary = (
        aligned.groupby(channel_col, dropna=False)
        .agg(
            targeting_rows=("target_id", "size"),
            unique_accounts=("account_id", "nunique"),
        )
        .reset_index()
    )
    channel_summary.to_csv(
        REPORTS / "targeting_channel_summary.csv", index=False
    )

# 3. Build a transparent payment outcome summary by account
# Use successful payments only; this is gross payment amount,
# not a causal estimate of campaign impact.
success = payments[payments["payment_status"] == "SUCCESS"].copy()

payment_by_account = (
    success.groupby("account_id")
    .agg(
        successful_payment_rows=("payment_id", "size"),
        gross_success_amount=("amount", "sum"),
        latest_success_payment=("event_at", "max"),
    )
    .reset_index()
)

# Join outcomes to targeting at account level for exploratory analysis
target_outcomes = aligned.merge(
    payment_by_account,
    on="account_id",
    how="left",
    validate="many_to_one",
)

target_outcomes["successful_payment_rows"] = (
    target_outcomes["successful_payment_rows"].fillna(0)
)
target_outcomes["gross_success_amount"] = (
    target_outcomes["gross_success_amount"].fillna(0)
)

# Account-level aggregation prevents accounts with repeated targeting
# from being counted as separate independent accounts.
account_outcomes = (
    target_outcomes.groupby("account_id")
    .agg(
        targeting_rows=("target_id", "size"),
        campaigns=("campaign_id", "nunique"),
        gross_success_amount=("gross_success_amount", "max"),
        latest_success_payment=("latest_success_payment", "max"),
    )
    .reset_index()
)

account_outcomes.to_csv(
    REPORTS / "targeting_account_outcomes_exploratory.csv", index=False
)

print("\nCAMPAIGN DATE ALIGNMENT")
print(date_summary.round(2).to_string(index=False))

if channel_col in aligned.columns:
    print("\nTARGETING BY RECOMMENDED CHANNEL")
    print(channel_summary.to_string(index=False))

print("\nACCOUNT-LEVEL EXPLORATORY OUTCOMES")
print(f"Accounts targeted: {account_outcomes['account_id'].nunique():,}")
print(
    "Accounts with any linked successful payment: "
    f"{int((account_outcomes['gross_success_amount'] > 0).sum()):,}"
)
print(
    "Total gross successful-payment amount linked to targeted accounts: "
    f"{account_outcomes['gross_success_amount'].sum():,.2f}"
)

print("\nCaution: these are exploratory associations, not causal campaign effects.")
print("A payment may have occurred before or after targeting.")
print("Use a time-bounded treatment/control experiment for causal evaluation.")
print(f"\nSaved reports to: {REPORTS}")
