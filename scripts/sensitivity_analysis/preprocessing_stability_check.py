"""
Complete-case stability check that motivated switching clustering
preprocessing from QuantileTransformer to log1p + StandardScaler.

For each preprocessing variant, this clusters (a) the full population
(72,189 developers, with 1,755 imputed via random_forest.py) and (b) the
complete-case population only (70,434 developers with real, non-imputed
GraphQL data), then reports the Adjusted Rand Index between the two
clusterings on their overlapping developers.

Findings this script reproduces (see ei-paper/5-threats.tex, Internal
validity): QuantileTransformer -> ARI ~= 0.46 (unstable); log1p -> ARI ~=
0.98 (stable). This is why log1p is the preprocessing actually used in
find_the_best_k.py / filter_and_PCA.py / k_means.py.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, QuantileTransformer
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

RANDOM_STATE = 42


def label_clusters(X, k=3, seed=RANDOM_STATE):
    km = KMeans(n_clusters=k, init='k-means++', random_state=seed, n_init=10)
    raw = km.fit_predict(X)
    means = pd.DataFrame(X).assign(raw=raw).groupby('raw').mean().sum(axis=1)
    rank = means.sort_values().index
    mapping = {rank[0]: 'Junior', rank[1]: 'Mid', rank[2]: 'Senior'}
    return pd.Series(raw).map(mapping).values


def cluster_population(df, feature_cols, transform):
    logins = df['login']
    features = df[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    if transform == 'log1p':
        X = np.log1p(features)
    elif transform == 'quantile':
        X = pd.DataFrame(
            QuantileTransformer(output_distribution='normal', random_state=RANDOM_STATE).fit_transform(features),
            columns=features.columns,
        )
    else:
        raise ValueError(transform)
    X = StandardScaler().fit_transform(X)
    iso = IsolationForest(contamination=0.01, random_state=RANDOM_STATE)
    keep = iso.fit_predict(X) == 1
    X_clean = X[keep]
    logins_clean = logins[keep].reset_index(drop=True)
    labels = label_clusters(X_clean)
    return pd.DataFrame({'login': logins_clean, 'experience': labels})


def main():
    aidev_df = pd.read_csv('../../data/prepare_data/data_from_aidev.csv')
    github_df = pd.read_csv('../../data/prepare_data/data_from_github.csv')
    aidev_df['login'] = aidev_df['login'].astype(str).str.strip()
    github_df['login'] = github_df['login'].astype(str).str.strip()

    full_df = pd.read_csv('../../data/prepare_data/final_combined_data.csv')
    feature_cols = [c for c in full_df.columns if c != 'login']

    cc_df = pd.merge(aidev_df, github_df, on='login', how='inner')
    target_cols = ['collab_breadth', '5yr_public_commits', '5yr_private_work',
                    '5yr_reviews_given', '5yr_prs_opened']
    for col in target_cols:
        cc_df[col] = cc_df[col].round().astype(int)

    print(f"Full population: {len(full_df)}; complete-case population: {len(cc_df)}\n")

    for transform in ['quantile', 'log1p']:
        print(f"=== preprocessing = {transform} ===")
        full_labels = cluster_population(full_df, feature_cols, transform)
        cc_labels = cluster_population(cc_df, feature_cols, transform)
        print("full sizes:", full_labels['experience'].value_counts().to_dict())
        print("complete-case sizes:", cc_labels['experience'].value_counts().to_dict())
        m = pd.merge(full_labels, cc_labels, on='login', suffixes=('_full', '_cc'))
        ari = adjusted_rand_score(m['experience_full'], m['experience_cc'])
        print(f"overlap N={len(m)}, Adjusted Rand Index (full vs complete-case) = {ari:.4f}\n")


if __name__ == '__main__':
    main()
