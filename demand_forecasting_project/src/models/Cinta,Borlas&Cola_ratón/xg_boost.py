import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

# Paso 1: Cargar los datos ajustados
data_path = 'data/processed/Cintas_Borlas_Cola_Raton/adjusted_data_cintas_borlas_colaraton.csv'  # Cambiar la ruta si es necesario
adjusted_data = pd.read_csv(data_path)

# Paso 2: Preparar los datos
adjusted_monthly_sales = adjusted_data.groupby(['Year', 'Month'])['Sales_Adjusted'].sum().reset_index()
adjusted_monthly_sales['Date'] = pd.to_datetime(adjusted_monthly_sales[['Year', 'Month']].assign(Day=1))
adjusted_monthly_sales = adjusted_monthly_sales.set_index('Date')


# Crear serie temporal y características
series = adjusted_monthly_sales['Sales_Adjusted']
adjusted_monthly_sales['Lag1'] = series.shift(1)
adjusted_monthly_sales['Lag2'] = series.shift(2)
adjusted_monthly_sales['Lag3'] = series.shift(3)
adjusted_monthly_sales = adjusted_monthly_sales.dropna()

# Dividir en entrenamiento y prueba
train = adjusted_monthly_sales[adjusted_monthly_sales.index.year < 2023]
test = adjusted_monthly_sales[adjusted_monthly_sales.index.year >= 2023]
# Agregar indicador de quiebres de stock
stock_break_dates = ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01']
adjusted_monthly_sales['Stock_Break'] = adjusted_monthly_sales.index.isin(stock_break_dates).astype(int)

# Crear serie temporal y características
series = adjusted_monthly_sales['Sales_Adjusted']
adjusted_monthly_sales['Lag1'] = series.shift(1)
adjusted_monthly_sales['Lag2'] = series.shift(2)
adjusted_monthly_sales['Lag3'] = series.shift(3)
adjusted_monthly_sales = adjusted_monthly_sales.dropna()

# Dividir en entrenamiento y prueba
train = adjusted_monthly_sales[adjusted_monthly_sales.index.year < 2023]
test = adjusted_monthly_sales[adjusted_monthly_sales.index.year >= 2023]

# Separar características (X) y etiquetas (y)
X_train = train[['Lag1', 'Lag2', 'Lag3', 'Stock_Break']]
y_train = train['Sales_Adjusted']
X_test = test[['Lag1', 'Lag2', 'Lag3', 'Stock_Break']]
y_test = test['Sales_Adjusted']


# Escalar los datos
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Paso 3: Configurar búsqueda de hiperparámetros para XGBoost
ts_split = TimeSeriesSplit(n_splits=3)
param_grid = {
    'n_estimators': [50, 100, 200],
    'learning_rate': [0.01, 0.1, 0.2],
    'max_depth': [2, 3, 5],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0]
}

grid_search = GridSearchCV(
    estimator=XGBRegressor(objective='reg:squarederror'),
    param_grid=param_grid,
    cv=ts_split,
    scoring='neg_mean_absolute_error',
    verbose=1
)

grid_search.fit(X_train_scaled, y_train)

# Mejor modelo
best_model = grid_search.best_estimator_
print(f"Mejores Hiperparámetros: {grid_search.best_params_}")

# Paso 4: Generar predicciones
predictions = best_model.predict(X_test_scaled)

# Paso 5: Visualizar resultados
plt.figure(figsize=(10, 6))
plt.plot(train.index, y_train, label='Entrenamiento')
plt.plot(test.index, y_test, label='Prueba')
plt.plot(test.index, predictions, label='Predicción', linestyle='--')
plt.title('Proyección de Ventas con XGBoost (Optimizado, Quiebres de Stock)', fontsize=14)
plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Ventas', fontsize=12)
plt.legend()
plt.grid()
plt.show()

# Paso 6: Evaluar el modelo
mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
rmse = np.sqrt(mse)

print(f"MAE: {mae}")
print(f"MSE: {mse}")
print(f"RMSE: {rmse}")

# Paso 7: Análisis detallado de errores
errors = y_test - predictions
absolute_errors = np.abs(errors)
percentage_errors = (absolute_errors / y_test) * 100

# Graficar errores absolutos
plt.figure(figsize=(10, 6))
plt.bar(test.index, absolute_errors, color='orange', alpha=0.7)
plt.title('Errores Absolutos por Fecha', fontsize=14)
plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Error Absoluto', fontsize=12)
plt.grid()
plt.show()

# Graficar valores reales vs predicciones
plt.figure(figsize=(10, 6))
plt.scatter(y_test, predictions, alpha=0.7, color='blue')
plt.title('Comparación de Valores Reales vs Predicciones', fontsize=14)
plt.xlabel('Ventas Reales', fontsize=12)
plt.ylabel('Predicciones', fontsize=12)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linestyle='--')
plt.grid()
plt.show()

# Guardar análisis de errores
error_analysis_df = pd.DataFrame({
    'Date': test.index,
    'Actual': y_test.values,
    'Predicted': predictions,
    'Absolute_Error': absolute_errors,
    'Percentage_Error': percentage_errors
})
error_analysis_df.to_csv('xgboost_error_analysis_cintas_borlas_colaraton_stock_breaks.csv', index=False)

print("Análisis detallado de errores guardado en 'xgboost_error_analysis_cintas_borlas_colaraton_stock_breaks.csv'.")
