import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

df = pd.read_csv('../../data/prepare_data/final_combined_data.csv')
df = df.dropna(subset=['login'])
df = df.fillna(0)

features = df.drop(columns=['login']).apply(pd.to_numeric, errors='coerce')
features = features.fillna(features.median())

features_log = np.log1p(features)
features_scaled = StandardScaler().fit_transform(features_log)

iso_forest = IsolationForest(contamination=0.01, random_state=42)
outlier_labels = iso_forest.fit_predict(features_scaled)
X = features_scaled[outlier_labels == 1]

print(f"Removed {(outlier_labels == -1).sum()} outliers via Isolation Forest; "
      f"{len(X)} profiles used for k diagnostics.")


def wk(X, k):
    km = KMeans(n_clusters=k, init='k-means++', random_state=42, n_init=10)
    labels = km.fit_predict(X)
    out = 0
    for i in np.unique(labels):
        c = X[labels == i]
        m = c.mean(axis=0)
        out += np.sum((c - m) ** 2)
    return out

def gap(X, k_range, B=10):
    gaps = []
    for k in k_range:
        wk_real = wk(X, k)
        mins = X.min(axis=0)
        maxs = X.max(axis=0)
        ref = []
        for _ in range(B):
            xr = np.random.uniform(mins, maxs, size=X.shape)
            ref.append(np.log(wk(xr, k)))
        gaps.append(np.mean(ref) - np.log(wk_real))
    return np.array(gaps)

k_range = range(2, 11)
gaps = gap(X, k_range)

sil = [
    silhouette_score(
        X,
        KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
    )
    for k in k_range
]

for k, s, g in zip(k_range, sil, gaps):
    print(f"k={k}: silhouette={s:.4f}, gap={g:.4f}")

plt.figure(figsize=(10, 5))
plt.plot(k_range, gaps, marker='o')
plt.title('Gap Statistic (log1p + Scaled, 12-D)')
plt.xlabel('k')
plt.ylabel('Gap')
plt.grid(True)
plt.tight_layout()
plt.savefig('../../results/gap_statistic_transformed.png', dpi=300)
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(k_range, sil, marker='o', color='green')
plt.title('Silhouette Score (log1p + Scaled, 12-D)')
plt.xlabel('k')
plt.ylabel('Score')
plt.grid(True)
plt.tight_layout()
plt.savefig('../../results/silhouette_score_transformed.png', dpi=300)
plt.show()
