# Importar bibliotecas necesarias
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Paso 1: Cargar los datos ajustados
data_path = 'data/processed/Cintas_Borlas_Cola_Raton/adjusted_data_cintas_borlas_colaraton.csv'  # Cambiar la ruta si es necesario
adjusted_data = pd.read_csv(data_path)

# Paso 2: Preparar los datos
adjusted_monthly_sales = adjusted_data.groupby(['Year', 'Month'])['Sales_Adjusted'].sum().reset_index()
adjusted_monthly_sales['Date'] = pd.to_datetime(adjusted_monthly_sales[['Year', 'Month']].assign(Day=1))
adjusted_monthly_sales = adjusted_monthly_sales.set_index('Date')

# Crear serie temporal
series = adjusted_monthly_sales['Sales_Adjusted']

# Paso 3: Dividir los datos en entrenamiento y prueba
train = series[adjusted_monthly_sales['Year'] < 2024]
test = series[adjusted_monthly_sales['Year'] >= 2024]

# Paso 4: Ajustar manualmente los parámetros del modelo SARIMA
# Configuración ajustada (p, d, q) x (P, D, Q, S)
model = SARIMAX(train, 
                order=(2, 1, 2),  # Ajustar componentes no estacionales
                seasonal_order=(0, 1, 1, 12),  # Ajustar componentes estacionales
                enforce_stationarity=False, 
                enforce_invertibility=False)

sarima_model = model.fit(disp=False)
print(sarima_model.summary())

# Paso 5: Generar predicciones
forecast = sarima_model.get_forecast(steps=len(test))
forecast_index = test.index
forecast_values = forecast.predicted_mean
confidence_intervals = forecast.conf_int()

# Paso 6: Visualizar resultados
plt.figure(figsize=(10, 6))
plt.plot(train, label='Entrenamiento')
plt.plot(test, label='Prueba')
plt.plot(forecast_index, forecast_values, label='Predicción', linestyle='--')
plt.fill_between(forecast_index, 
                 confidence_intervals.iloc[:, 0], 
                 confidence_intervals.iloc[:, 1], 
                 color='pink', alpha=0.3, label='Intervalo de confianza')
plt.title('Proyección de Ventas con SARIMA (Ajustado)', fontsize=14)
plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Ventas', fontsize=12)
plt.legend()
plt.grid()
plt.show()

# Paso 7: Evaluar el modelo
mae = mean_absolute_error(test, forecast_values)
mse = mean_squared_error(test, forecast_values)
rmse = np.sqrt(mse)

print(f"MAE: {mae}")
print(f"MSE: {mse}")
print(f"RMSE: {rmse}")

# Guardar las predicciones
forecast_df = pd.DataFrame({
    'Date': forecast_index,
    'Actual': test.values,
    'Predicted': forecast_values,
    'Lower_CI': confidence_intervals.iloc[:, 0].values,
    'Upper_CI': confidence_intervals.iloc[:, 1].values
})
forecast_df.to_csv('sarima_forecast_adjusted_cintas_borlas_colaraton.csv', index=False)
