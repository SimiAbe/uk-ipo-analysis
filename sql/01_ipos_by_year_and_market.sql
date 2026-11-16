-- Number of IPOs and new money raised per year, AIM vs Main Market (2015 onwards)
SELECT
    year,
    market_group,
    COUNT(*)                         AS ipos,
    ROUND(SUM(raised_new_gbp_m), 0)  AS new_money_gbp_m
FROM new_issues
WHERE is_ipo = 1
  AND year >= 2015
GROUP BY year, market_group
ORDER BY year, market_group;
