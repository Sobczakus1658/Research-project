import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

COLS = ['login', 'total_mr', 'accepted_mr', 'rejected_mr', 'acceptance_rate']


def run_fourth_experiment():
    agent_df = pd.read_csv(
        '../../data/second_experiment/ratio_merge_requests_all.csv',
        header=None, names=COLS
    )
    agent_df['acceptance_rate'] = pd.to_numeric(agent_df['acceptance_rate'], errors='coerce')
    agent_df['group'] = 'Agent'

    human_df = pd.read_csv(
        '../../data/fourth_experiment/human_pull_request_ratio.csv',
        header=None, names=COLS
    )
    human_df['acceptance_rate'] = pd.to_numeric(human_df['acceptance_rate'], errors='coerce')
    human_df['group'] = 'Human'

    merged_df = pd.concat([agent_df, human_df], ignore_index=True)
    merged_df.to_csv('../../data/fourth_experiment/fourth_experiment_merged.csv', index=False)

    def iqr(x):
        return x.quantile(0.75) - x.quantile(0.25)

    summary_stats = merged_df.groupby('group')['acceptance_rate'].agg(
        User_Count=('count'),
        Mean=('mean'),
        Std_Dev=('std'),
        Median=('median'),
        IQR=(iqr),
        Min=('min'),
        Max=('max')
    ).reindex(['Agent', 'Human'])

    print("==========================================================")
    print("  ACCEPTANCE RATE (%) SUMMARY STATS: AGENT vs HUMAN PRs    ")
    print("==========================================================")
    print(summary_stats.to_string())
    print("\n")

    summary_stats.to_csv('../../data/fourth_experiment/fourth_experiment_summary_stats.csv')

    agent_rates = merged_df[merged_df['group'] == 'Agent']['acceptance_rate'].dropna()
    human_rates = merged_df[merged_df['group'] == 'Human']['acceptance_rate'].dropna()

    print("==========================================================")
    print("       FORMAL STATISTICAL HYPOTHESIS TESTING              ")
    print("==========================================================")

    u_stat, p_val = stats.mannwhitneyu(agent_rates, human_rates, alternative='two-sided')
    n1, n2 = len(agent_rates), len(human_rates)
    r_rb = 1 - (2 * u_stat) / (n1 * n2)
    print(f"Mann-Whitney U (two-sided): U={u_stat:.1f}, p-value={p_val:.4e}, rank-biserial r={r_rb:.4f}")
    if p_val < 0.05:
        print("  -> Significant difference in acceptance rate between Agent-authored and Human-authored PRs.")
    else:
        print("  -> No significant difference between Agent-authored and Human-authored PRs.")

    plt.figure(figsize=(7, 6))
    sns.boxplot(
        data=merged_df,
        x='group',
        y='acceptance_rate',
        order=['Agent', 'Human'],
        palette='Set3'
    )
    plt.title('Pull-Request Acceptance Rate (%): Agent-authored vs Human-authored')
    plt.xlabel('Pull-request origin')
    plt.ylabel('Acceptance Rate (%)')
    plt.grid(True, ls="--", alpha=0.5)

    plot_path = '../../results/fourth_experiment_boxplot.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\nBoxplot saved to: {plot_path}")


if __name__ == '__main__':
    run_fourth_experiment()
