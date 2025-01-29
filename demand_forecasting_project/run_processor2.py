import sys
import os

# Cambiar al directorio raíz del proyecto para garantizar las rutas correctas
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Añadir el directorio raíz del proyecto al PATH
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from demand_forecasting_project.src.data.data_processor import DataProcessor

# Configuración de rutas
raw_data_path = os.path.join("data", "input")
processed_data_path = os.path.join("data", "processed")
hierarchy_path = os.path.join("data", "hierarchy_mapping.json")

# Crear instancia del procesador
processor = DataProcessor(
    raw_data_path=raw_data_path,
    processed_data_path=processed_data_path,
    hierarchy_path=hierarchy_path
)

# Nombre del archivo de entrada
input_file = "data.xlsx"

# Ejecutar procesamiento
processor.process(input_file)