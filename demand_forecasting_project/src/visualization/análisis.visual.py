import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos
ventas_historicas = pd.read_csv('data/processed/ventas_historicas_por_familia.csv')
ventas_superfamilia = pd.read_csv('data/processed/ventas_por_super_familia.csv')

# Graficar ventas por familia
ventas_historicas.groupby('Familia')['Ventas Totales'].sum().plot(kind='bar', figsize=(12, 6))
plt.title('Ventas Totales por Familia')
plt.ylabel('Ventas Totales')
plt.show()

# Graficar ventas por superfamilia
ventas_superfamilia.groupby('Super Familia')['Ventas Totales'].sum().plot(kind='bar', figsize=(12, 6))
plt.title('Ventas Totales por Super Familia')
plt.ylabel('Ventas Totales')
plt.show()
