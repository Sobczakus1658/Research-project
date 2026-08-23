import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('../../data/first_experiment/experience_pull_request.csv')

level_order = ['Junior', 'Mid', 'Senior']

stats_df = df.groupby('experience')['pull_request'].agg(
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
stats_formatted['Mdn'] = stats_formatted['Mdn'].map('{:.1f}'.format)

sns.set_theme(style="whitegrid")
plt.figure(figsize=(6, 5))

palette = ['#3b528b', '#21918c', '#5ec962']

ax_box = sns.boxplot(
    data=df,
    x='experience',
    y='pull_request',
    hue='experience',
    legend=False,
    order=[lvl for lvl in level_order if lvl in df['experience'].unique()],
    palette=palette,
    showfliers=False,
    width=0.5
)

plt.title("AI Agent Usage Frequency by Experience Level", fontsize=11, fontweight='bold', pad=12)
plt.xlabel("Experience Level", fontsize=10, labelpad=8)
plt.ylabel("Frequency (Pull Requests)", fontsize=10, labelpad=8)

plt.tight_layout()
plt.savefig('../../results/boxplot.png', dpi=300, bbox_inches='tight')
plt.close()

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
plt.savefig('../../results/summary_table.png', dpi=300, bbox_inches='tight')
plt.close()