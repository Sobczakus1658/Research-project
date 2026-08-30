import pandas as pd
from sklearn.cluster import KMeans


df = pd.read_csv('../../data/prepare_data/preprocessed_data_12d.csv')
features_df = df.drop(columns=['login']).apply(pd.to_numeric, errors='coerce')
features_df = features_df.fillna(features_df.median())

X = features_df

kmeans = KMeans(n_clusters=3, init='k-means++', random_state=42, n_init=10)
raw_labels = kmeans.fit_predict(X)

df['experience_raw'] = raw_labels
cluster_means = df.groupby('experience_raw').mean(numeric_only=True).sum(axis=1)
rank_map = cluster_means.sort_values().index
label_mapping = {
    rank_map[0]: 'Junior',
    rank_map[1]: 'Mid',
    rank_map[2]: 'Senior'
}

df['experience'] = df['experience_raw'].map(label_mapping)

print("Cluster Strength (Count):")
print(df['experience'].value_counts())

output_df = df[['login', 'experience']]
output_df.to_csv('../../data/prepare_data/user_experience_levels.csv', index=False)

print("\nFile saved to '../../data/prepare_data/user_experience_levels.csv'")