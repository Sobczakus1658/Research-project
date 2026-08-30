"""
Checks the overlap between human_pull_request's authors and the 72,189
developers linked to Agentic-PRs -- the number quoted in
ei-paper/3-method.tex (RQ4 paragraph) as the reason RQ4 compares two
independent populations instead of stratifying by activity profile.

Requires data/prepare_data/data_from_aidev.csv (built from AIDev's
all_user table) and a CSV of distinct human_pull_request authors; the
latter is not otherwise produced by this repo's pipeline, so this script
expects it as data/fourth_experiment/human_pull_request_authors.csv
(single column: login), extracted with:
    SELECT DISTINCT user AS login FROM human_pull_request;
"""
import pandas as pd

aidev_df = pd.read_csv('../../data/prepare_data/data_from_aidev.csv')
aidev_df['login'] = aidev_df['login'].astype(str).str.strip()

human_authors = pd.read_csv('../../data/fourth_experiment/human_pull_request_authors.csv')
human_authors['login'] = human_authors['login'].astype(str).str.strip()

overlap = set(aidev_df['login']) & set(human_authors['login'])

print(f"Agentic-PR population (all_user / data_from_aidev.csv): {len(aidev_df)}")
print(f"Distinct human_pull_request authors: {len(human_authors)}")
print(f"Overlap: {len(overlap)}")
