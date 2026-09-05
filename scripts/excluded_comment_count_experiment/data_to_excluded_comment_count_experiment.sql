WITH combined_comments AS (
    SELECT pr_id, user, user_type, id FROM pr_comments WHERE user_type = 'User'
    UNION ALL
    SELECT r.pr_id, c.user, c.user_type, c.id FROM pr_review_comments_v2 c JOIN pr_reviews r ON c.pull_request_review_id = r.id WHERE c.user_type = 'User'
),
pr_comment_stats AS (
    SELECT pr_id, COUNT(id) as total_comments FROM combined_comments GROUP BY pr_id
)
SELECT
    COALESCE(iss.user, pr.user) AS real_human_author,
    pr.id AS pull_request_id,
    COALESCE(cs.total_comments, 0) AS comments_by_human_maintainers
FROM pull_request pr
LEFT JOIN related_issue ri ON pr.id = ri.pr_id
LEFT JOIN issue iss ON ri.issue_id = iss.id
LEFT JOIN pr_comment_stats cs ON pr.id = cs.pr_id
WHERE
    real_human_author NOT LIKE '%[bot]%'
    AND real_human_author NOT IN ('Copilot')
    AND real_human_author IS NOT NULL
ORDER BY comments_by_human_maintainers DESC;