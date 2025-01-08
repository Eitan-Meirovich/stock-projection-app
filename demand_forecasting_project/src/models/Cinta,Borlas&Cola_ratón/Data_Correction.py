# Importar librerías necesarias
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

# ----------------------------
# 1. Cargar y Preparar Datos
# ----------------------------
# Cargar el archivo CSV
file_path = 'data/processed/processed_data_cintas, borlas & cola raton.csv'
cintas_data = pd.read_csv(file_path)

# Paso 2: Limpieza de datos
columns_to_drop = ['Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16']
cintas_data_cleaned = cintas_data.drop(columns=columns_to_drop)
cintas_data_cleaned['Date'] = pd.to_datetime(cintas_data_cleaned['Date'])

# Paso 3: Identificación de quiebres de stock
product_sales_stats = cintas_data_cleaned.groupby('Product_Code')['Sales'].agg(['mean', 'std']).reset_index()
product_sales_stats.columns = ['Product_Code', 'Mean_Sales', 'Std_Sales']
cintas_data_with_stats = pd.merge(cintas_data_cleaned, product_sales_stats, on='Product_Code', how='left')
threshold_factor = 0.2  # Definir el factor para identificar quiebres
cintas_data_with_stats['Stock_Out'] = cintas_data_with_stats['Sales'] < cintas_data_with_stats['Mean_Sales'] * threshold_factor

# Paso 4: Ajustar ventas en períodos de quiebre
adjusted_data = cintas_data_with_stats.copy()
adjusted_data['Sales_Adjusted'] = adjusted_data['Sales']
adjusted_data.loc[adjusted_data['Stock_Out'], 'Sales_Adjusted'] = None
adjusted_data['Sales_Adjusted'] = adjusted_data.groupby('Product_Code')['Sales_Adjusted'].transform(lambda x: x.interpolate(method='linear'))

# Paso 5: Análisis de tendencia y estacionalidad
adjusted_monthly_sales = adjusted_data.groupby(['Year', 'Month'])['Sales_Adjusted'].sum().reset_index()
adjusted_monthly_sales['Date'] = pd.to_datetime(adjusted_monthly_sales[['Year', 'Month']].assign(Day=1))
adjusted_monthly_sales = adjusted_monthly_sales.set_index('Date')

# Descomposición de la serie temporal
decomposition = seasonal_decompose(adjusted_monthly_sales['Sales_Adjusted'], model='additive', period=12)
plt.figure(figsize=(10, 8))
decomposition.plot()
plt.suptitle('Descomposición de la Serie Temporal - Ventas Ajustadas', fontsize=14)
plt.tight_layout()
plt.show()

# Paso 6: Visualización de comparación de ventas originales vs ajustadas
monthly_sales = cintas_data_cleaned.groupby(['Year', 'Month'])['Sales'].sum().reset_index()
monthly_sales['Date'] = pd.to_datetime(monthly_sales[['Year', 'Month']].assign(Day=1))
monthly_sales = monthly_sales.set_index('Date')

plt.figure(figsize=(12, 6))
plt.plot(monthly_sales.index, monthly_sales['Sales'], label='Ventas Originales', marker='o')
plt.plot(adjusted_monthly_sales.index, adjusted_monthly_sales['Sales_Adjusted'], label='Ventas Ajustadas', linestyle='--', marker='o')
plt.title('Comparación de Ventas - Originales vs Ajustadas', fontsize=14)
plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Ventas Totales', fontsize=12)
plt.legend()
plt.grid(True)
plt.show()

# Guardar los datos ajustados para uso posterior
adjusted_data.to_csv('data/processed/Cintas_Borlas_Cola_Raton/adjusted_data_cintas_borlas_colaraton.csv', index=False)