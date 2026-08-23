import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

df = pd.read_csv('../../data/prepare_data/final_combined_data.csv')
df = df.dropna(subset=['login'])
df = df.fillna(0)

logins = df['login']
features = df.drop(columns=['login'])

features_log = np.log1p(features)

iso_forest = IsolationForest(contamination=0.01, random_state=42)
outlier_labels = iso_forest.fit_predict(features_log)

features_clean = features_log[outlier_labels == 1]
logins_clean = logins[outlier_labels == 1]

scaler = StandardScaler()
data_scaled = scaler.fit_transform(features_clean)

pca = PCA(n_components=2)
data_pca = pca.fit_transform(data_scaled)

df_final = pd.DataFrame(
    data_pca, 
    columns=['Principal_Component_1', 'Principal_Component_2']
)
df_final['login'] = logins_clean.values
df_final.to_csv('../../data/prepare_data/preprocessed_data.csv', index=False)

loadings = pd.DataFrame(
    pca.components_.T, 
    columns=['PC1', 'PC2'], 
    index=features_clean.columns
)

plt.figure(figsize=(10, 6))

loadings_pc1 = loadings['PC1'].sort_values()
loadings_pc1.plot(kind='barh', color='skyblue', edgecolor='black')

plt.title('Variable Influence on Principal Component 1 (PC1)', fontsize=13, fontweight='bold')
plt.xlabel('Weight (Loading)', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.4)

plt.tight_layout()
plt.savefig('../../results/pca_pc1.png', dpi=300)
print("Saved: ../../results/pca_pc1.png")
plt.show()


plt.figure(figsize=(10, 6))

loadings_pc2 = loadings['PC2'].sort_values()
loadings_pc2.plot(kind='barh', color='salmon', edgecolor='black')

plt.title('Variable Influence on Principal Component 2 (PC2)', fontsize=13, fontweight='bold')
plt.xlabel('Weight (Loading)', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.4)

plt.tight_layout()
plt.savefig('../../results/pca_pc2.png', dpi=300)
print("Saved: ../../results/pca_pc2.png")
plt.show()