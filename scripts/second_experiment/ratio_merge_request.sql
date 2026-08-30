SELECT
    user,
    COUNT(*) AS total_resolved_pull_requests,
    SUM(CASE WHEN merged_at IS NOT NULL THEN 1 ELSE 0 END) AS accepted_pull_requests,
    SUM(CASE WHEN merged_at IS NULL THEN 1 ELSE 0 END) AS rejected_pull_requests,
    ROUND(CAST(SUM(CASE WHEN merged_at IS NOT NULL THEN 1 ELSE 0 END) AS DECIMAL) / COUNT(*) * 100, 2) AS acceptance_rate_percent
FROM
    all_pull_request
WHERE
    state != 'open'
GROUP BY
    user;