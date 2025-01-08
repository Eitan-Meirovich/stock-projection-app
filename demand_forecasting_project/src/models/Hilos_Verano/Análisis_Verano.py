import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# **1. Cargar datos históricos de la Super Familia "Hilos Verano"**
file_path = 'data/processed/processed_data_hilos verano.csv'   # Ajusta la ruta
data = pd.read_csv(file_path)

# Preparar datos mensuales
data['Date'] = pd.to_datetime(data['Date'])
monthly_sales = data.groupby(data['Date'].dt.to_period('M'))['Sales'].sum().reset_index()
monthly_sales['Date'] = monthly_sales['Date'].dt.to_timestamp()
monthly_sales.set_index('Date', inplace=True)

# Visualizar ventas mensuales
plt.figure(figsize=(12, 6))
plt.plot(monthly_sales, marker='o')
plt.title('Ventas Mensuales - Super Familia "Verano"')
plt.xlabel('Fecha')
plt.ylabel('Ventas Totales')
plt.grid()
plt.show()

# Optimizar el modelo SARIMA con auto_arima
print("Buscando los mejores parámetros con auto_arima...")
auto_model = auto_arima(monthly_sales['Sales'], 
                        seasonal=True, m=12,  # Frecuencia estacional de 12 meses
                        trace=True, 
                        error_action='ignore', 
                        suppress_warnings=True, 
                        stepwise=True)

print("\nParámetros óptimos encontrados:")
print(auto_model.summary())

# Crear modelo SARIMA con los parámetros óptimos
best_order = auto_model.order
best_seasonal_order = auto_model.seasonal_order

sarima_model = SARIMAX(monthly_sales['Sales'], 
                       order=best_order, 
                       seasonal_order=best_seasonal_order, 
                       enforce_stationarity=False, 
                       enforce_invertibility=False)

# Entrenar el modelo
sarima_result = sarima_model.fit(disp=False)

# Pronóstico
forecast_steps = 12  # Predecir 12 meses hacia adelante
forecast = sarima_result.get_forecast(steps=forecast_steps)
forecast_index = pd.date_range(start=monthly_sales.index[-1], periods=forecast_steps+1, freq='M')[1:]

forecast_mean = forecast.predicted_mean
forecast_ci = forecast.conf_int()

# Graficar resultados
plt.figure(figsize=(12, 6))
plt.plot(monthly_sales, label='Ventas Observadas')
plt.plot(forecast_index, forecast_mean, color='red', label='Pronóstico SARIMA')
plt.fill_between(forecast_index, 
                 forecast_ci.iloc[:, 0], 
                 forecast_ci.iloc[:, 1], 
                 color='pink', alpha=0.3)
plt.title('Pronóstico Optimizado SARIMA - Super Familia "Verano"')
plt.xlabel('Fecha')
plt.ylabel('Ventas Totales')
plt.legend()
plt.grid()
plt.show()

# Evaluar modelo
y_true = monthly_sales['Sales'][-12:]  # Últimos 12 meses
y_pred = sarima_result.predict(start=len(monthly_sales)-12, end=len(monthly_sales)-1)
mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))

print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")

# Guardar las predicciones del modelo SARIMA
forecast_df = pd.DataFrame({
    'Date': forecast_index,
    'Forecast_Sales': forecast_mean.values
})

forecast_df.to_csv('data/processed/Verano/sarima_forecast_Verano.csv', index=False)
print("Proyecciones guardadas en 'sarima_forecast_Verano.csv'")