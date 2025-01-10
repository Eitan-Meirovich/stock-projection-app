import pandas as pd


# Cargar el archivo processed_data.csv
import os

# Ajustar la ruta al archivo con base en la ubicación del script
file_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\processed_data.csv'
processed_data = pd.read_csv(file_path)

# Confirmar columnas disponibles
columns = processed_data.columns.tolist()

# Inspeccionar valores únicos de la columna Super_Family
super_families = processed_data['Super Familia'].unique()

# Dividir los datos por Super_Family
processed_data_groups = {}
for super_family in super_families:
    filtered_data = processed_data[processed_data['Super Familia'] == super_family]
    processed_data_groups[super_family] = filtered_data
    # Guardar cada subconjunto en un archivo CSV separado
    output_file = f'demand_forecasting_project/data/processed/processed_data_{super_family.lower()}.csv'
    filtered_data.to_csv(output_file, index=False)

# Resumen del proceso
{
    "columnas_disponibles": columns,
    "super_familias_encontradas": list(super_families),
    "archivos_generados": [f"processed_data_{sf.lower()}.csv" for sf in super_families]
}