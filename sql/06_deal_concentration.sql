-- How dependent is each year's fundraising on its single largest IPO?
WITH ranked AS (
    SELECT
        year,
        company,
        raised_new_gbp_m,
        ROW_NUMBER() OVER (PARTITION BY year ORDER BY raised_new_gbp_m DESC) AS rn,
        SUM(raised_new_gbp_m) OVER (PARTITION BY year)                       AS year_total
    FROM new_issues
    WHERE is_ipo = 1
      AND year >= 2015
)
SELECT
    year,
    company                                        AS largest_ipo,
    ROUND(raised_new_gbp_m, 0)                     AS largest_ipo_gbp_m,
    ROUND(year_total, 0)                           AS year_total_gbp_m,
    ROUND(100.0 * raised_new_gbp_m / year_total, 0) AS largest_share_pct
FROM ranked
WHERE rn = 1
ORDER BY year;
