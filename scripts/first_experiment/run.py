import pandas as pd

df_pr = pd.read_csv('../../data/first_experiment/pull_requests_sum.csv', names=['login', 'pull_requests'])

df_clusters = pd.read_csv('../../data/prepare_data/user_experience_levels.csv')

merged_df = pd.merge(df_clusters, df_pr, on='login')

final_df = merged_df[['experience', 'pull_requests']].rename(
    columns={'experience': 'experience', 'pull_requests': 'pull_request'}
)

final_df.to_csv('../../data/first_experiment/experience_pull_request.csv', index=False)

