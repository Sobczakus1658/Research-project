import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

FILE_NAME = '../data/data_from_aidev.csv'

df = pd.read_csv(FILE_NAME)

exclude_cols = ['user_id', 'username', 'login', 'id']
features = [col for col in df.columns if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col])]
print(f"Features used for scoring: {features}")

# f(x) = min(4, max(0, 1 + 2 * (x - P50) / (P90 - P50)))
def calculate_feature_score(series):
    p50 = series.median()
    p90 = series.quantile(0.90)
    denominator = p90 - p50
    if denominator == 0:
        denominator = 1e-6
    
    raw_score = 1 + 2 * (series - p50) / denominator
    return np.clip(raw_score, 0, 4)

score_cols = []
for col in features:
    score_col_name = f'{col}_score'
    df[score_col_name] = calculate_feature_score(df[col])
    score_cols.append(score_col_name)

df['total_score'] = df[score_cols].sum(axis=1)

t33 = df['total_score'].quantile(0.3333)
t66 = df['total_score'].quantile(0.6666)

def classify(score):
    if score <= t33:
        return 'junior'
    elif score <= t66:
        return 'mid'
    else:
        return 'expert'

df['experience_level'] = df['total_score'].apply(classify)

fig, ax = plt.subplots(figsize=(10, 6))

color_jr = '#ff7f0e'
color_mid = '#1f77b4'
color_ex = '#2ca02c'

counts, bins, patches = ax.hist(
    df['total_score'], 
    bins=30, 
    edgecolor='black', 
    linewidth=0.6, 
    alpha=0.85
)

for patch in patches:
    bin_center = patch.get_x() + patch.get_width() / 2
    if bin_center <= t33:
        patch.set_facecolor(color_jr)
    elif bin_center <= t66:
        patch.set_facecolor(color_mid)
    else:
        patch.set_facecolor(color_ex)

legend_elements = [
    Patch(facecolor=color_jr, edgecolor='black', label=f'Junior (Score $\leq$ {t33:.2f})'),
    Patch(facecolor=color_mid, edgecolor='black', label=f'Mid ({t33:.2f} - {t66:.2f})'),
    Patch(facecolor=color_ex, edgecolor='black', label=f'Expert (> {t66:.2f})')
]

ax.legend(handles=legend_elements, title='Experience Level Regions', loc='upper right', fontsize=11, title_fontsize=12)
ax.set_title('Distribution of Total Score by Experience Groups', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Total Score', fontsize=12)
ax.set_ylabel('User Count', fontsize=12)
ax.grid(True, linestyle=':', alpha=0.5)

plt.tight_layout()

plt.savefig('../results/distribution_plot_clean.png', dpi=300)
print("Saved clean visualization to '../results/distribution_plot_clean.png'")