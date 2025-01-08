import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

# Cargar datos procesados
file_path = 'data/processed/processed_data.csv'
data = pd.read_csv(file_path)

# Agrupar ventas por Familia
family_data = data.groupby(['Familia', 'Year', 'Month']).agg({'Sales': 'sum'}).reset_index()

# Crear características para clustering
family_summary = family_data.groupby('Familia').agg({
    'Sales': ['mean', 'median', 'std', 'sum'],
    'Year': ['min', 'max'],
    'Month': ['min', 'max']
}).reset_index()

# Preparar datos para clustering
family_summary.columns = ['Familia', 'Sales_Mean', 'Sales_Median', 'Sales_STD', 
                          'Sales_Sum', 'Year_Min', 'Year_Max', 'Month_Min', 'Month_Max']
features = family_summary[['Sales_Mean', 'Sales_STD', 'Sales_Sum']]

# Normalizar características
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Método del codo y Silhouette Score
distortions = []
silhouette_scores = []
K = range(2, 10)

for k in K:
    kmeans = KMeans(n_clusters=k, random_state=42)
    clusters = kmeans.fit_predict(features_scaled)
    distortions.append(kmeans.inertia_)
    sil_score = silhouette_score(features_scaled, clusters)
    silhouette_scores.append(sil_score)

# Graficar el método del codo y Silhouette Score
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(K, distortions, 'bo-')
plt.title("Elbow Method for Optimal Clusters")
plt.xlabel("Number of Clusters")
plt.ylabel("Distortion")

plt.subplot(1, 2, 2)
plt.plot(K, silhouette_scores, 'go-')
plt.title("Silhouette Score for Different Clusters")
plt.xlabel("Number of Clusters")
plt.ylabel("Silhouette Score")

plt.tight_layout()
plt.show()

# Entrenar KMeans con el número óptimo de clusters (ajusta manualmente si es necesario)
n_clusters = 4  # Ajustar basado en la gráfica
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
family_summary['Cluster'] = kmeans.fit_predict(features_scaled)

# Guardar resultados
output_file_path = 'data/processed/clustering_by_family.csv'
family_summary.to_csv(output_file_path, index=False)
print(f"Clustering por Familia guardado en: {output_file_path}")
