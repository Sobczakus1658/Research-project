CREATE TABLE all_pull_request AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/all_pull_request.parquet');

CREATE TABLE all_repository AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/all_repository.parquet');

CREATE TABLE all_user AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/all_user.parquet');

CREATE TABLE human_pr_task_type AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/human_pr_task_type.parquet');

CREATE TABLE human_pull_request AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/human_pull_request.parquet');

CREATE TABLE issue AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/issue.parquet');

CREATE TABLE pr_comments AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/pr_comments.parquet');

CREATE TABLE pr_commit_details AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/pr_commit_details.parquet');

CREATE TABLE pr_commits AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/pr_commits.parquet');

CREATE TABLE pr_review_comments AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/pr_review_comments.parquet');

CREATE TABLE pr_review_comments_v2 AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/pr_review_comments_v2.parquet');

CREATE TABLE pr_reviews AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/pr_reviews.parquet');

CREATE TABLE pr_task_type AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/pr_task_type.parquet');

CREATE TABLE pr_timeline AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/pr_timeline.parquet');

CREATE TABLE pull_request AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/pull_request.parquet');

CREATE TABLE related_issue AS
SELECT * FROM read_parquet('/home/sobczakus/projekt_badawczy/AIDev/related_issue.parquet');
