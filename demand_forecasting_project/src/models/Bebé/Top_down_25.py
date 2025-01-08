import pandas as pd

# Cargar las proyecciones SARIMA (corregidas al primer día del mes)
forecast_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Bebé\2025_forecast_Bebe.csv'  # Ruta del archivo generado
forecast_df = pd.read_csv(forecast_path)

# Convertir fechas a formato datetime y periodos mensuales
forecast_df['Date'] = pd.to_datetime(forecast_df['Date'])
forecast_df['Month'] = forecast_df['Date'].dt.to_period('M')

# Cargar datos históricos para calcular proporciones
file_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\processed_data_bebé.csv'
data = pd.read_csv(file_path)
data['Date'] = pd.to_datetime(data['Date'])
data['Month'] = data['Date'].dt.to_period('M')

# Calcular proporciones históricas de Familias
family_proportions = data.groupby('Familia')['Sales'].sum()
family_proportions /= family_proportions.sum()  # Normalizar a proporciones

# Distribuir las proyecciones de Super Familia hacia Familias
family_forecast = []
for _, row in forecast_df.iterrows():
    for family, proportion in family_proportions.items():
        family_forecast.append({
            'Month': row['Month'], 
            'Familia': family, 
            'Forecast_Family': row['Forecast_Sales'] * proportion
        })

family_forecast_df = pd.DataFrame(family_forecast)

# Calcular proporciones de Productos dentro de Familias
product_proportions = data.groupby(['Familia', 'Product_Code'])['Sales'].sum()
product_proportions /= product_proportions.groupby(level=0).transform('sum')

# Distribuir predicciones de Familias hacia Productos
product_forecast = []
for _, row in family_forecast_df.iterrows():
    familia = row['Familia']
    forecast = row['Forecast_Family']
    if familia in product_proportions.index:  # Verificar si la Familia tiene productos históricos
        products = product_proportions.loc[familia]
        for product_code, proportion in products.items():
            product_forecast.append({
                'Month': row['Month'], 
                'Familia': familia, 
                'Product_Code': product_code, 
                'Forecast_Product': forecast * proportion
            })
    else:  # Caso de Familia sin historial de productos
        product_forecast.append({
            'Month': row['Month'],
            'Familia': familia,
            'Product_Code': 'Sin_Historial',
            'Forecast_Product': forecast  # Asignar todo el pronóstico al producto genérico
        })

product_forecast_df = pd.DataFrame(product_forecast)

# Guardar resultados
family_forecast_df.to_csv(r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Bebé\forecast_family_2025.csv', index=False)
product_forecast_df.to_csv(r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Bebé\forecast_product_2025.csv', index=False)

# Mostrar resultados
print("Proyección por Familia (2024):")
print(family_forecast_df.head())

print("\nProyección por Producto (2024):")
print(product_forecast_df.head())
