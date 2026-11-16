-- Which sectors still list? Top sectors by IPO count, 2021 onwards
SELECT
    ftse_sector,
    COUNT(*)                        AS ipos,
    ROUND(SUM(raised_new_gbp_m), 0) AS new_money_gbp_m
FROM new_issues
WHERE is_ipo = 1
  AND year >= 2021
  AND ftse_sector IS NOT NULL
GROUP BY ftse_sector
ORDER BY ipos DESC
LIMIT 10;
