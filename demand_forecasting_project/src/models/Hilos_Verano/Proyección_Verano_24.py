import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
from pmdarima import auto_arima

# Cargar datos históricos de la Super Familia "Invierno"
file_path = 'data/processed/processed_data_hilos verano.csv'
data = pd.read_csv(file_path)

# Preparar y verificar datos
data['Date'] = pd.to_datetime(data['Date'])
print("Datos disponibles desde:", data['Date'].min(), "hasta:", data['Date'].max())

# Filtrar los datos hasta el 31 de diciembre de 2023
train_data = data[data['Date'] <= '2023-12-31']

# Agrupar ventas mensuales para entrenamiento
monthly_sales = train_data.groupby(train_data['Date'].dt.to_period('M'))['Sales'].sum().reset_index()
monthly_sales['Date'] = monthly_sales['Date'].dt.to_timestamp()
monthly_sales.set_index('Date', inplace=True)

# Encontrar los mejores parámetros usando auto_arima sin estacionalidad
print("Optimizando parámetros SARIMA con auto_arima (sin estacionalidad)...")
auto_model = auto_arima(monthly_sales['Sales'], 
                        seasonal=False,   # Deshabilitar estacionalidad
                        trace=True,       # Mostrar progreso
                        suppress_warnings=True, 
                        stepwise=True)
print(auto_model.summary())

# Entrenar el modelo SARIMA con parámetros óptimos manuales (simplificados)
print("Entrenando el modelo SARIMA con parámetros manuales...")
sarima_model = SARIMAX(monthly_sales['Sales'], 
                       order=(1, 1, 1), 
                       seasonal_order=(1, 1, 1, 12),  # Sin componente estacional
                       enforce_stationarity=False,
                       enforce_invertibility=False)
sarima_result = sarima_model.fit(disp=False)
print("Modelo entrenado.")

# Generar predicciones para todo el año 2024
forecast = sarima_result.get_forecast(steps=12)
forecast_mean = forecast.predicted_mean
forecast_conf_int = forecast.conf_int()
forecast_index = pd.date_range(start='2024-01-01', periods=12, freq='M')

# Ajustar fechas al primer día del mes
forecast_df = pd.DataFrame({
    'Date': pd.date_range(start='2024-01-01', periods=12, freq='M'),
    'Forecast_Sales': forecast_mean.values,
    'Lower_Bound': forecast_conf_int.iloc[:, 0],
    'Upper_Bound': forecast_conf_int.iloc[:, 1]
})

forecast_df['Date'] = forecast_df['Date'].dt.to_period('M').dt.to_timestamp('D')  # Primer día del mes

# Cargar los datos reales del 2024
real_data = data[(data['Date'] >= '2024-01-01') & (data['Date'] <= '2024-12-31')]
real_monthly_sales = real_data.groupby(real_data['Date'].dt.to_period('M'))['Sales'].sum().reset_index()
real_monthly_sales['Date'] = real_monthly_sales['Date'].dt.to_timestamp()

# Comparar predicciones vs datos reales
comparison_df = pd.merge(forecast_df, real_monthly_sales, on='Date', how='left', suffixes=('_Pred', '_Real'))

# Manejar valores faltantes si no hay datos reales
comparison_df['Sales'] = comparison_df['Sales'].fillna(0)

# Calcular métricas de error
mae = mean_absolute_error(comparison_df['Sales'], comparison_df['Forecast_Sales'])
rmse = np.sqrt(mean_squared_error(comparison_df['Sales'], comparison_df['Forecast_Sales']))

# Mostrar resultados
print("\nComparación de Predicciones vs Datos Reales:")
print(comparison_df)
print(f"\nMAE (Error Medio Absoluto): {mae:.2f}")
print(f"RMSE (Raíz del Error Cuadrático Medio): {rmse:.2f}")

# Graficar predicciones vs datos reales
plt.figure(figsize=(12, 6))
plt.plot(comparison_df['Date'], comparison_df['Sales'], label='Ventas Reales', marker='o')
plt.plot(comparison_df['Date'], comparison_df['Forecast_Sales'], label='Pronóstico SARIMA', marker='o', linestyle='--')
plt.title('Comparación de Pronóstico SARIMA vs Ventas Reales - Año 2024')
plt.xlabel('Fecha')
plt.ylabel('Ventas Totales')
plt.legend()
plt.grid()
plt.show()

# Guardar proyecciones
timestamp_index = forecast_index.to_period('M').to_timestamp('D')
comparison_df = pd.DataFrame({
    'Date': timestamp_index,
    'Forecast_Sales': forecast_mean.values
})
forecast_df.to_csv('data/processed/Verano/2024_forecast_Verano_ajustado.csv', index=False)
print("Proyecciones ajustadas guardadas en '2024_forecast_Verano_ajustado.csv'.")
