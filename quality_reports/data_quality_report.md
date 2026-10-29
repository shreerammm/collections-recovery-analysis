# Data Quality Report — Collections Recovery Analysis

## 1. Payment Data

- Total staged payment rows: 25,014.
- Missing payment references: 382 (1.53%).
- Missing or invalid payment dates: 0.
- Invalid or non-positive payment amounts: 0.
- Payment IDs appearing more than once: 14 IDs, each appearing twice.

**Action:** Investigate repeated payment IDs and missing references before finalizing recovery totals.

## 2. Monthly Payment Trend

- Gross successful payment amount increased from 170.28 million in February 2026 to 189.19 million in March 2026, an increase of approximately 11.11%.
- The amount decreased to 175.23 million in April 2026.
- August 2026 contains data only through August 8 and is not comparable with a full month.

**Interpretation:** The March increase alone does not prove that the recovery rate improved by 11% month-on-month.

## 3. Campaign Date Alignment

Of 45,000 targeting rows:
- Before campaign start: 15,253 (33.90%).
- After campaign end: 20,886 (46.41%).
- Within campaign date window: 8,861 (19.69%).

**Action:** Investigate campaign dates, targeting timestamps, and campaign-to-targeting relationships.

## 4. Limitations

Gross successful payment amounts are not a recovery rate. A valid recovery-rate analysis requires an agreed numerator and denominator, consistent reporting dates, treatment of reversed payments, and reliable account and payment attribution.

## 5. Conclusion

The current analysis identifies payment-quality issues and substantial campaign-date misalignment. These issues should be investigated before the claim of an 11% month-on-month recovery improvement is accepted.