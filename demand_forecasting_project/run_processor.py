import sys
import os


# Añadir el directorio raíz del proyecto al PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from data.data_processor import DataProcessor
# Configuración de rutas
raw_data_path = 'data/input'
processed_data_path = 'data/processed'
hierarchy_path = 'data/hierarchy_mapping.json'

# Crear instancia del procesador
processor = DataProcessor(
    raw_data_path=raw_data_path,
    processed_data_path=processed_data_path,
    hierarchy_path=hierarchy_path
)

# Nombre del archivo de entrada
input_file = 'data.xlsx'

# Ejecutar procesamiento
processor.process(input_file)
