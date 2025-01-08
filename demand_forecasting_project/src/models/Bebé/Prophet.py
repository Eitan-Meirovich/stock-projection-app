import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
from prophet import Prophet

# Cargar datos
file_path = 'data/processed/processed_data_bebé.csv'
data = pd.read_csv(file_path)
data['Date'] = pd.to_datetime(data['Date'])
print("Datos disponibles desde:", data['Date'].min(), "hasta:", data['Date'].max())

# Filtrar datos hasta 2023
train_data = data[data['Date'] <= '2023-12-31']
monthly_sales = train_data.groupby(train_data['Date'].dt.to_period('M'))['Sales'].sum().reset_index()
monthly_sales['Date'] = monthly_sales['Date'].dt.to_timestamp()
monthly_sales.set_index('Date', inplace=True)

# Preparar datos para Prophet
prophet_data = monthly_sales.reset_index()[['Date', 'Sales']].rename(columns={'Date': 'ds', 'Sales': 'y'})
prophet_model = Prophet()
prophet_model.fit(prophet_data)

# Predicción con Prophet
prophet_future = prophet_model.make_future_dataframe(periods=12, freq='M')
prophet_forecast = prophet_model.predict(prophet_future)
prophet_forecast_2024 = prophet_forecast[prophet_forecast['ds'].dt.year == 2024]

prophet_forecast_df = pd.DataFrame({
    'Date': prophet_forecast_2024['ds'],
    'Forecast_Sales': prophet_forecast_2024['yhat'],
    'Lower_Bound': prophet_forecast_2024['yhat_lower'],
    'Upper_Bound': prophet_forecast_2024['yhat_upper']
})

# Comparar con datos reales
real_data_2024 = data[(data['Date'] >= '2024-01-01') & (data['Date'] <= '2024-12-31')]
real_monthly_sales = real_data_2024.groupby(real_data_2024['Date'].dt.to_period('M'))['Sales'].sum().reset_index()
real_monthly_sales['Date'] = real_monthly_sales['Date'].dt.to_timestamp()

# Asegurar alineación de datos
aligned_real_sales_length = min(len(real_monthly_sales), len(prophet_forecast_df))
aligned_real_sales = real_monthly_sales['Sales'].values[:aligned_real_sales_length]
aligned_prophet_forecast = prophet_forecast_df['Forecast_Sales'].values[:aligned_real_sales_length]

# Métricas
prophet_mae = mean_absolute_error(aligned_real_sales, aligned_prophet_forecast)
prophet_rmse = np.sqrt(mean_squared_error(aligned_real_sales, aligned_prophet_forecast))
print(f"Prophet -> MAE: {prophet_mae:.2f}, RMSE: {prophet_rmse:.2f}")

# Gráfico
plt.figure(figsize=(12, 6))
plt.plot(real_monthly_sales['Date'][:aligned_real_sales_length], aligned_real_sales, label='Ventas Reales', marker='o', color='blue')
plt.plot(prophet_forecast_df['Date'][:aligned_real_sales_length], aligned_prophet_forecast, label='Prophet', linestyle='--', color='green')
plt.fill_between(prophet_forecast_df['Date'][:aligned_real_sales_length], 
                 prophet_forecast_df['Lower_Bound'][:aligned_real_sales_length], 
                 prophet_forecast_df['Upper_Bound'][:aligned_real_sales_length], 
                 color='green', alpha=0.2)
plt.title('Modelo Prophet - Año 2024')
plt.xlabel('Fecha')
plt.ylabel('Ventas Totales')
plt.legend()
plt.grid()
plt.show()
