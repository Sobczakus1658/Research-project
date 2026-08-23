SELECT
    au.login,
    COUNT(pr.id) AS total_prs
FROM all_user au
LEFT JOIN all_pull_request pr ON au.id = pr.user_id
GROUP BY au.login, au.id;