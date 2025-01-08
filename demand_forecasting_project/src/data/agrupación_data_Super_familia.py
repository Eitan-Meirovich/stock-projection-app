import pandas as pd
import os

# Archivos de entrada y salida
input_file = 'data/processed/processed_data.csv'  # Archivo existente
output_file = 'data/processed/ventas_por_super_familia.csv'    # Archivo que crearemos

# Crear directorio de salida si no existe
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Cargar datos
data = pd.read_csv(input_file)
data['Date'] = pd.to_datetime(data['Date'])  # Asegurar que Fecha sea tipo datetime

# Agrupar ventas por Super Familia y Fecha
ventas_super_familia = (data
                        .groupby(['Super Familia', 'Date'])['Sales']
                        .sum()
                        .reset_index()
                        .rename(columns={'Sales': 'Ventas Totales'}))

# Guardar el resultado en un nuevo archivo
ventas_super_familia.to_csv(output_file, index=False)
print(f"Archivo creado: {output_file}")
