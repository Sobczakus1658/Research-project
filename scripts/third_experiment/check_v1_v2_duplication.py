"""
Verifies the claim behind data_to_third_experiment.sql's comment that
pr_review_comments (v1) would double-count rows against pr_review_comments_v2
if both were summed. Confirms v1 is a strict subset of v2 by id (same rows,
identical body text), which is why the fixed query uses v2 only.
"""
import duckdb

PR_REVIEW_COMMENTS_V1_PARQUET = '../../data/raw/pr_review_comments.parquet'
PR_REVIEW_COMMENTS_V2_PARQUET = '../../data/raw/pr_review_comments_v2.parquet'

con = duckdb.connect()
con.execute(f"CREATE VIEW v1 AS SELECT * FROM read_parquet('{PR_REVIEW_COMMENTS_V1_PARQUET}')")
con.execute(f"CREATE VIEW v2 AS SELECT * FROM read_parquet('{PR_REVIEW_COMMENTS_V2_PARQUET}')")

n1 = con.execute("SELECT COUNT(*) FROM v1").fetchone()[0]
n2 = con.execute("SELECT COUNT(*) FROM v2").fetchone()[0]
both = con.execute("SELECT COUNT(*) FROM v1 JOIN v2 ON v1.id = v2.id").fetchone()[0]
v1_only = con.execute("SELECT COUNT(*) FROM v1 WHERE id NOT IN (SELECT id FROM v2)").fetchone()[0]
v2_only = con.execute("SELECT COUNT(*) FROM v2 WHERE id NOT IN (SELECT id FROM v1)").fetchone()[0]
body_mismatch = con.execute(
    "SELECT COUNT(*) FROM v1 JOIN v2 ON v1.id = v2.id WHERE v1.body IS DISTINCT FROM v2.body"
).fetchone()[0]

print(f"v1 (pr_review_comments) rows: {n1}")
print(f"v2 (pr_review_comments_v2) rows: {n2}")
print(f"ids present in both: {both}")
print(f"ids only in v1: {v1_only}")
print(f"ids only in v2: {v2_only}")
print(f"matched ids with different body text: {body_mismatch}")
print()
if v1_only == 0 and body_mismatch == 0:
    print("CONFIRMED: v1 is a strict subset of v2 (same id -> identical body). "
          "Summing both via UNION ALL would double-count every v1 row -- "
          "this is why data_to_third_experiment.sql uses v2 only.")
