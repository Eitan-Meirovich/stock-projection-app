import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Cargar datos históricos de la Super Familia "Invierno"
file_path = 'data/processed/processed_data_invierno.csv'
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

# Entrenar el modelo SARIMA con datos hasta 2023
print("Entrenando el modelo SARIMA con datos hasta diciembre de 2023...")
sarima_model = SARIMAX(monthly_sales['Sales'], 
                       order=(1, 1, 1), 
                       seasonal_order=(1, 1, 1, 12),
                       enforce_stationarity=False,
                       enforce_invertibility=False)
sarima_result = sarima_model.fit(disp=False)
print("Modelo entrenado.")

# Generar predicciones para todo el año 2024
forecast_steps = 12
forecast = sarima_result.get_forecast(steps=forecast_steps)
forecast_mean = forecast.predicted_mean
forecast_index = pd.date_range(start='2024-01-01', periods=12, freq='M')

# Ajustar fechas al primer día del mes
forecast_df = pd.DataFrame({
    'Date': forecast_index,
    'Forecast_Sales': forecast_mean.values
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

comparison_df = pd.DataFrame({
    'Date': forecast_index,
    'Forecast_Sales': forecast_mean.values
})

comparison_df.to_csv('data/processed/Invierno/2024_forecast_invierno.csv', index=False)
print("Proyecciones guardadas en 'sarima_forecast_invierno.csv'")