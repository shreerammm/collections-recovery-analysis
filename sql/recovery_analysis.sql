
-- Collections Recovery Analysis
-- SQL dialect: DuckDB
-- Run from the project root folder.

-- 1. Payment status distribution
SELECT
    payment_status,
    COUNT(*) AS payment_rows,
    COUNT(DISTINCT payment_id) AS distinct_payment_ids,
    SUM(TRY_CAST(amount AS DOUBLE)) AS gross_amount
FROM read_csv_auto('data_staging/payments.csv', header = true)
GROUP BY payment_status
ORDER BY payment_status;


-- 2. Monthly gross successful payment trend
-- Descriptive measure only; not a recovery rate.
WITH successful_payments AS (
    SELECT
        DATE_TRUNC(
            'month',
            TRY_CAST(event_at AS TIMESTAMPTZ)
        ) AS payment_month,
        payment_id,
        account_id,
        TRY_CAST(amount AS DOUBLE) AS amount
    FROM read_csv_auto('data_staging/payments.csv', header = true)
    WHERE UPPER(payment_status) = 'SUCCESS'
)
SELECT
    STRFTIME(payment_month, '%Y-%m') AS month,
    COUNT(*) AS successful_rows,
    COUNT(DISTINCT payment_id) AS distinct_payment_ids,
    COUNT(DISTINCT account_id) AS distinct_accounts,
    SUM(amount) AS gross_success_amount
FROM successful_payments
GROUP BY payment_month
ORDER BY payment_month;


-- 3. Payment data quality checks
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (
        WHERE payment_reference IS NULL
           OR TRIM(CAST(payment_reference AS VARCHAR)) = ''
    ) AS missing_payment_references,
    COUNT(*) FILTER (
        WHERE event_at IS NULL
           OR TRY_CAST(event_at AS TIMESTAMPTZ) IS NULL
    ) AS missing_or_invalid_event_dates,
    COUNT(*) FILTER (
        WHERE TRY_CAST(amount AS DOUBLE) IS NULL
           OR TRY_CAST(amount AS DOUBLE) <= 0
    ) AS invalid_or_nonpositive_amounts
FROM read_csv_auto('data_staging/payments.csv', header = true);


-- 4. Payment IDs appearing more than once
-- Investigate before excluding any records.
SELECT
    payment_id,
    COUNT(*) AS row_count,
    COUNT(DISTINCT account_id) AS account_count,
    COUNT(DISTINCT payment_status) AS status_count,
    SUM(TRY_CAST(amount AS DOUBLE)) AS summed_amount
FROM read_csv_auto('data_staging/payments.csv', header = true)
GROUP BY payment_id
HAVING COUNT(*) > 1
ORDER BY row_count DESC, payment_id;


-- 5. Campaign targeting date alignment
SELECT
    COUNT(*) AS targeting_rows,
    COUNT(*) FILTER (
        WHERE TRY_CAST(t.target_date AS DATE)
              < TRY_CAST(c.start_at AS DATE)
    ) AS before_campaign_start,
    COUNT(*) FILTER (
        WHERE TRY_CAST(t.target_date AS DATE)
              > TRY_CAST(c.end_at AS DATE)
    ) AS after_campaign_end,
    COUNT(*) FILTER (
        WHERE TRY_CAST(t.target_date AS DATE)
              BETWEEN TRY_CAST(c.start_at AS DATE)
                  AND TRY_CAST(c.end_at AS DATE)
    ) AS within_campaign_window
FROM read_csv_auto('data_staging/daily_targeting.csv', header = true) t
LEFT JOIN read_csv_auto('data_staging/campaigns.csv', header = true) c
    ON t.campaign_id = c.campaign_id;
