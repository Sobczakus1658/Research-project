CREATE VIEW user_experience_levels AS
WITH user_base_stats AS (
    SELECT
        au.id,
        ro.owner AS login,
        au.followers,
        MAX(ar.stars) as stars
    FROM repository_owners AS ro
    INNER JOIN all_repository AS ar
        ON ro.url = ar.url
    INNER JOIN all_user AS au
        ON au.login = ro.owner
    GROUP BY ro.owner, au.id, au.followers
)
SELECT
    id,
    login,
    stars,
    followers,
    CASE
        WHEN stars > 10 OR followers > 20 THEN 'EXPERT'

        WHEN (stars BETWEEN 2 AND 10) OR (followers BETWEEN 5 AND 20) THEN 'REGULAR'

        ELSE 'NEWCOMER'
    END AS experience_level
FROM user_base_stats;

CREATE VIEW user_experience_date AS
WITH global_start AS (
    SELECT MIN(CAST(SUBSTR(created_at, 1, 4) AS INT)) as project_start_year
    FROM all_pull_request
)
SELECT
    au.id,
    au.login,
    (gs.project_start_year - CAST(SUBSTR(au.created_at, 1, 4) AS INT)) as years_before_project,
    CASE
        WHEN (gs.project_start_year - CAST(SUBSTR(au.created_at, 1, 4) AS INT)) < 1 THEN 'NEWCOMER'
        WHEN (gs.project_start_year - CAST(SUBSTR(au.created_at, 1, 4) AS INT)) > 3 THEN 'EXPERT'
        ELSE 'REGULAR'
    END as experience_level
FROM all_user au
CROSS JOIN global_start gs;

CREATE VIEW user_experience_pr_count AS
WITH pr_stats AS (
    SELECT
        user_id,
        COUNT(id) as pr_count
    FROM all_pull_request
    GROUP BY user_id
)
SELECT
    au.id,
    au.login,
    COALESCE(ps.pr_count, 0) as total_pr_created,
    CASE
        WHEN COALESCE(ps.pr_count, 0) > 15 THEN 'EXPERT'
        WHEN COALESCE(ps.pr_count, 0) BETWEEN 4 AND 15 THEN 'REGULAR'
        ELSE 'NEWCOMER'
    END as experience_level
FROM all_user au
LEFT JOIN pr_stats ps ON  au.id = ps.user_id;

CREATE VIEW user_experience_reviews AS
WITH review_stats AS (
    SELECT
        user as user,
        SUM(CASE WHEN state = 'APPROVED' THEN 1 ELSE 0 END) as approved_count,
        SUM(CASE WHEN state = 'COMMENTED' THEN 1 ELSE 0 END) as commented_count,
        COUNT(id) as total_reviews
    FROM pr_reviews
    WHERE user_type = 'User'
    GROUP BY user
)
SELECT
    au.id,
    au.login,
    COALESCE(rs.approved_count, 0) as approved_count,
    COALESCE(rs.commented_count, 0) as commented_count,
    CASE
        WHEN COALESCE(rs.approved_count, 0) > 10 OR COALESCE(rs.commented_count, 0) > 20 THEN 'EXPERT'
        WHEN COALESCE(rs.approved_count, 0) BETWEEN 3 AND 10 OR COALESCE(rs.commented_count, 0) BETWEEN 5 AND 20 THEN 'REGULAR'
        ELSE 'NEWCOMER'
    END as experience_level
FROM all_user au
LEFT JOIN review_stats rs on au.login = rs.user;

CREATE VIEW user_experience_commits AS
WITH commit_stats AS (
    SELECT
        author,
        COUNT(pr_id) as total_commits
    FROM pr_commits
    GROUP BY author
)
SELECT
    au.id,
    au.login,
    COALESCE(cs.total_commits, 0) as total_commits_count,
    CASE
        WHEN COALESCE(cs.total_commits, 0) > 100 THEN 'EXPERT'
        WHEN COALESCE(cs.total_commits, 0) BETWEEN 20 AND 100 THEN 'REGULAR'
        ELSE 'NEWCOMER'
    END as experience_level
FROM all_user au
LEFT JOIN commit_stats cs ON au.login = cs.author;

CREATE VIEW user_experience_issues AS
WITH issue_stats AS (
    SELECT
        user,
        COUNT(id) as total_issues
    FROM issue
    GROUP BY user
)
SELECT
    au.id,
    au.login,
    COALESCE(is_s.total_issues, 0) as total_issues_count,
    CASE
        WHEN COALESCE(is_s.total_issues, 0) > 10 THEN 'EXPERT'
        WHEN COALESCE(is_s.total_issues, 0) BETWEEN 3 AND 10 THEN 'REGULAR'
        ELSE 'NEWCOMER'
    END as experience_level
FROM all_user au
LEFT JOIN issue_stats is_s ON au.login = is_s.user;

CREATE VIEW user_experience AS
WITH scores AS (
    SELECT
        u.id,
        u.login,
        (CASE r.experience_level WHEN 'EXPERT' THEN 3 WHEN 'REGULAR' THEN 2 ELSE 1 END) * 3 AS points_rep,

        (CASE d.experience_level WHEN 'EXPERT' THEN 3 WHEN 'REGULAR' THEN 2 ELSE 1 END) AS points_date,

        (CASE pr.experience_level WHEN 'EXPERT' THEN 3 WHEN 'REGULAR' THEN 2 ELSE 1 END) AS points_pr,

        (CASE rev.experience_level WHEN 'EXPERT' THEN 3 WHEN 'REGULAR' THEN 2 ELSE 1 END) AS points_rev,

        (CASE com.experience_level WHEN 'EXPERT' THEN 3 WHEN 'REGULAR' THEN 2 ELSE 1 END) AS points_com,

        (CASE iss.experience_level WHEN 'EXPERT' THEN 3 WHEN 'REGULAR' THEN 2 ELSE 1 END) AS points_iss

    FROM all_user u
    JOIN user_experience_levels r ON u.id = r.id
    JOIN user_experience_date d       ON u.id = d.id
    JOIN user_experience_pr_count pr  ON u.id = pr.id
    JOIN user_experience_reviews rev  ON u.id = rev.id
    JOIN user_experience_commits com  ON u.id = com.id
    JOIN user_experience_issues iss   ON u.id = iss.id
),
total_scoring AS (
    SELECT
        id,
        login,
        (points_rep + points_date + points_pr + points_rev + points_com + points_iss) AS final_score
    FROM scores
)
SELECT
    id,
    login,
    final_score,
    CASE
        WHEN final_score >= 19 THEN 'EXPERT'
        WHEN final_score <= 12 THEN 'NEWCOMER'
        ELSE 'REGULAR'
    END AS experience_level
FROM total_scoring;