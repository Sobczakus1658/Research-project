import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('../../data/fourth_experiment/fourth_experiment_summary_stats.csv')

stats_formatted = df.copy()
stats_formatted['User_Count'] = stats_formatted['User_Count'].apply(lambda x: f"{int(x):,}")
for col in ['Mean', 'Std_Dev', 'Median', 'IQR', 'Min', 'Max']:
    stats_formatted[col] = stats_formatted[col].map('{:.2f}'.format)

fig, ax_table = plt.subplots(figsize=(8, 2.5))
ax_table.axis('off')
plt.title("RQ4 summary statistics: Agent vs Human PR acceptance rate (%)", fontsize=11, fontweight='bold', pad=10)

table = ax_table.table(
    cellText=stats_formatted.values,
    colLabels=stats_formatted.columns,
    cellLoc='center',
    loc='center'
)
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.1, 1.8)

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor('#1f3044')
        cell.get_text().set_color('white')
        cell.get_text().set_weight('bold')

plt.tight_layout()
table_path = '../../results/fourth_experiment_summary_table.png'
plt.savefig(table_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Summary table saved to: {table_path}")
