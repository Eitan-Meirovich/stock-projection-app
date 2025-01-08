import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Cargar datos
file_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\processed_data_invierno.csv'

data = pd.read_csv(file_path)
data['Date'] = pd.to_datetime(data['Date'])
print("Datos disponibles desde:", data['Date'].min(), "hasta:", data['Date'].max())

# Filtrar datos hasta 2023
train_data = data[data['Date'] <= '2024-12-31']
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

# --- Datos Reales 2024 ---
real_data_2024 = data[(data['Date'] >= '2024-01-01') & (data['Date'] <= '2024-12-31')]
real_monthly_sales = real_data_2024.groupby(real_data_2024['Date'].dt.to_period('M'))['Sales'].sum().reset_index()
real_monthly_sales['Date'] = real_monthly_sales['Date'].dt.to_timestamp()

# --- Combinar Modelos (Híbrido) ---
hybrid_forecast = 0.5 * hw_forecast.values + 0.5 * sarima_forecast_mean.values

# Asegurar alineación de datos
aligned_real_sales_length = min(len(real_monthly_sales), len(hybrid_forecast))
aligned_real_sales = real_monthly_sales['Sales'].values[:aligned_real_sales_length]
aligned_hybrid_forecast = hybrid_forecast[:aligned_real_sales_length]

# --- Métricas ---
hybrid_mae = mean_absolute_error(aligned_real_sales, aligned_hybrid_forecast)
hybrid_rmse = np.sqrt(mean_squared_error(aligned_real_sales, aligned_hybrid_forecast))
print(f"Modelo Híbrido -> MAE: {hybrid_mae:.2f}, RMSE: {hybrid_rmse:.2f}")


# Guardar el archivo
import os
output_dir = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Invierno'
output_file = '2025_forecast_Invierno.csv'

hybrid_forecast_df = pd.DataFrame({
    'Date': pd.date_range(start='2025-01-01', periods=len(hybrid_forecast), freq='M'),
    'Forecast_Sales': hybrid_forecast
})

# Guardar el archivo como CSV
hybrid_forecast_df.to_csv(os.path.join(output_dir, output_file), index=False)
print(f"Proyecciones guardadas en '{os.path.join(output_dir, output_file)}'.")