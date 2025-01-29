import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import datetime, date
import os

# Obtener la fecha actual
current_date = datetime.now()

# Calcular el inicio del período de entrenamiento (1 de enero 2024)
train_start = pd.Timestamp('2024-01-01')

# Calcular el inicio y fin del período de pronóstico
forecast_start = pd.Timestamp(current_date.year, current_date.month, 1) + pd.DateOffset(months=1)
forecast_periods = 15  # 15 meses móviles

# Cargar datos
file_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\processed_data_bebé.csv'

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

# --- Modelo Holt-Winters ---
print("Entrenando modelo Holt-Winters...")
hw_model = ExponentialSmoothing(monthly_sales['Sales'],
                                 seasonal='add',
                                 seasonal_periods=12,
                                 trend='add').fit()
hw_forecast = hw_model.forecast(steps=12)

# --- Modelo SARIMA ---
print("Entrenando modelo SARIMA...")
sarima_model = SARIMAX(monthly_sales['Sales'], 
                       order=(1, 1, 1), 
                       seasonal_order=(1, 1, 1, 12),
                       enforce_stationarity=False, 
                       enforce_invertibility=False).fit()
sarima_forecast = sarima_model.get_forecast(steps=12)
sarima_forecast_mean = sarima_forecast.predicted_mean

# --- Combinar Modelos (Híbrido) ---
# --- Combinar Modelos (Híbrido) ---
hybrid_forecast = 0.5 * hw_forecast.values + 0.5 * sarima_forecast_mean.values

# Crear DataFrame con las proyecciones
hybrid_forecast_df = pd.DataFrame({
    'Date': pd.date_range(start=forecast_start, periods=forecast_periods, freq='M'),
    'Forecast_Sales': hybrid_forecast
})

# Guardar el archivo como CSV
output_dir = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Bebé'
output_file = 'Proyeccion_15MM_Bebé.csv'
os.makedirs(output_dir, exist_ok=True)
# Guardar el archivo como CSV
hybrid_forecast_df.to_csv(os.path.join(output_dir, output_file), index=False)
print(f"Proyecciones guardadas en '{os.path.join(output_dir, output_file)}'.")

# Imprimir las proyecciones
print("\nProyecciones mensuales:")
print(hybrid_forecast_df.to_string(index=False))