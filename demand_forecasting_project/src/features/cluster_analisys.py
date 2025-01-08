import pandas as pd

# Cargar el archivo de datos clusterizados
file_path = 'data/processed/clustered_data.csv'
clustered_data = pd.read_csv(file_path)

# Analizar la distribución de clusters
cluster_distribution = clustered_data['Cluster'].value_counts()
print("Cluster Distribution:\n", cluster_distribution)

# Calcular estadísticas descriptivas por cluster
cluster_stats = clustered_data.groupby('Cluster').agg({
    'Sales': ['mean', 'median', 'std', 'sum'],
    'Year': ['min', 'max'],
    'Month': ['min', 'max']
})
print("Cluster Statistics:\n", cluster_stats)

import matplotlib.pyplot as plt
import seaborn as sns

# Configurar estilo para gráficos
sns.set(style="whitegrid")

# Crear un gráfico de dispersión para visualizar los clusters
plt.figure(figsize=(10, 6))
sns.scatterplot(
    x=clustered_data['Month'], 
    y=clustered_data['Sales'], 
    hue=clustered_data['Cluster'], 
    palette='viridis', 
    alpha=0.7
)

plt.title("Cluster Visualization: Sales vs Month", fontsize=16)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Sales", fontsize=12)
plt.legend(title="Cluster")
plt.show()

# Agrupación por Cluster y Producto
cluster_product_stats = clustered_data.groupby(['Cluster', 'Product_Code']).agg({
    'Sales': ['mean', 'sum', 'std'],
    'Month': ['count', 'nunique']
}).reset_index()

# Renombrar columnas para claridad
cluster_product_stats.columns = [
    'Cluster', 'Product_Code', 'Sales_Mean', 'Sales_Sum', 
    'Sales_STD', 'Month_Count', 'Unique_Months'
]

print(cluster_product_stats)

import matplotlib.pyplot as plt
import seaborn as sns

# Gráfico de barras: Total de ventas por cluster
cluster_totals = clustered_data.groupby('Cluster')['Sales'].sum().reset_index()

plt.figure(figsize=(8, 5))
sns.barplot(x='Cluster', y='Sales', data=cluster_totals, palette='viridis')
plt.title("Total Sales by Cluster", fontsize=16)
plt.xlabel("Cluster", fontsize=12)
plt.ylabel("Total Sales", fontsize=12)
plt.show()

# Gráfico de línea: Distribución de ventas por mes y cluster
monthly_sales = clustered_data.groupby(['Month', 'Cluster'])['Sales'].sum().reset_index()

plt.figure(figsize=(10, 6))
sns.lineplot(
    x='Month', y='Sales', hue='Cluster', data=monthly_sales, 
    palette='viridis', marker='o'
)
plt.title("Monthly Sales by Cluster", fontsize=16)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Sales", fontsize=12)
plt.legend(title="Cluster")
plt.show()
