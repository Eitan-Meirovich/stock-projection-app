import pandas as pd

# Parámetros de entrada y salida
input_file = 'data/processed/processed_data.csv'  # Archivo de datos procesados
output_file = 'ventas_historicas_por_familia.csv'  # Archivo de salida

# Cargar los datos procesados
data = pd.read_csv(input_file)

# Verificar columnas relevantes
# Se asume que existen las columnas: 'Familia', 'Fecha' y 'Ventas'
if 'Familia' not in data.columns or 'Date' not in data.columns or 'Sales' not in data.columns:
    raise ValueError("El archivo debe contener las columnas: 'Familia', 'Date' y 'Sales'.")

# Convertir 'Fecha' a formato de fecha (por si acaso)
data['Date'] = pd.to_datetime(data['Date'])

# Agregar las ventas históricas por familia y por mes/año
ventas_por_familia = data.groupby(['Familia', 'Year', 'Month'])['Sales'].sum().reset_index()

# Renombrar columnas para claridad
ventas_por_familia.columns = ['Familia', 'Año', 'Mes', 'Ventas Totales']

# Ordenar los datos por familia y fecha
ventas_por_familia = ventas_por_familia.sort_values(by=['Familia', 'Año', 'Mes'])

# Guardar el archivo resultante
ventas_por_familia.to_csv(output_file, index=False)

print(f"Archivo generado con éxito: {output_file}")
