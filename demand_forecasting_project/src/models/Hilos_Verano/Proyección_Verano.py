import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Cargar datos históricos de la Super Familia "Hilos Verano"
file_path =file_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\processed_data_hilos verano.csv'

data = pd.read_csv(file_path)

# Preparar y verificar datos
data['Date'] = pd.to_datetime(data['Date'])
print("Datos disponibles desde:", data['Date'].min(), "hasta:", data['Date'].max())

# Filtrar los datos hasta el 31 de diciembre de 2024
train_data = data[data['Date'] <= '2024-12-31']

# Agrupar ventas mensuales para entrenamiento
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
forecast_steps = 12
forecast_index = pd.date_range(start='2025-01-01', periods=12, freq='M')
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



# Guardar proyecciones para 2025
forecast_df.to_csv(r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Verano\2025_forecast_Verano_ETS.csv', index=False)
print("Proyecciones guardadas en '2025_forecast_Verano_ETS.csv'.")