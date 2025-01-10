import os
import pandas as pd

# Ruta de la carpeta raíz donde están almacenados los archivos
root_folder = "Results"  # Cambia esto por la ruta local de tus archivos

# Crear una lista para almacenar los DataFrames
normalized_data = []

# Iterar sobre las carpetas y archivos
for root, dirs, files in os.walk(root_folder):
    for file in files:
        if file.endswith('_details.csv'):
            # Ruta completa del archivo
            file_path = os.path.join(root, file)
            
            try:
                # Leer archivo
                df = pd.read_csv(file_path)
                
                # Renombrar columnas para normalización
                df.rename(columns={
                    'Month':'Fecha',
                    'Total_Projection':'Projection',
                    'Stock_Total': 'Stock Total',
                    'Stock_Flow': 'Stock_Flow'
                }, inplace=True)
                
                # Extraer información de la estructura de carpetas
                path_parts = root.split(os.sep)
                super_familia = path_parts[-2]  # Nivel de "Invierno/Verano"
                familia = path_parts[-1]       # Nombre de la familia
                codigo_producto = file.split('_')[0]  # Código del producto
                
                # Agregar columnas adicionales
                df['Super Familia'] = super_familia
                df['Familia'] = familia
                df['Codigo Producto'] = codigo_producto
                
                # Filtrar columnas relevantes
                columns_to_keep = ['Fecha', 'Super Familia', 'Familia', 'Codigo Producto', 
                                   'Projection', 'Stock Total', 'Stock_Flow']
                normalized_df = df[[col for col in columns_to_keep if col in df.columns]]
                
                # Agregar a la lista de datos consolidados
                normalized_data.append(normalized_df)
            except Exception as e:
                print(f"Error procesando el archivo {file_path}: {e}")

# Consolidar los datos
if normalized_data:
    consolidated_df = pd.concat(normalized_data, ignore_index=True)
    
    # Exportar a un archivo CSV consolidado
    output_path = "Stock_Optimization/Results/consolidado_datos.csv"  # Cambia el nombre y la ubicación según lo necesites
    consolidated_df.to_csv(output_path, index=False)
    print(f"Archivo consolidado generado en: {output_path}")
else:
    print("No se encontraron datos para consolidar.")
