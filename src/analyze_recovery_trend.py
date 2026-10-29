
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "quality_reports" / "query_2_results.csv"
OUTPUT = ROOT / "reports" / "recovery_monthly_changes.csv"

# Load monthly successful-payment results
df = pd.read_csv(INPUT)
df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
df = df.sort_values("month")

# August is partial, so exclude it from full-month comparisons
full_months = df[df["month"] < pd.Timestamp("2026-08-01")].copy()

# Calculate month-on-month changes
full_months["amount_change"] = (
    full_months["gross_success_amount"].diff()
)
full_months["amount_change_pct"] = (
    full_months["gross_success_amount"].pct_change() * 100
)
full_months["payment_id_change_pct"] = (
    full_months["distinct_payment_ids"].pct_change() * 100
)
full_months["account_change_pct"] = (
    full_months["distinct_accounts"].pct_change() * 100
)

# Save results
full_months["month"] = full_months["month"].dt.strftime("%Y-%m")
full_months.to_csv(OUTPUT, index=False)

print("\nMONTH-ON-MONTH ANALYSIS")
print(
    full_months[
        [
            "month",
            "gross_success_amount",
            "amount_change_pct",
            "payment_id_change_pct",
            "account_change_pct",
        ]
    ].round(2).to_string(index=False)
)

print("\nINTERPRETATION")
march = full_months.loc[full_months["month"] == "2026-03"]

if not march.empty:
    print(
        "March gross successful payment amount change vs February: "
        f'{march["amount_change_pct"].iloc[0]:.2f}%'
    )

positive_months = (
    full_months["amount_change_pct"].dropna() > 0
).sum()
comparisons = full_months["amount_change_pct"].notna().sum()

print(
    f"Positive month-on-month changes: {positive_months} "
    f"out of {comparisons} full-month comparisons."
)
print(
    "\nNote: These are gross successful-payment amounts, not a recovery rate. "
    "They do not account for eligible outstanding balance or net reversals."
)
print(f"\nSaved results to: {OUTPUT}")
