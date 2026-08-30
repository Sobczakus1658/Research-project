CREATE OR REPLACE VIEW repository_owners AS
SELECT
    url,
    SPLIT_PART(full_name, '/', 1) AS owner
FROM all_repository;

SELECT
    au.login,
    COALESCE(au.followers, 0) AS followers,
    COALESCE(rep_stats.max_stars, 0) AS max_stars,
    COALESCE(rep_stats.max_forks, 0) AS max_forks,
    (2026 - CAST(SUBSTR(au.created_at, 1, 4) AS INT)) AS account_age,
    COALESCE(pr_stats.activity_span_days, 0) AS agent_activity_span_days,
    COALESCE(pr_stats.agent_diversity, 0) AS agent_diversity,
    COALESCE(pr_stats.repo_breadth, 0) AS agentic_repo_breadth
FROM all_user au
LEFT JOIN (
    SELECT
        ro.owner,
        MAX(ar.stars) AS max_stars,
        MAX(ar.forks) AS max_forks
    FROM repository_owners ro
    JOIN all_repository ar ON ro.url = ar.url
    GROUP BY ro.owner
) rep_stats ON au.login = rep_stats.owner
LEFT JOIN (
    SELECT
        user_id,
        CAST(MAX(created_at) AS DATE) - CAST(MIN(created_at) AS DATE) AS activity_span_days,
        COUNT(DISTINCT agent) AS agent_diversity,
        COUNT(DISTINCT repo_id) AS repo_breadth
    FROM all_pull_request
    GROUP BY user_id
) pr_stats ON au.id = pr_stats.user_id;
