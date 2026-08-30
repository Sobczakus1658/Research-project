"""
Reruns RQ1-RQ3 restricted to the 70,434 complete-case developers (excluding
the 1,755 developers whose GraphQL indicators were random-forest-imputed),
under the log1p clustering pipeline actually used in k_means.py. RQ4 is
unaffected by clustering/imputation choices by construction and is not
rerun here.

Reported in ei-paper/5-threats.tex (Internal validity) and
ei-paper/4-results.tex (RQ3 paragraph): RQ1 and RQ2 are essentially
unchanged; RQ3 does not replicate (its direction reverses and loses
significance).
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from scipy import stats

RANDOM_STATE = 42
ORDER = ['Junior', 'Mid', 'Senior']


def cluster(df, feature_cols, seed=RANDOM_STATE):
    logins = df['login']
    features = df[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    X = StandardScaler().fit_transform(np.log1p(features))
    iso = IsolationForest(contamination=0.01, random_state=seed)
    keep = iso.fit_predict(X) == 1
    X_clean = X[keep]
    logins_clean = logins[keep].reset_index(drop=True)
    km = KMeans(n_clusters=3, init='k-means++', random_state=seed, n_init=10)
    raw = km.fit_predict(X_clean)
    means = pd.DataFrame(X_clean).assign(raw=raw).groupby('raw').mean().sum(axis=1)
    rank = means.sort_values().index
    mapping = {rank[0]: 'Junior', rank[1]: 'Mid', rank[2]: 'Senior'}
    return pd.DataFrame({'login': logins_clean, 'experience': pd.Series(raw).map(mapping).values})


def report(name, df, col):
    print(f"=== {name} (complete-case, log1p) ===")
    print(df.groupby('experience')[col].agg(['count', 'mean', 'std', 'median']).reindex(ORDER))
    groups = [df[df.experience == g][col].dropna() for g in ORDER]
    h, p = stats.kruskal(*groups)
    n_total = sum(len(g) for g in groups)
    print(f"Kruskal-Wallis H={h:.2f} p={p:.4e} epsilon-squared={h/(n_total-1):.4f}")
    for a, b in [(ORDER[0], ORDER[1]), (ORDER[0], ORDER[2]), (ORDER[1], ORDER[2])]:
        d1 = df[df.experience == a][col].dropna()
        d2 = df[df.experience == b][col].dropna()
        u, pv = stats.mannwhitneyu(d1, d2, alternative='two-sided')
        r = 1 - (2 * u) / (len(d1) * len(d2))
        print(f"  {a} vs {b}: U={u:.1f} p={pv:.4e} rank-biserial r={r:.4f}")
    print()


def main():
    full_df = pd.read_csv('../../data/prepare_data/final_combined_data.csv')
    aidev_df = pd.read_csv('../../data/prepare_data/data_from_aidev.csv')
    github_df = pd.read_csv('../../data/prepare_data/data_from_github.csv')
    aidev_df['login'] = aidev_df['login'].astype(str).str.strip()
    github_df['login'] = github_df['login'].astype(str).str.strip()
    cc_df = pd.merge(aidev_df, github_df, on='login', how='inner')
    for col in ['collab_breadth', '5yr_public_commits', '5yr_private_work',
                '5yr_reviews_given', '5yr_prs_opened']:
        cc_df[col] = cc_df[col].round().astype(int)

    feature_cols = [c for c in full_df.columns if c != 'login']
    cc_labels = cluster(cc_df, feature_cols)
    full_labels = pd.read_csv('../../data/prepare_data/user_experience_levels.csv')

    m = pd.merge(full_labels, cc_labels, on='login', suffixes=('_full', '_cc'))
    print(f"overlap N={len(m)}, ARI (full vs complete-case) = "
          f"{adjusted_rand_score(m['experience_full'], m['experience_cc']):.4f}\n")

    cc_labels.to_csv('../../data/sensitivity_analysis/complete_case_labels.csv', index=False)

    pr = pd.read_csv('../../data/first_experiment/pull_requests_sum.csv', names=['login', 'pull_requests'])
    report("RQ1", pd.merge(cc_labels, pr, on='login'), 'pull_requests')

    ratio = pd.read_csv(
        '../../data/second_experiment/ratio_merge_requests_all.csv',
        header=None, names=['login', 'total_mr', 'accepted_mr', 'rejected_mr', 'acceptance_rate'],
    )
    ratio['acceptance_rate'] = pd.to_numeric(ratio['acceptance_rate'], errors='coerce')
    report("RQ2", pd.merge(cc_labels, ratio, on='login'), 'acceptance_rate')

    rq3 = pd.read_csv('../../data/third_experiment/data_to_third_experiment.csv')
    m3 = pd.merge(rq3, cc_labels, left_on='real_human_author', right_on='login', how='inner')
    report("RQ3", m3, 'comments_by_human_maintainers')


if __name__ == '__main__':
    main()
