-- Companies moving between markets (not IPOs): is AIM still feeding the Main Market?
SELECT
    year,
    transfer,
    COUNT(*) AS companies
FROM new_issues
WHERE is_ipo = 0
  AND transfer IS NOT NULL
  AND year >= 2015
GROUP BY year, transfer
ORDER BY year, companies DESC;
