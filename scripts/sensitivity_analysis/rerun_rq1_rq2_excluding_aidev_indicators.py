"""
Reruns RQ1 and RQ2 (descriptive stats + Kruskal-Wallis) using the cluster
labels from clustering_sensitivity_checks.py's check (iv) -- clustering
without the 3 AIDev-derived indicators -- to see whether RQ1's large effect
size is partly circular (built, in part, from the same agent-usage signal
it then measures as an outcome). Run clustering_sensitivity_checks.py first.

Reported in ei-paper/5-threats.tex (Internal validity, end of paragraph on
the four sensitivity checks).
"""
import pandas as pd
from scipy import stats

labels = pd.read_csv('../../data/sensitivity_analysis/exclude_aidev_indicators_labels.csv')
ORDER = ['Junior', 'Mid', 'Senior']


def report(name, df, col):
    print(f"=== {name} (clustering without AIDev-derived indicators) ===")
    print(df.groupby('experience')[col].agg(['count', 'mean', 'median']).reindex(ORDER))
    groups = [df[df.experience == g][col].dropna() for g in ORDER]
    h, p = stats.kruskal(*groups)
    print(f"Kruskal-Wallis H={h:.2f} p={p:.4e}\n")


pr = pd.read_csv('../../data/first_experiment/pull_requests_sum.csv', names=['login', 'pull_requests'])
m1 = pd.merge(labels, pr, on='login')
report("RQ1", m1, 'pull_requests')

ratio = pd.read_csv(
    '../../data/second_experiment/ratio_merge_requests_all.csv',
    header=None, names=['login', 'total_mr', 'accepted_mr', 'rejected_mr', 'acceptance_rate'],
)
ratio['acceptance_rate'] = pd.to_numeric(ratio['acceptance_rate'], errors='coerce')
m2 = pd.merge(labels, ratio, on='login')
report("RQ2", m2, 'acceptance_rate')
