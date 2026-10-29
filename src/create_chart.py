
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

data_file = project_root / "quality_reports" / "query_2_results.csv"
output_file = project_root / "reports" / "monthly_payment_trend.png"

df = pd.read_csv(data_file)

df["month"] = pd.to_datetime(df["month"])

plt.figure(figsize=(10, 5))
plt.plot(
    df["month"],
    df["gross_success_amount"] / 1_000_000,
    marker="o"
)

plt.title("Monthly Gross Successful Payment Amount")
plt.xlabel("Month")
plt.ylabel("Gross successful payments (millions)")
plt.xticks(df["month"], df["month"].dt.strftime("%b %Y"), rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(output_file, dpi=150)
plt.show()

print(f"Chart saved to: {output_file}")
