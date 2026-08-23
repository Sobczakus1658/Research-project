SELECT
    au.login,
    COALESCE(au.followers, 0) AS followers,
    COALESCE(rep_stats.max_stars, 0) AS max_stars,
    COALESCE(rep_stats.max_forks, 0) AS max_forks,
    (2026 - CAST(SUBSTR(au.created_at, 1, 4) AS INT)) AS account_age,
    COALESCE(hpr.human_pr_count, 0) AS human_prs,
    COALESCE(comm_counts.total_commits, 0) AS total_commits,
    COALESCE(rev_counts.total_reviews, 0) AS total_reviews,
    COALESCE(iss_counts.total_issues, 0) AS total_issues
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
    SELECT user_id, COUNT(id) AS human_pr_count
    FROM human_pull_request GROUP BY user_id
) hpr ON au.id = hpr.user_id
LEFT JOIN (
    SELECT author, COUNT(pr_id) AS total_commits
    FROM pr_commits GROUP BY author
) comm_counts ON au.login = comm_counts.author
LEFT JOIN (
    SELECT user, COUNT(id) AS total_reviews
    FROM pr_reviews WHERE user_type = 'User' GROUP BY user
) rev_counts ON au.login = rev_counts.user
LEFT JOIN (
    SELECT user, COUNT(id) AS total_issues
    FROM issue GROUP BY user
) iss_counts ON au.login = iss_counts.user;