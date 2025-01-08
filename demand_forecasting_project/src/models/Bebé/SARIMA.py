import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
from pmdarima import auto_arima
import matplotlib.pyplot as plt
import numpy as np

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

# Optimización SARIMA
try:
    print("Optimizando parámetros SARIMA...")
    auto_model = auto_arima(
        monthly_sales['Sales'], 
        seasonal=True, 
        m=6,  # Cambiar a 6 para estacionalidad semestral o probar con otros valores
        trace=True, 
        suppress_warnings=True, 
        stepwise=True,
        seasonal_test='ch',  # Alternativa para pruebas de estacionalidad
        error_action='ignore'  # Ignorar errores menores
    )
    print("Parámetros óptimos para SARIMA:", auto_model.order, auto_model.seasonal_order)

    # Entrenar modelo SARIMA
    print("Entrenando modelo SARIMA...")
    sarima_model = SARIMAX(
        monthly_sales['Sales'],
        order=auto_model.order,
        seasonal_order=auto_model.seasonal_order,
        enforce_stationarity=True,
        enforce_invertibility=True
    )
    sarima_result = sarima_model.fit(disp=False)
    print("Modelo SARIMA entrenado.")

    # Predicciones con SARIMA
    forecast_steps = 12
    forecast_index = pd.date_range(start='2024-01-01', periods=forecast_steps, freq='M')
    sarima_forecast = sarima_result.get_forecast(steps=forecast_steps)
    sarima_forecast_mean = sarima_forecast.predicted_mean
    sarima_conf_int = sarima_forecast.conf_int()

    # Crear DataFrame de predicciones SARIMA
    sarima_forecast_df = pd.DataFrame({
        'Date': forecast_index,
        'Forecast_Sales': sarima_forecast_mean.values,
        'Lower_Bound': sarima_conf_int.iloc[:, 0].values,
        'Upper_Bound': sarima_conf_int.iloc[:, 1].values
    })
except Exception as e:
    print("Error con SARIMA:", e)
    sarima_forecast_df = pd.DataFrame()

# Comparar con datos reales
real_data_2024 = data[(data['Date'] >= '2024-01-01') & (data['Date'] <= '2024-12-31')]
real_monthly_sales = real_data_2024.groupby(real_data_2024['Date'].dt.to_period('M'))['Sales'].sum().reset_index()
real_monthly_sales['Date'] = real_monthly_sales['Date'].dt.to_timestamp()

aligned_real_sales_length = min(len(real_monthly_sales), len(sarima_forecast_df))
aligned_real_sales = real_monthly_sales['Sales'].values[:aligned_real_sales_length]
aligned_sarima_forecast = sarima_forecast_df['Forecast_Sales'].values[:aligned_real_sales_length]

# Métricas
sarima_mae = mean_absolute_error(aligned_real_sales, aligned_sarima_forecast)
sarima_rmse = np.sqrt(mean_squared_error(aligned_real_sales, aligned_sarima_forecast))
print(f"SARIMA -> MAE: {sarima_mae:.2f}, RMSE: {sarima_rmse:.2f}")

# Gráfico
plt.figure(figsize=(12, 6))
plt.plot(real_monthly_sales['Date'][:aligned_real_sales_length], aligned_real_sales, label='Ventas Reales', marker='o', color='blue')
plt.plot(sarima_forecast_df['Date'][:aligned_real_sales_length], aligned_sarima_forecast, label='SARIMA', linestyle='--', color='orange')
plt.fill_between(sarima_forecast_df['Date'][:aligned_real_sales_length], 
                 sarima_forecast_df['Lower_Bound'][:aligned_real_sales_length], 
                 sarima_forecast_df['Upper_Bound'][:aligned_real_sales_length], 
                 color='orange', alpha=0.2)
plt.title('Modelo SARIMA - Año 2024')
plt.xlabel('Fecha')
plt.ylabel('Ventas Totales')
plt.legend()
plt.grid()
plt.show()
