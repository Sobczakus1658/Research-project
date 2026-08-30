"""
Computes 95% bootstrap confidence intervals for every effect size reported
in ei-paper/4-results.tex: epsilon-squared (Kruskal-Wallis) and
rank-biserial correlation (pairwise Mann-Whitney U) for RQ1-RQ3, and
rank-biserial correlation for RQ4.

Method (documented in ei-paper/3-method.tex, Statistical analysis
subsection): resample each group independently with replacement, recompute
the statistic, repeat 2,000 times, take the 2.5th/97.5th percentiles.
"""
import pandas as pd
import numpy as np
from scipy import stats

np.random.seed(42)
N_BOOT = 2000
ORDER = ['Junior', 'Mid', 'Senior']


def boot_eps2(groups, n_boot=N_BOOT):
    vals = list(groups.values())
    n_total = sum(len(v) for v in vals)
    obs_h, _ = stats.kruskal(*vals)
    obs_eps2 = obs_h / (n_total - 1)
    boots = []
    for _ in range(n_boot):
        rs = [np.random.choice(v, len(v), replace=True) for v in vals]
        h, _ = stats.kruskal(*rs)
        boots.append(h / (n_total - 1))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return obs_eps2, lo, hi


def boot_rb(g1, g2, n_boot=N_BOOT):
    n1, n2 = len(g1), len(g2)
    obs_u, _ = stats.mannwhitneyu(g1, g2, alternative='two-sided')
    obs_r = 1 - (2 * obs_u) / (n1 * n2)
    boots = []
    for _ in range(n_boot):
        r1 = np.random.choice(g1, n1, replace=True)
        r2 = np.random.choice(g2, n2, replace=True)
        u, _ = stats.mannwhitneyu(r1, r2, alternative='two-sided')
        boots.append(1 - (2 * u) / (n1 * n2))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return obs_r, lo, hi


def run_rq(name, groups_dict, order, pairs):
    print(f"\n========== {name} ==========")
    groups = {g: groups_dict[g] for g in order}
    eps2, lo, hi = boot_eps2(groups)
    print(f"epsilon-squared = {eps2:.4f}  95% CI [{lo:.4f}, {hi:.4f}]")
    for a, b in pairs:
        r, lo, hi = boot_rb(groups[a], groups[b])
        print(f"  {a} vs {b}: rank-biserial r = {r:.4f}  95% CI [{lo:.4f}, {hi:.4f}]")


def main():
    levels = pd.read_csv('../../data/prepare_data/user_experience_levels.csv')

    pr = pd.read_csv('../../data/first_experiment/pull_requests_sum.csv', names=['login', 'pull_requests'])
    m1 = pd.merge(levels, pr, on='login')
    g1 = {g: m1[m1.experience == g]['pull_requests'].values for g in ORDER}
    run_rq("RQ1", g1, ORDER, [('Senior', 'Junior'), ('Senior', 'Mid'), ('Mid', 'Junior')])

    ratio = pd.read_csv(
        '../../data/second_experiment/ratio_merge_requests_all.csv',
        header=None, names=['login', 'total_mr', 'accepted_mr', 'rejected_mr', 'acceptance_rate'],
    )
    ratio['acceptance_rate'] = pd.to_numeric(ratio['acceptance_rate'], errors='coerce')
    m2 = pd.merge(levels, ratio, on='login')
    g2 = {g: m2[m2.experience == g]['acceptance_rate'].dropna().values for g in ORDER}
    run_rq("RQ2", g2, ORDER, [('Senior', 'Junior'), ('Senior', 'Mid'), ('Mid', 'Junior')])

    rq3 = pd.read_csv('../../data/third_experiment/data_to_third_experiment.csv')
    m3 = pd.merge(rq3, levels, left_on='real_human_author', right_on='login', how='inner')
    g3 = {g: m3[m3.experience == g]['comments_by_human_maintainers'].values for g in ORDER}
    run_rq("RQ3", g3, ORDER, [('Junior', 'Mid'), ('Junior', 'Senior'), ('Mid', 'Senior')])

    human = pd.read_csv(
        '../../data/fourth_experiment/human_pull_request_ratio.csv',
        header=None, names=['login', 'total_mr', 'accepted_mr', 'rejected_mr', 'acceptance_rate'],
    )
    human['acceptance_rate'] = pd.to_numeric(human['acceptance_rate'], errors='coerce')
    print("\n========== RQ4 ==========")
    r, lo, hi = boot_rb(ratio['acceptance_rate'].dropna().values, human['acceptance_rate'].dropna().values)
    print(f"Agent vs Human: rank-biserial r = {r:.4f}  95% CI [{lo:.4f}, {hi:.4f}]")


if __name__ == '__main__':
    main()
