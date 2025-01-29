import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
from datetime import datetime, date
import os

# Obtener la fecha actual
current_date = datetime.now()

# Calcular el inicio del período de entrenamiento (1 de enero 2024)
train_start = pd.Timestamp('2024-01-01')

# Calcular el inicio y fin del período de pronóstico
forecast_start = pd.Timestamp(current_date.year, current_date.month, 1) + pd.DateOffset(months=1)
forecast_periods = 15  # 15 meses móviles


# Cargar datos históricos de la Super Familia "Hilos Verano"
file_path =file_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\processed_data_hilos verano.csv'

data = pd.read_csv(file_path)
data['Date'] = pd.to_datetime(data['Date'])
print(f"Datos disponibles desde: {data['Date'].min()} hasta: {data['Date'].max()}")
print(f"Período de entrenamiento: {train_start} hasta: {current_date.strftime('%Y-%m-%d')}")
print(f"Período de pronóstico: {forecast_start.strftime('%Y-%m')} hasta: {(forecast_start + pd.DateOffset(months=forecast_periods-1)).strftime('%Y-%m')}")


# Filtrar datos de entrenamiento
train_data = data[data['Date'] >= train_start]
monthly_sales = train_data.groupby(train_data['Date'].dt.to_period('M'))['Sales'].sum().reset_index()
monthly_sales['Date'] = monthly_sales['Date'].dt.to_timestamp()
monthly_sales.set_index('Date', inplace=True)



# Ajustar modelo de Suavizamiento Exponencial Holt-Winters (ETS)
print("Entrenando el modelo de Suavizamiento Exponencial Holt-Winters...")
model = ExponentialSmoothing(monthly_sales['Sales'], 
                             trend='add',       # Capturar tendencia aditiva
                             seasonal='add',    # Capturar estacionalidad aditiva
                             seasonal_periods=12)  # Periodo estacional de 12 meses
ets_result = model.fit()
print("Modelo entrenado.")

# Generar predicciones para todo el año 2025
forecast_steps = forecast_periods  # 12 meses + 3 meses de proyección
forecast_index = pd.date_range(start=forecast_start, periods=forecast_periods, freq='M'),
forecast_values = ets_result.forecast(steps=forecast_steps)

# Crear DataFrame de predicciones
forecast_df = pd.DataFrame({
    'Date': forecast_index,
    'Forecast_Sales': forecast_values.values
})
forecast_df['Date'] = forecast_df['Date'].dt.to_period('M').dt.to_timestamp('D')  # Primer día del mes

# Calcular intervalos de confianza
std_error = np.std(ets_result.resid)
forecast_df['Lower_Bound'] = forecast_df['Forecast_Sales'] - 1.96 * std_error
forecast_df['Upper_Bound'] = forecast_df['Forecast_Sales'] + 1.96 * std_error

output_dir=r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Verano'
output_file = 'Proyeccion_15MM_Verano.csv'

# Guardar proyecciones para 2025
forecast_df.to_csv(os.path.join(output_dir, output_file), index=False)
print(f"Proyecciones guardadas en '{os.path.join(output_dir, output_file)}'.")

# Imprimir las proyecciones
print("\nProyecciones mensuales:")
print(forecast_df.to_string(index=False))