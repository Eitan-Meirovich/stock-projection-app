import pandas as pd
import json

# Ruta del archivo de entrada
input_file_path = 'data/input/data.xlsx'
output_hierarchy_path = 'data/hierarchy_mapping.json'

# Cargar datos desde Excel
data = pd.read_excel(input_file_path)

# Verificar columnas disponibles
print(f"Columnas disponibles: {data.columns.tolist()}")

# Renombrar columnas si es necesario
column_mapping = {
    'fecha': 'Date',
    'Codigo Producto': 'Product_Code',
    'Familia': 'Family',
    'Super Familia': 'Super_Family'
}
data.rename(columns=column_mapping, inplace=True)

# Filtrar datos válidos
data = data.dropna(subset=['Product_Code', 'Family', 'Super_Family'])

# Eliminar duplicados
data = data.drop_duplicates(subset='Product_Code')

# Crear un único mapeo jerárquico
hierarchy_mapping = {
    row['Product_Code']: {
        'Family': row['Family'],
        'Super_Family': row['Super_Family']
    }
    for _, row in data.iterrows()
}

# Guardar el mapeo como JSON
with open(output_hierarchy_path, 'w', encoding='utf-8') as f:
    json.dump(hierarchy_mapping, f, indent=4, ensure_ascii=False)

print(f"Archivo de jerarquías guardado en: {output_hierarchy_path}")
