import pandas as pd

aidev_df = pd.read_csv('../../data/prepare_data/data_from_aidev.csv')
aidev_df['login'] = aidev_df['login'].astype(str).str.strip()

human_authors = pd.read_csv('../../data/third_experiment/human_pull_request_authors.csv')
human_authors['login'] = human_authors['login'].astype(str).str.strip()

overlap = set(aidev_df['login']) & set(human_authors['login'])

print(f"Agentic-PR population (all_user / data_from_aidev.csv): {len(aidev_df)}")
print(f"Distinct human_pull_request authors: {len(human_authors)}")
print(f"Overlap: {len(overlap)}")
