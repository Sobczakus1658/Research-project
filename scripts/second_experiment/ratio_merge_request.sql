SELECT
    user,
    COUNT(*) AS total_pull_requests,
    SUM(CASE WHEN merged_at IS NOT NULL THEN 1 ELSE 0 END) AS accepted_pull_requests,
    SUM(CASE WHEN closed_at IS NOT NULL AND merged_at IS NULL THEN 1 ELSE 0 END) AS rejected_pull_requests, -- (lub w zależności od wersji wyliczenia)
    ROUND(CAST(COUNT(merged_at) AS DECIMAL) / COUNT(*) * 100, 2) AS acceptance_rate_percent
FROM
    human_pull_request
GROUP BY
    user;