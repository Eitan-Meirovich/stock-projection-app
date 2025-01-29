import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def normalize_proportions(series):
    """
    Normaliza una serie asegurando que sume 1
    """
    return series / series.sum() if series.sum() > 0 else series

def distribute_forecast(total_forecast, proportions):
    """
    Distribuye el pronóstico total según las proporciones
    asegurando que la suma sea igual al total
    """
    distributed = total_forecast * proportions
    # Ajustar por redondeo
    adjustment = total_forecast - distributed.sum()
    distributed.iloc[0] += adjustment
    return distributed

# Configuración de rutas
base_dir = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data'
forecast_dir = os.path.join(base_dir,'processed', 'Invierno')
file_path = os.path.join(base_dir,'Input', 'Invierno.xlsx')
forecast_path = 'Proyección_15MM_Invierno.csv'

# Cargar datos
print("Cargando datos...")
data = pd.read_excel(file_path)
data['Date'] = pd.to_datetime(data['Date'])

# Cargar pronósticos SARIMA
forecast_df = pd.read_csv(os.path.join(forecast_dir, forecast_path))

# Convertir fechas
data['Month'] = data['Date'].dt.to_period('M')
forecast_df['Month'] = pd.to_datetime(forecast_df['Date']).dt.to_period('M')

# Pronósticos de super familia
super_family_forecast = forecast_df.rename(columns={'Forecast_Sales': 'Forecast_SuperFamily'})[['Month', 'Forecast_SuperFamily']]

# Calcular proporciones históricas por familia
print("Calculando proporciones...")
family_props = data.groupby('Familia')['Sales'].sum()
family_props = normalize_proportions(family_props)

# Distribuir hacia familias
print("Distribuyendo hacia familias...")
family_forecast = []
for _, row in super_family_forecast.iterrows():
    forecast_value = row['Forecast_SuperFamily']
    family_values = distribute_forecast(forecast_value, family_props)
    
    for familia, forecast in family_values.items():
        family_forecast.append({
            'Month': row['Month'],
            'Familia': familia,
            'Forecast_Family': forecast
        })

family_forecast_df = pd.DataFrame(family_forecast)

# Calcular proporciones por producto dentro de cada familia
print("Calculando proporciones por producto...")
product_props = data.groupby(['Familia', 'Codigo Producto'])['Sales'].sum()
product_props = product_props.groupby('Familia').transform(normalize_proportions)

# Distribuir hacia productos
print("Distribuyendo hacia productos...")
product_forecast = []
for _, row in family_forecast_df.iterrows():
    familia = row['Familia']
    forecast_value = row['Forecast_Family']
    
    if familia in product_props.index.get_level_values(0):
        products = product_props.loc[familia]
        product_values = distribute_forecast(forecast_value, products)
        
        for product_code, forecast in product_values.items():
            product_forecast.append({
                'Month': row['Month'],
                'Familia': familia,
                'Product_Code': product_code,
                'Forecast_Product': forecast
            })

product_forecast_df = pd.DataFrame(product_forecast)

# Validaciones
print("\nValidación de sumas totales:")
total_super = super_family_forecast['Forecast_SuperFamily'].sum()
total_family = family_forecast_df['Forecast_Family'].sum()
total_product = product_forecast_df['Forecast_Product'].sum()

print(f"Suma total super familia: {total_super:,.2f}")
print(f"Suma total familias: {total_family:,.2f}")
print(f"Suma total productos: {total_product:,.2f}")

# Verificar coherencia por mes
print("\nVerificación de coherencia entre niveles:")
for month in product_forecast_df['Month'].unique():
    super_total = super_family_forecast[super_family_forecast['Month'] == month]['Forecast_SuperFamily'].iloc[0]
    family_total = family_forecast_df[family_forecast_df['Month'] == month]['Forecast_Family'].sum()
    product_total = product_forecast_df[product_forecast_df['Month'] == month]['Forecast_Product'].sum()
    
    print(f"\nMes {month}:")
    print(f"Diferencia Super-Familia: {((family_total - super_total) / super_total * 100):.2f}%")
    print(f"Diferencia Familia-Producto: {((product_total - family_total) / family_total * 100):.2f}%")

# Visualizaciones
print("\nGenerando visualizaciones...")
# Por familia
family_props_df = pd.DataFrame({
    'Familia': family_forecast_df['Familia'],
    'proportion': family_forecast_df['Forecast_Family'] / 
                 family_forecast_df.groupby('Month')['Forecast_Family'].transform('sum')
})

plt.figure(figsize=(15, 7))
sns.boxplot(data=family_props_df, x='Familia', y='proportion')
plt.title('Distribución de Proporciones por Familia')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Por producto
product_props_df = pd.DataFrame({
    'Familia': product_forecast_df['Familia'],
    'proportion': product_forecast_df['Forecast_Product'] / 
                 product_forecast_df.groupby(['Month', 'Familia'])['Forecast_Product'].transform('sum')
})

plt.figure(figsize=(15, 7))
sns.boxplot(data=product_props_df, x='Familia', y='proportion')
plt.title('Distribución de Proporciones por Producto')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Guardar resultados
print("\nGuardando resultados...")
family_forecast_df.to_csv(os.path.join(forecast_dir, 'forecast_family_invierno.csv'), index=False)
product_forecast_df.to_csv(os.path.join(forecast_dir, 'forecast_product_invierno.csv'), index=False)

validation_df = pd.DataFrame({
    'Nivel': ['Super Familia', 'Familia', 'Producto'],
    'Total': [total_super, total_family, total_product],
    'Diferencia_%': [0, ((total_family - total_super)/total_super)*100, 
                    ((total_product - total_super)/total_super)*100]
})
validation_df.to_csv(os.path.join(forecast_dir, 'forecast_validation_fixed.csv'), index=False)

print("\nProceso completado. Archivos guardados:")
print("- forecast_family_invierno.csv")
print("- forecast_product_invierno.csv")
print("- forecast_validation_fixed.csv")