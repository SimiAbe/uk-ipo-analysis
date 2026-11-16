-- Data-quality checks run before analysis
-- 1) IPO rows where new and existing money raised are identical and non-zero
--    (possible duplication; clusters after LSE's August 2026 format change)
-- 2) IPO rows with no country of incorporation recorded
SELECT
    year,
    SUM(CASE WHEN raised_new_gbp_m > 0
              AND raised_new_gbp_m = raised_existing_gbp_m THEN 1 ELSE 0 END) AS new_equals_existing,
    SUM(CASE WHEN country_of_inc IS NULL THEN 1 ELSE 0 END)                     AS missing_country,
    COUNT(*)                                                                    AS ipos
FROM new_issues
WHERE is_ipo = 1
  AND year >= 2015
GROUP BY year
ORDER BY year;
