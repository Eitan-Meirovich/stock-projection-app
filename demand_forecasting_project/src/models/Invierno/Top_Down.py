import pandas as pd

# Cargar datos históricos de la Super Familia "Invierno"
file_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\processed_data_invierno.csv'
data = pd.read_csv(file_path)

# Cargar las proyecciones guardadas del modelo SARIMA
forecast_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Invierno\2025_forecast_Invierno.csv'
forecast_df = pd.read_csv(forecast_path)

# Convertir fechas a Period (mes) y preparar datos
data['Date'] = pd.to_datetime(data['Date'])
data['Month'] = data['Date'].dt.to_period('M')
forecast_df['Month'] = pd.to_datetime(forecast_df['Date']).dt.to_period('M')

# Proyecciones reales de nivel Super Familia
super_family_forecast = forecast_df.rename(columns={'Forecast_Sales': 'Forecast_SuperFamily'})[['Month', 'Forecast_SuperFamily']]

# Calcular proporciones históricas de Familias
family_proportions = data.groupby('Familia')['Sales'].sum()
family_proportions /= family_proportions.sum()

# Distribuir predicciones hacia Familias
family_forecast = []
for _, row in super_family_forecast.iterrows():
    for family, proportion in family_proportions.items():
        family_forecast.append({
            'Month': row['Month'], 
            'Familia': family, 
            'Forecast_Family': row['Forecast_SuperFamily'] * proportion
        })

family_forecast_df = pd.DataFrame(family_forecast)

# Calcular proporciones de Productos dentro de Familias
product_proportions = data.groupby(['Familia', 'Product_Code'])['Sales'].sum()
product_proportions /= product_proportions.groupby(level=0).transform('sum')

# Distribuir predicciones hacia Productos
product_forecast = []
for _, row in family_forecast_df.iterrows():
    familia = row['Familia']
    forecast = row['Forecast_Family']
    products = product_proportions.loc[familia]
    for product_code, proportion in products.items():
        product_forecast.append({
            'Month': row['Month'], 
            'Familia': familia, 
            'Product_Code': product_code, 
            'Forecast_Product': forecast * proportion
        })

product_forecast_df = pd.DataFrame(product_forecast)

# Guardar resultados
family_forecast_df.to_csv(r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Invierno\forecast_family_invierno.csv', index=False)
product_forecast_df.to_csv(r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Invierno\forecast_product_invierno.csv', index=False)

print("Proyección por Familia guardada en 'forecast_family_invierno.csv'")
print("Proyección por Producto guardada en 'forecast_product_invierno.csv'")

# Mostrar resultados
print("Proyección por Familia:")
print(family_forecast_df.head())
print("\nProyección por Producto:")
print(product_forecast_df.head())
