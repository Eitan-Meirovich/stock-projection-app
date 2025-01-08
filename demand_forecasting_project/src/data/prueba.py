import pandas as pd

# Archivo de entrada
input_file = 'data/processed/ventas_por_super_familia.csv'  # Ajusta el nombre si es necesario

# Cargar los datos
data = pd.read_csv(input_file)

# Mostrar valores únicos de Super Familia
print("Valores únicos en Super Familia:")
print(data['Super Familia'].unique())

# Filtrar registros con Super Familia inválida (0.0 o nulos)
invalid_super_familia = data[data['Super Familia'].isnull() | (data['Super Familia'] == 0.0)]
print("\nRegistros con Super Familia '0.0' o nula:")
print(invalid_super_familia)

# Opcional: Guardar registros inválidos en un archivo separado para revisión
invalid_super_familia.to_csv('data/processed/registros_invalidos_super_familia.csv', index=False)
# Eliminar registros inválidos
data = data[data['Super Familia'] != 0.0]

# Guardar el archivo limpio
data.to_csv('data/processed/ventas_por_super_familia_limpio.csv', index=False)
print("Archivo limpio guardado como: ventas_por_super_familia_limpio.csv")
