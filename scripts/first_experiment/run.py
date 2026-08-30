import pandas as pd
from scipy import stats

df_pr = pd.read_csv('../../data/first_experiment/pull_requests_sum.csv', names=['login', 'pull_requests'])

df_clusters = pd.read_csv('../../data/prepare_data/user_experience_levels.csv')

merged_df = pd.merge(df_clusters, df_pr, on='login')

final_df = merged_df[['experience', 'pull_requests']].rename(
    columns={'experience': 'experience', 'pull_requests': 'pull_request'}
)

final_df.to_csv('../../data/first_experiment/experience_pull_request.csv', index=False)


def rank_biserial(u_stat, n1, n2):
    return 1 - (2 * u_stat) / (n1 * n2)


juniors = final_df[final_df['experience'] == 'Junior']['pull_request'].dropna()
mids = final_df[final_df['experience'] == 'Mid']['pull_request'].dropna()
seniors = final_df[final_df['experience'] == 'Senior']['pull_request'].dropna()

print("==========================================================")
print("       FORMAL STATISTICAL HYPOTHESIS TESTING              ")
print("==========================================================")

kw_stat, kw_p = stats.kruskal(juniors, mids, seniors)
n_total = len(juniors) + len(mids) + len(seniors)
epsilon_sq = kw_stat / (n_total - 1)

print(f"1. Kruskal-Wallis Test (for 3 groups):")
print(f"   - H-statistic: {kw_stat:.4f}")
print(f"   - p-value:     {kw_p:.4e}")
print(f"   - epsilon-squared effect size: {epsilon_sq:.4f}")

alpha = 0.05
if kw_p < alpha:
    print(f"   -> DECISION: Reject H0 (p < {alpha}).")
    print("      Developer experience significantly impacts AI-agent usage frequency.\n")

    bonf_alpha = alpha / 3

    pairs = [
        ('Senior', 'Junior', seniors, juniors),
        ('Senior', 'Mid', seniors, mids),
        ('Mid', 'Junior', mids, juniors)
    ]

    for g1, g2, d1, d2 in pairs:
        u_stat, p_val = stats.mannwhitneyu(d1, d2, alternative='two-sided')
        r_rb = rank_biserial(u_stat, len(d1), len(d2))
        print(f"   * Test {g1} vs {g2}: U={u_stat:.1f}, p-value={p_val:.4e}, rank-biserial r={r_rb:.4f}")
        if p_val < bonf_alpha:
            print(f"     -> CONCLUSION: Significant difference between {g1} and {g2}.")
        else:
            print(f"     -> CONCLUSION: No significant difference between {g1} and {g2}.")
else:
    print(f"   -> DECISION: Fail to reject H0 (p >= {alpha}).")
    print("      AI-agent usage frequency does not significantly differ by experience level.")
