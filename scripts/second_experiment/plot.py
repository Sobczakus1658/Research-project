import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('../../data/second_experiment/second_experiment_merged.csv')

level_order = ['Junior', 'Mid', 'Senior']

stats_df = df.groupby('experience')['acceptance_rate'].agg(
    N='count',
    Mean='mean',
    SD='std',
    Mdn='median'
).reindex(level_order).dropna(how='all').reset_index()

stats_df.rename(columns={'experience': 'Level'}, inplace=True)

stats_formatted = stats_df.copy()
stats_formatted['N'] = stats_formatted['N'].apply(lambda x: f"{int(x):,}")
stats_formatted['Mean'] = stats_formatted['Mean'].map('{:.2f}'.format)
stats_formatted['SD'] = stats_formatted['SD'].map('{:.2f}'.format)
stats_formatted['Mdn'] = stats_formatted['Mdn'].map('{:.2f}'.format)

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

output_path = '../../results/second_experiment_summary_table.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()