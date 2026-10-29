
from pathlib import Path

import pandas as pd
import streamlit as st

# Project folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUALITY_DIR = PROJECT_ROOT / "quality_reports"
REPORTS_DIR = PROJECT_ROOT / "reports"

st.set_page_config(
    page_title="Collections Recovery Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Collections Recovery Analysis")
st.caption("Payment trends, data quality, and campaign alignment")

# Load SQL outputs
try:
    monthly = pd.read_csv(QUALITY_DIR / "query_2_results.csv")
    payment_quality = pd.read_csv(QUALITY_DIR / "query_3_results.csv")
    campaign_quality = pd.read_csv(QUALITY_DIR / "query_5_results.csv")
    status = pd.read_csv(QUALITY_DIR / "query_1_results.csv")
except FileNotFoundError as error:
    st.error(f"Missing results file: {error}")
    st.info("Run `python src/run_sql.py` from your project root first.")
    st.stop()

# Key metrics
quality = payment_quality.iloc[0]
campaign = campaign_quality.iloc[0]

feb = monthly.loc[monthly["month"] == "2026-02", "gross_success_amount"]
mar = monthly.loc[monthly["month"] == "2026-03", "gross_success_amount"]

if not feb.empty and not mar.empty and feb.iloc[0] != 0:
    march_change = (mar.iloc[0] / feb.iloc[0] - 1) * 100
else:
    march_change = None

outside_campaign = (
    campaign["before_campaign_start"] + campaign["after_campaign_end"]
)
outside_pct = outside_campaign / campaign["targeting_rows"] * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Staged payment rows",
    f'{int(quality["total_rows"]):,}'
)
col2.metric(
    "Missing payment references",
    f'{int(quality["missing_payment_references"]):,}'
)
col3.metric(
    "March vs February gross amount",
    f"{march_change:.2f}%" if march_change is not None else "N/A"
)
col4.metric(
    "Targeting outside campaign dates",
    f"{outside_pct:.2f}%"
)

st.warning(
    "Important: gross successful payment amount is not a recovery rate. "
    "The March increase alone does not prove sustained recovery improvement."
)

# Monthly trend
st.subheader("1. Monthly Gross Successful Payment Amount")

monthly["month"] = pd.to_datetime(monthly["month"])
monthly = monthly.sort_values("month").set_index("month")

st.line_chart(monthly["gross_success_amount"] / 1_000_000)
st.caption(
    "Amounts shown in millions. August 2026 contains only data through August 8."
)

# Payment status
st.subheader("2. Payment Status Distribution")

st.bar_chart(
    status.set_index("payment_status")["payment_rows"]
)

st.dataframe(status, use_container_width=True, hide_index=True)

# Payment quality
st.subheader("3. Payment Data Quality")

q1, q2, q3 = st.columns(3)
q1.metric(
    "Missing references",
    f'{int(quality["missing_payment_references"]):,}'
)
q2.metric(
    "Invalid/missing event dates",
    f'{int(quality["missing_or_invalid_event_dates"]):,}'
)
q3.metric(
    "Invalid/non-positive amounts",
    f'{int(quality["invalid_or_nonpositive_amounts"]):,}'
)

st.write("Repeated payment IDs")
duplicate_file = QUALITY_DIR / "query_4_results.csv"

if duplicate_file.exists():
    duplicates = pd.read_csv(duplicate_file)
    st.dataframe(duplicates, use_container_width=True, hide_index=True)
else:
    st.info("Run the SQL analysis to generate the duplicate-payment report.")

# Campaign alignment
st.subheader("4. Campaign Date Alignment")

campaign_view = pd.DataFrame({
    "Category": [
        "Before campaign start",
        "Within campaign window",
        "After campaign end",
    ],
    "Rows": [
        int(campaign["before_campaign_start"]),
        int(campaign["within_campaign_window"]),
        int(campaign["after_campaign_end"]),
    ],
})

st.bar_chart(campaign_view.set_index("Category"))
st.dataframe(campaign_view, use_container_width=True, hide_index=True)

st.caption(
    "Out-of-window records are investigation flags; validate campaign dates "
    "and timestamp rules before treating them as confirmed errors."
)

st.subheader("5. Monthly Data Table")
display_monthly = monthly.reset_index()
display_monthly["month"] = display_monthly["month"].dt.strftime("%Y-%m")
st.dataframe(display_monthly, use_container_width=True, hide_index=True)

st.caption("Source: project staging data and SQL query outputs.")
