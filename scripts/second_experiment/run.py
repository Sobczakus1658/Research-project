import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

def run_second_experiment():
    
    mr_df = pd.read_csv(
        '../../data/second_experiment/ratio_merge_requests_all.csv',
        header=None,
        names=['login', 'total_mr', 'accepted_mr', 'rejected_mr', 'acceptance_rate']
    )
    
    mr_df['acceptance_rate'] = pd.to_numeric(mr_df['acceptance_rate'], errors='coerce')
    mr_df['total_mr'] = pd.to_numeric(mr_df['total_mr'], errors='coerce')

    levels_df = pd.read_csv('../../data/prepare_data/user_experience_levels.csv')

    merged_df = pd.merge(mr_df, levels_df, on='login', how='inner')
    merged_df.to_csv('../../data/second_experiment/second_experiment_merged.csv', index=False)

    def iqr(x):
        return x.quantile(0.75) - x.quantile(0.25)

    summary_stats = merged_df.groupby('experience')['acceptance_rate'].agg(
        User_Count=('count'),
        Mean=('mean'),
        Std_Dev=('std'),
        Median=('median'),
        IQR=(iqr),
        Min=('min'),
        Max=('max')
    ).reindex(['Junior', 'Mid', 'Senior']).dropna(how='all')

    print("==========================================================")
    print("      ACCEPTANCE RATE (%) SUMMARY STATS PER EXPERIENCE     ")
    print("==========================================================")
    print(summary_stats.to_string())
    print("\n")

    summary_stats.to_csv('../../data/second_experiment/second_experiment_summary_stats.csv')

    def rank_biserial(u_stat, n1, n2):
        return 1 - (2 * u_stat) / (n1 * n2)

    juniors = merged_df[merged_df['experience'] == 'Junior']['acceptance_rate'].dropna()
    mids = merged_df[merged_df['experience'] == 'Mid']['acceptance_rate'].dropna()
    seniors = merged_df[merged_df['experience'] == 'Senior']['acceptance_rate'].dropna()

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
        print("      Developer experience significantly impacts code acceptance rate.\n")
        
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
                print(f"     -> CONCLUSION: Significant difference in acceptance rate between {g1} and {g2}.")
            else:
                print(f"     -> CONCLUSION: No significant difference between {g1} and {g2}.")
    else:
        print(f"   -> DECISION: Fail to reject H0 (p >= {alpha}).")
        print("      Code acceptance rate does not significantly differ by experience level.")

    plt.figure(figsize=(9, 6))
    sns.boxplot(
        data=merged_df, 
        x='experience', 
        y='acceptance_rate', 
        order=['Junior', 'Mid', 'Senior'],
        palette='Set3'
    )
    plt.title('Code Acceptance Rate (%) by Experience Level')
    plt.xlabel('Author Experience Level')
    plt.ylabel('Acceptance Rate (%)')
    plt.grid(True, ls="--", alpha=0.5)
    
    plot_path = '../../results/second_experiment_boxplot.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\nBoxplot saved to: {plot_path}")

if __name__ == '__main__':
    run_second_experiment()