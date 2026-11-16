-- Headline annual totals: IPO count, new money, and total money raised
-- (existing-share sales are only recorded from 15 June 2016, so total_raised is comparable from 2017)
SELECT
    year,
    COUNT(*)                                  AS ipos,
    ROUND(SUM(raised_new_gbp_m), 0)           AS new_money_gbp_m,
    ROUND(SUM(raised_total_gbp_m), 0)         AS total_raised_gbp_m,
    ROUND(AVG(raised_new_gbp_m), 1)           AS avg_new_money_per_ipo_gbp_m,
    SUM(CASE WHEN raised_new_gbp_m >= 100 THEN 1 ELSE 0 END) AS ipos_raising_100m_plus
FROM new_issues
WHERE is_ipo = 1
  AND year >= 2015
GROUP BY year
ORDER BY year;
