CREATE INDEX id_all_pull_request ON all_pull_request (id);
CREATE INDEX user_id_all_pull_request ON all_pull_request (user_id);
CREATE INDEX repo_id_all_pull_request ON all_pull_request (repo_id);

CREATE INDEX id_all_repository ON all_repository (id);

CREATE INDEX id_user ON all_user (id);
CREATE INDEX login_user ON all_user (login);

CREATE INDEX id_human_pr_task_type ON human_pr_task_type (id);

CREATE INDEX id_human_pull_request ON human_pull_request (id);
CREATE INDEX user_human_pull_request ON human_pull_request (user_id);

CREATE INDEX id_issue ON issue (id);
CREATE INDEX user_id_issue ON issue (user_id);

CREATE INDEX id_pr_comments ON pr_comments (id);
CREATE INDEX pr_id_pr_comments ON pr_comments (pr_id);
CREATE INDEX user_id_pr_comments ON pr_comments (user_id);

CREATE INDEX pr_id_pr_commit_details ON pr_commit_details(pr_id);

CREATE INDEX pr_id_pr_commits ON pr_commits(pr_id);

CREATE INDEX id_pr_reviews_comments ON pr_reviews_comments(id);
CREATE INDEX user_pr_reviews_comments ON pr_reviews_comments(user);
CREATE INDEX pull_request_review_id_pr_reviews_comments ON pr_reviews_comments(pull_request_review_id);

CREATE INDEX id_pr_reviews_comments2 ON pr_reviews_comments(id);
CREATE INDEX user_pr_reviews_comments2 ON pr_reviews_comments(user);
CREATE INDEX pull_request_review_id_pr_reviews_comments2 ON pr_reviews_comments(pull_request_review_id);

CREATE INDEX id_pr_reviews ON pr_reviews(id);
CREATE INDEX pr_id_pr_reviews ON pr_reviews(pr_id);
CREATE INDEX user_pr_reviews ON pr_reviews(user);

CREATE INDEX id_pr_task_type ON pr_task_type(id);

CREATE INDEX id_pr_task_type ON pr_timeline(pr_id);

CREATE INDEX pr_id_related_issue on related_issue(pr_id);
