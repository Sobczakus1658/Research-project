import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

def run_third_experiment():
    exp_df = pd.read_csv('../../data/third_experiment/data_to_third_experiment.csv')
    levels_df = pd.read_csv('../../data/prepare_data/user_experience_levels.csv')

    merged_df = pd.merge(
        exp_df, 
        levels_df, 
        left_on='real_human_author', 
        right_on='login', 
        how='inner'
    )

    level_order = ['Junior', 'Mid', 'Senior']

    summary_stats = merged_df.groupby('experience')['comments_by_human_maintainers'].agg(
        N='count',
        Mean='mean',
        SD='std',
        Mdn='median'
    ).reindex(level_order).dropna(how='all')

    print("==========================================================")
    print(" DESCRIPTIVE STATISTICS OF COMMENT COUNT PER EXPERIENCE   ")
    print("==========================================================")
    print(summary_stats.to_string())
    print("\n")

    summary_stats.to_csv('../../data/third_experiment/third_experiment_summary_stats.csv', index=False)
    
    stats_formatted = summary_stats.reset_index().rename(columns={'experience': 'Level'})
    stats_formatted['N'] = stats_formatted['N'].apply(lambda x: f"{int(x):,}")
    stats_formatted['Mean'] = stats_formatted['Mean'].map('{:.2f}'.format)
    stats_formatted['SD'] = stats_formatted['SD'].map('{:.2f}'.format)
    stats_formatted['Mdn'] = stats_formatted['Mdn'].map('{:.1f}'.format)

    fig, ax_table = plt.subplots(figsize=(5, 3))
    ax_table.axis('off')
    plt.title("Summary statistics", fontsize=12, fontweight='bold', pad=10)

    table = ax_table.table(
        cellText=stats_formatted.values,
        colLabels=stats_formatted.columns,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor('#1f3044')
            cell.get_text().set_color('white')
            cell.get_text().set_weight('bold')

    plt.tight_layout()
    table_path = '../../results/third_experiment_summary_table.png'
    plt.savefig(table_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Summary table saved to: {table_path}")

    juniors = merged_df[merged_df['experience'] == 'Junior']['comments_by_human_maintainers']
    mids = merged_df[merged_df['experience'] == 'Mid']['comments_by_human_maintainers']
    seniors = merged_df[merged_df['experience'] == 'Senior']['comments_by_human_maintainers']

    print("==========================================================")
    print("      STATISTICAL SIGNIFICANCE ANALYSIS                   ")
    print("==========================================================")

    def rank_biserial(u_stat, n1, n2):
        return 1 - (2 * u_stat) / (n1 * n2)

    kw_stat, kw_p = stats.kruskal(juniors, mids, seniors)
    n_total = len(juniors) + len(mids) + len(seniors)
    epsilon_sq = kw_stat / (n_total - 1)
    print(f"Kruskal-Wallis Test (for all 3 groups):")
    print(f"  H-statistic = {kw_stat:.4f}, p-value = {kw_p:.4e}, epsilon-squared = {epsilon_sq:.4f}")
    if kw_p < 0.05:
        print("  -> Result: There is a statistically significant difference between at least two groups (p < 0.05).\n")
    else:
        print("  -> Result: No grounds to reject the null hypothesis of no differences between groups (p >= 0.05).\n")

    print("Pairwise Mann-Whitney U Tests (group-to-group comparisons):")
    pairs = [
        ('Junior', 'Mid', juniors, mids),
        ('Junior', 'Senior', juniors, seniors),
        ('Mid', 'Senior', mids, seniors)
    ]

    for g1_name, g2_name, g1_data, g2_data in pairs:
        if len(g1_data) > 0 and len(g2_data) > 0:
            u_stat, p_val = stats.mannwhitneyu(g1_data, g2_data, alternative='two-sided')
            r_rb = rank_biserial(u_stat, len(g1_data), len(g2_data))
            print(f"  * {g1_name} vs {g2_name}: U = {u_stat:.1f}, p-value = {p_val:.4e}, rank-biserial r = {r_rb:.4f}")
            if p_val < 0.0167:
                print(f"    -> The difference between {g1_name} and {g2_name} is STATISTICALLY SIGNIFICANT.")
            else:
                print(f"    -> No statistically significant difference between {g1_name} and {g2_name}.")

    plt.figure(figsize=(9, 6))
    sns.boxplot(
        data=merged_df, 
        x='experience', 
        y='comments_by_human_maintainers', 
        hue='experience',
        legend=False,
        order=level_order,
        palette='Set2'
    )
    plt.yscale('log')
    plt.title('Number of Comments in Pull Requests by Experience Level')
    plt.xlabel('Experience Level')
    plt.ylabel('Number of Comments (Log Scale)')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    
    plot_path = '../../results/third_experiment_boxplot.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Boxplot figure saved to: {plot_path}")

if __name__ == '__main__':
    run_third_experiment()