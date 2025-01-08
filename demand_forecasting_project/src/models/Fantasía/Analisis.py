import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos de la Super Familia "Bebé"
file_path = 'data/processed/processed_data_fantasia.csv'  # Ajusta el nombre del archivo

data = pd.read_csv(file_path)

# Convertir la columna de fechas al formato datetime
data['Date'] = pd.to_datetime(data['Date'])

# Verificar el rango de fechas disponibles
print("Datos disponibles desde:", data['Date'].min(), "hasta:", data['Date'].max())

# Agrupar las ventas mensuales
monthly_sales = data.groupby(data['Date'].dt.to_period('M'))['Sales'].sum().reset_index()
monthly_sales['Date'] = monthly_sales['Date'].dt.to_timestamp()

# Graficar las ventas mensuales
plt.figure(figsize=(12, 6))
plt.plot(monthly_sales['Date'], monthly_sales['Sales'], marker='o')
plt.title('Ventas Mensuales - Super Familia "Bebé"')
plt.xlabel('Fecha')
plt.ylabel('Ventas Totales')
plt.grid()
plt.show()

# Graficar el promedio de ventas por mes
monthly_sales['Month'] = monthly_sales['Date'].dt.month
avg_sales_by_month = monthly_sales.groupby('Month')['Sales'].mean()

plt.figure(figsize=(12, 6))
avg_sales_by_month.plot(kind='bar', color='skyblue', alpha=0.7)
plt.title('Promedio de Ventas Mensuales - Super Familia "Bebé"')
plt.xlabel('Mes')
plt.ylabel('Ventas Promedio')
plt.grid()
plt.show()

# Guardar resumen para referencias posteriores
monthly_sales.to_csv('data/processed/summary_bebe_sales.csv', index=False)
print("Resumen de ventas mensuales guardado en 'summary_bebe_sales.csv'.")
