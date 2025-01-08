import pandas as pd

# Cargar los datos clusterizados
file_path = 'data/processed/clustered_data.csv'
data = pd.read_csv(file_path)

# Calcular estadísticas descriptivas por cluster
cluster_stats = data.groupby('Cluster').agg({
    'Sales': ['mean', 'median', 'std', 'sum'],
    'Year': ['min', 'max'],
    'Month': ['min', 'max']
})

print("Estadísticas Descriptivas por Cluster:")
print(cluster_stats)
