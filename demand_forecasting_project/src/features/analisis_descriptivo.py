import pandas as pd

# Cargar el archivo con las Familias y Clusters asignados
file_path = 'data/processed/clustering_by_family.csv'
family_clusters = pd.read_csv(file_path)

# Mostrar resumen de Familias por Cluster
family_count = family_clusters['Cluster'].value_counts().sort_index()
print("Número de Familias por Cluster:")
print(family_count)

# Mostrar estadísticas descriptivas por Cluster
cluster_stats = family_clusters.groupby('Cluster').agg({
    'Sales_Mean': ['mean', 'std'],
    'Sales_Sum': ['mean', 'sum'],
    'Sales_STD': ['mean', 'std']
})
print("\nEstadísticas descriptivas por Cluster:")
print(cluster_stats)

# Mostrar algunas Familias por Cluster
print("\nFamilias en cada Cluster:")
for cluster in sorted(family_clusters['Cluster'].unique()):
    familias = family_clusters[family_clusters['Cluster'] == cluster]['Familia'].tolist()
    print(f"Cluster {cluster}: {familias[:5]}...")  # Mostrar solo las primeras 5 Familias
