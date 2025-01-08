# Importar bibliotecas necesarias
from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt

# Paso 1: Cargar los datos ajustados
data_path = 'data/processed/Cintas_Borlas_Cola_Raton/adjusted_data_cintas_borlas_colaraton.csv'  # Cambiar la ruta si es necesario
adjusted_data = pd.read_csv(data_path)

# Paso 2: Preparar los datos para Prophet
adjusted_monthly_sales = adjusted_data.groupby(['Year', 'Month'])['Sales_Adjusted'].sum().reset_index()
adjusted_monthly_sales['Date'] = pd.to_datetime(adjusted_monthly_sales[['Year', 'Month']].assign(Day=1))
prophet_data = adjusted_monthly_sales[['Date', 'Sales_Adjusted']].rename(columns={'Date': 'ds', 'Sales_Adjusted': 'y'})


# Paso 3: Agregar eventos relevantes
# Crear un dataframe con eventos específicos
custom_events = pd.DataFrame({
    'ds': pd.to_datetime([
        '2023-09-01', '2023-10-01', '2023-11-01', '2023-12-01', '2024-01-01', '2024-02-01',
        '2024-09-01', '2024-10-01', '2024-11-01', '2024-12-01', '2025-01-01', '2025-02-01'
    ]),
    'event': [1] * 12  # Asignar valor 1 para los meses de eventos
})

# Fusionar eventos con el conjunto de datos
prophet_data = prophet_data.merge(custom_events, on='ds', how='left')
prophet_data['event'] = prophet_data['event'].fillna(0)  # Rellenar con 0 para meses sin eventos

# Paso 4: Dividir los datos en entrenamiento y prueba
train = prophet_data[prophet_data['ds'] < '2024-01-01']  # Datos hasta 2022
test = prophet_data[prophet_data['ds'] >= '2024-01-01']  # Datos desde 2023

# Paso 5: Construir y entrenar el modelo Prophet
model = Prophet()
model.add_country_holidays(country_name='CL')  # Ejemplo: incluir feriados de Chile
model.add_regressor('event', standardize=True)  # Agregar eventos como regresor personalizado
model.fit(train)

# Paso 6: Generar proyecciones
future = model.make_future_dataframe(periods=12, freq='M')  # Proyección de 12 meses
future = future.merge(custom_events, on='ds', how='left')  # Incorporar eventos relevantes
future['event'] = future['event'].fillna(0)  # Rellenar con 0 para meses sin eventos
forecast = model.predict(future)

# Paso 7: Visualizar resultados
fig = model.plot(forecast)
plt.title('Proyección de Ventas - Cintas, Borlas & Cola Ratón', fontsize=14)
plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Ventas Proyectadas', fontsize=12)
plt.grid(True)
plt.show()

# Paso 8: Comparar proyecciones con el conjunto de prueba
# Ajustar el formato de las fechas del conjunto de prueba
test['ds'] = test['ds'].dt.to_period('M').dt.to_timestamp()  # Asegurar formato mensual consistente
forecast['ds'] = forecast['ds'].dt.to_period('M').dt.to_timestamp()  # Ajustar fechas del forecast

# Alinear predicciones con el conjunto de prueba
aligned_forecast = forecast[['ds', 'yhat']].merge(test, on='ds', how='inner')
aligned_forecast['Error'] = aligned_forecast['y'] - aligned_forecast['yhat']
aligned_forecast['Absolute_Error'] = aligned_forecast['Error'].abs()
aligned_forecast['Percentage_Error'] = (aligned_forecast['Absolute_Error'] / aligned_forecast['y']) * 100

# Guardar los resultados
forecast.to_csv('forecast_cintas_borlas_colaraton.csv', index=False)
aligned_forecast.to_csv('comparison_test_forecast.csv', index=False)

# Mostrar errores de predicción
print("Errores de Predicción:")
print(aligned_forecast[['ds', 'y', 'yhat', 'Error', 'Absolute_Error', 'Percentage_Error']].head())
