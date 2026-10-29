# Counterfactual Targeting Strategy

## 1. Objective

Design a targeting approach that can be tested to determine whether improved collections targeting increases net recovery, rather than merely increasing contact attempts or gross payment amounts.

## 2. Findings from the Current Data

- The analysis includes 45,000 targeting records across 23,344 distinct accounts.
- 80.74% of targeting records are classified as outside the associated campaign date window in the latest Python analysis.
- 10,288 targeted accounts have at least one linked successful payment. This is an exploratory association, not proof that targeting caused the payment.
- Targeting volumes are similar across FIELD, SMS, VOICE, and WHATSAPP.
- The current analysis does not establish which channel produces the best recovery outcome.

## 3. Recommended Targeting Approach

### Step A: Validate eligibility
Before assigning accounts to campaigns:
- Resolve account and borrower identity conflicts.
- Validate campaign start and end dates.
- Exclude accounts that are ineligible under approved policy.
- Use a consistent reporting time zone.
- Identify recent successful payments, reversals, active promises to pay, and prior contact attempts.

### Step B: Prioritize accounts
Create transparent priority groups using validated characteristics:
- Days past due (DPD).
- Outstanding balance.
- Risk segment.
- Previous promise-to-pay outcomes.
- Recent contact history and channel availability.
- Contact restrictions, complaints, and applicable customer-protection rules.

Do not assume that high balance or high risk alone means an account will respond better.

### Step C: Select a suitable channel
Use approved channel eligibility and customer contact preferences. Compare FIELD, SMS, VOICE, and WHATSAPP only where the channels are appropriate and permitted. Avoid repeatedly contacting the same account through multiple channels without a defined contact policy.

## 4. Counterfactual Experiment

Run a controlled experiment among eligible accounts.

1. Define the eligible account population before assignment.
2. Randomly assign eligible accounts to a treatment group and a business-as-usual control group.
3. Stratify randomization by important characteristics such as DPD band, risk segment, and outstanding-balance band.
4. Apply the proposed targeting strategy to the treatment group.
5. Continue the existing approved strategy for the control group.
6. Track outcomes over a pre-defined period, such as 30 days, using the same rules for both groups.
7. Analyze results on an intention-to-treat basis, retaining accounts in their originally assigned groups.

Where several channels are being compared, use a properly powered multi-arm experiment or run separate controlled tests.

## 5. Success Metrics

### Primary metric
Net recovery rate over the defined observation window:

Net recovery rate = net eligible collections received during the window / eligible outstanding balance at the start of the window.

Define the numerator, treatment of reversals, and denominator consistently before the experiment begins. Avoid double-counting repeated payments.

### Secondary metrics
- Net recovered amount per eligible account.
- Percentage of accounts making a successful payment.
- Promise-to-pay rate and promise-kept rate.
- Cost per successful recovery.
- Contact success and channel delivery rates.
- Complaints, opt-outs, and contact-policy violations.

## 6. Evaluation

Compare the treatment and control groups on the pre-defined primary metric. Report the absolute difference, relative difference where meaningful, confidence interval, sample size, and statistical significance.

Check whether the treatment effect differs across pre-specified DPD, risk, and balance groups. Do not claim causal improvement from simple comparisons of historical campaign results.

## 7. Data and Operational Risks

- Campaign date alignment must be reconciled before attributing outcomes to campaigns.
- Payments must be linked to accounts and events using validated identifiers and timestamps.
- Repeated payment IDs and reversed payments require investigation.
- Borrower and agent identity conflicts limit reliable attribution.
- Historical payments may precede targeting or be associated with other collection activity.
- Any experiment must comply with approved contact policies and customer-protection requirements.

## 8. Conclusion

The existing data is sufficient to identify quality problems and propose a controlled targeting experiment, but it does not establish that one channel or targeting strategy causes better recovery. A randomized, time-bounded experiment with a consistent net recovery-rate definition is recommended to test whether the proposed approach improves outcomes.
## Campaign Date Alignment and Exploratory Outcomes

### Campaign date alignment

Comparing targeting dates with campaign start and end dates at the calendar-date level produced the following results:

| Alignment | Targeting rows | Percentage |
|---|---:|---:|
| Before campaign start | 15,253 | 33.90% |
| Within campaign window | 8,861 | 19.69% |
| After campaign end | 20,886 | 46.41% |
| **Total** | **45,000** | **100.00%** |

Only 19.69% of targeting records fall within their campaign's stated date window. This discrepancy requires investigation before campaign-level performance is interpreted. Possible explanations to investigate include campaign metadata errors, reused campaign identifiers, date-boundary conventions, or targeting records generated outside the intended campaign period. These are hypotheses, not established causes.

### Exploratory payment association

Of 23,344 distinct targeted accounts, 10,288 had at least one linked successful payment, approximately 44.1%. The gross successful-payment amount linked to targeted accounts was 1,022,731,952.22.

These figures are descriptive associations only. They do not establish that targeting caused the payments: a payment may have occurred before targeting, and targeted accounts may differ from untargeted accounts in their underlying likelihood of repayment.

### Recommended evaluation design

For a credible campaign-effect estimate:

1. Define a consistent eligible-account population and an outcome window.
2. Record each account's treatment assignment and first targeting timestamp.
3. Compare targeted accounts with an appropriate control group, ideally through randomized assignment.
4. Measure net successful collections after reversals within the same fixed period, using a clearly defined denominator.
5. Compare results by campaign and channel only after campaign dates, account identities, and channel attribution have been validated.

Until these checks are complete, the available results do not establish a causal campaign effect or substantiate a sustained 11% month-on-month recovery improvement.