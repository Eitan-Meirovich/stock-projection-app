# config.py
import os
from dotenv import load_dotenv

# Carga variables de entorno
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas de carpetas
DATA_DIR = os.path.join(BASE_DIR, "..", "Stock_Optimization", "Data")
RESULTS_DIR = os.path.join(BASE_DIR, "..", "Stock_Optimization", "Results")
SCRIPTS_DIR = os.path.join(BASE_DIR, "..", "Stock_Optimization", "Scripts")
PROCESSED_DIR = os.path.join(BASE_DIR, "..", "demand_forecasting_project", "data", "processed")

# Archivos
STOCK_DATA_PATH = os.path.join(DATA_DIR, "stock_data.csv")
CONSOLIDATED_FORECAST_PATH = os.path.join(DATA_DIR, "consolidated_forecast.csv")
RELATION_CONE_PATH = os.path.join(DATA_DIR, "relation_cone_skein.xlsx")
OUTPUT_FILE = os.path.join(DATA_DIR, "consolidated_forecast.csv")
# Credenciales DB (si usas .env)
SERVER = os.getenv("SQL_SERVER", "186.10.95.240")
DATABASE = os.getenv("DATABASE", "tasa_entel_srv")
USERNAME = os.getenv("USERNAME", "tasa_entel_usr")
PASSWORD = os.getenv("PASSWORD", "t4s43nt3l")

