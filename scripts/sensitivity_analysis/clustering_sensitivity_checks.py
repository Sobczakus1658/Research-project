"""
Four sensitivity checks against the log1p-based clustering pipeline used in
k_means.py, reported in ei-paper/5-threats.tex (Internal validity):

  (i)   alternative k (2, 3, 4, 5)
  (ii)  repeated initializations (different random seeds for the whole
        pipeline: Isolation Forest + k-means, not just k-means' n_init)
  (iii) retained outliers (skip Isolation Forest entirely)
  (iv)  excluding the 3 AIDev-derived indicators (agent_activity_span_days,
        agent_diversity, agentic_repo_breadth), leaving the other 9

Each check reports cluster sizes and, where meaningful, the Adjusted Rand
Index against the reported k=3/log1p/outliers-removed/12-indicator baseline.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

RANDOM_STATE = 42
AIDEV_DERIVED_COLS = ['agent_activity_span_days', 'agent_diversity', 'agentic_repo_breadth']


def preprocess(features, seed=RANDOM_STATE):
    X = np.log1p(features)
    X = StandardScaler().fit_transform(X)
    iso = IsolationForest(contamination=0.01, random_state=seed)
    keep = iso.fit_predict(X) == 1
    return X[keep], keep


def label_clusters(X, k, seed=RANDOM_STATE):
    km = KMeans(n_clusters=k, init='k-means++', random_state=seed, n_init=10)
    raw = km.fit_predict(X)
    means = pd.DataFrame(X).assign(raw=raw).groupby('raw').mean().sum(axis=1)
    rank = means.sort_values().index
    if k == 3:
        mapping = {rank[0]: 'Junior', rank[1]: 'Mid', rank[2]: 'Senior'}
    else:
        mapping = {r: f'C{i}' for i, r in enumerate(rank)}
    return pd.Series(raw).map(mapping).values


def main():
    df = pd.read_csv('../../data/prepare_data/final_combined_data.csv')
    df = df.dropna(subset=['login']).fillna(0)
    logins = df['login']
    features = df.drop(columns=['login'])

    X_baseline, keep_baseline = preprocess(features)
    logins_baseline = logins[keep_baseline].reset_index(drop=True)
    baseline_labels = label_clusters(X_baseline, 3)
    print("=== BASELINE (k=3, seed=42, outliers removed, 12 indicators) ===")
    print(pd.Series(baseline_labels).value_counts(), "\n")

    print("=== (i) Alternative k ===")
    for k in [2, 4, 5]:
        labs = label_clusters(X_baseline, k)
        print(f"k={k}:", pd.Series(labs).value_counts().to_dict())
    print()

    print("=== (ii) Repeated initializations (different seeds, whole pipeline) ===")
    for seed in [0, 1, 2, 7, 123]:
        X_s, keep_s = preprocess(features, seed=seed)
        logins_s = logins[keep_s].reset_index(drop=True)
        labs_s = label_clusters(X_s, 3, seed=seed)
        m = pd.merge(
            pd.DataFrame({'login': logins_baseline, 'base': baseline_labels}),
            pd.DataFrame({'login': logins_s, 'seed_run': labs_s}),
            on='login',
        )
        ari = adjusted_rand_score(m['base'], m['seed_run'])
        print(f"seed={seed}: sizes={pd.Series(labs_s).value_counts().to_dict()}, ARI vs baseline={ari:.4f}")
    print()

    print("=== (iii) Retained outliers (no Isolation Forest removal) ===")
    X_full = StandardScaler().fit_transform(np.log1p(features))
    labs_keep = label_clusters(X_full, 3)
    print("sizes:", pd.Series(labs_keep).value_counts().to_dict())
    m3 = pd.merge(
        pd.DataFrame({'login': logins_baseline, 'base': baseline_labels}),
        pd.DataFrame({'login': logins, 'keep': labs_keep}),
        on='login',
    )
    print("ARI vs baseline:", adjusted_rand_score(m3['base'], m3['keep']), "\n")

    print("=== (iv) Exclude AIDev-derived indicators ===")
    features9 = features.drop(columns=AIDEV_DERIVED_COLS)
    X9, keep9 = preprocess(features9)
    logins9 = logins[keep9].reset_index(drop=True)
    labs9 = label_clusters(X9, 3)
    print("sizes (9 indicators):", pd.Series(labs9).value_counts().to_dict())
    m4 = pd.merge(
        pd.DataFrame({'login': logins_baseline, 'base': baseline_labels}),
        pd.DataFrame({'login': logins9, 'excl': labs9}),
        on='login',
    )
    print("ARI vs baseline (12 vs 9 indicators):", adjusted_rand_score(m4['base'], m4['excl']))

    out = pd.DataFrame({'login': logins9, 'experience': labs9})
    out.to_csv('../../data/sensitivity_analysis/exclude_aidev_indicators_labels.csv', index=False)
    print("\nSaved 9-indicator cluster labels to "
          "../../data/sensitivity_analysis/exclude_aidev_indicators_labels.csv "
          "for downstream RQ1/RQ2 reruns.")


if __name__ == '__main__':
    main()
