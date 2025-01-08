import pandas as pd
import json

# Ruta completa de los archivos
csv_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\output\Consolidated_forecast.csv'
json_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\hierarchy_mapping.json'
try:
    # Cargar los datos
    forecast_data = pd.read_csv(csv_path)
    with open(json_path, 'r', encoding='utf-8') as file:
        hierarchy_data = json.load(file)

    # Mostrar un resumen de los datos
    print(forecast_data.head())
    print(f"\nColumnas del CSV: {forecast_data.columns}")
    print(f"\nEjemplo de jerarquía: {list(hierarchy_data.items())[:5]}")
except FileNotFoundError as e:
    print(f"Error: {e}")
except UnicodeDecodeError as e:
    print(f"Error de codificación: {e}")