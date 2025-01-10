import pandas as pd

# Rutas de los archivos de entrada
stock_path = 'Stock_Optimization/Data/stock_data.csv'  # Cambia a la ruta correcta de tu archivo
forecast_path = 'Data/consolidated_forecast.csv'  # Cambia a la ruta correcta de tu archivo
combined_data_path = 'Data/combined_stock_forecast.csv'  # Archivo combinado existente

# Cargar los datos
stock_data = pd.read_csv(stock_path)
forecast_data = pd.read_csv(forecast_path)
combined_data = pd.read_csv(combined_data_path)

# Combinar los datasets usando la columna 'Product_Code'
combined_data = pd.merge(stock_data, forecast_data, on='Product_Code', how='inner')

# Calcular la proyección acumulada directamente desde 'Forecast_Product'
combined_data['Total_Projection'] = combined_data['Forecast_Product']

# Calcular el stock restante después de considerar la proyección
if 'Stock' in combined_data.columns:
    combined_data['Stock_After_Consumption'] = combined_data['Stock'] - combined_data['Total_Projection']
else:
    combined_data['Stock_After_Consumption'] = None

# Crear la columna 'Fecha' asumiendo datos mensuales
if 'Month' in combined_data.columns and 'Year' in combined_data.columns:
    # Formatear la fecha como "01-Mes-Año"
    combined_data['Fecha'] = combined_data['Year'].astype(str) + '-' + combined_data['Month'].astype(str).str.zfill(2) + '-01'
else:
    # Si no existen columnas 'Year' y 'Month', asumir columnas base para generar fechas (ajustar según contexto)
    combined_data['Fecha'] = '2025-01-01'  # Por defecto, asignar una fecha estática si no hay base

# Guardar los resultados en un archivo CSV
output_path = 'Data/combined_with_generated_date.csv'  # Cambia a la ruta deseada
combined_data.to_csv(output_path, index=False)

print(f"Archivo procesado y guardado en: {output_path}")
