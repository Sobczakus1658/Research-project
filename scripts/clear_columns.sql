ALTER TABLE related_issue DROP COLUMN source;

ALTER TABLE pr_timeline DROP COLUMN assignee;
ALTER TABLE pr_timeline DROP COLUMN label;
ALTER TABLE pr_timeline DROP COLUMN message;

ALTER TABLE pr_task_type DROP COLUMN title;
ALTER TABLE pr_task_type DROP COLUMN reason;

ALTER TABLE pr_reviews DROP COLUMN body;

ALTER TABLE pr_review_comments DROP COLUMN diff_hunk;
ALTER TABLE pr_review_comments DROP COLUMN path;
ALTER TABLE pr_review_comments DROP COLUMN body;
ALTER TABLE pr_review_comments DROP COLUMN in_reply_to_id;
ALTER TABLE pr_review_comments DROP COLUMN pull_request_url;
ALTER TABLE pr_review_comments DROP COLUMN position;
ALTER TABLE pr_review_comments DROP COLUMN original_position;

ALTER TABLE pr_review_comments_v2 DROP COLUMN diff_hunk;
ALTER TABLE pr_review_comments_v2 DROP COLUMN path;
ALTER TABLE pr_review_comments_v2 DROP COLUMN body;
ALTER TABLE pr_review_comments_v2 DROP COLUMN in_reply_to_id;
ALTER TABLE pr_review_comments_v2 DROP COLUMN pull_request_url;
ALTER TABLE pr_review_comments_v2 DROP COLUMN position;
ALTER TABLE pr_review_comments_v2 DROP COLUMN original_position;

ALTER TABLE pr_commit_details DROP COLUMN message;
ALTER TABLE pr_commit_details DROP COLUMN commit_stats_additions;
ALTER TABLE pr_commit_details DROP COLUMN commit_stats_deletions;
ALTER TABLE pr_commit_details DROP COLUMN filename;
ALTER TABLE pr_commit_details DROP COLUMN additions;
ALTER TABLE pr_commit_details DROP COLUMN deletions;
ALTER TABLE pr_commit_details DROP COLUMN patch;

ALTER TABLE pr_comments DROP COLUMN body;

ALTER TABLE issue DROP COLUMN body;
ALTER TABLE issue DROP COLUMN closed_at;
ALTER TABLE issue DROP COLUMN html_url;
ALTER TABLE issue DROP COLUMN title;
ALTER TABLE issue DROP COLUMN number;

ALTER TABLE human_pr_task_type DROP COLUMN title;
ALTER TABLE human_pr_task_type DROP COLUMN reason;
