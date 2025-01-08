import os
import pandas as pd

# Ruta exacta donde se encuentran los datos de proyección
PROCESSED_DIR = r"C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed"

# Ruta para guardar el archivo consolidado en la carpeta de optimización
OPTIMIZATION_DIR = r"C:\Users\Ukryl\stock-projection-app\Stock_Optimization\data"
OUTPUT_FILE = os.path.join(OPTIMIZATION_DIR, "consolidated_forecast.csv")

# Carpetas por superfamilia
folders = ["Invierno", "Verano", "Bebé"]

def consolidate_forecasts():
    """
    Consolida los archivos que comienzan con 'forecast_product_' de diferentes super familias
    en un solo archivo y lo guarda en la carpeta de optimización de stock.
    """
    consolidated_data = []

    for folder in folders:
        folder_path = os.path.join(PROCESSED_DIR, folder)
        if not os.path.exists(folder_path):
            print(f"Advertencia: La carpeta {folder_path} no existe. Se omitirá.")
            continue
        for file in os.listdir(folder_path):
            if file.startswith("forecast_product_") and file.endswith(".csv"):
                file_path = os.path.join(folder_path, file)
                try:
                    # Leer el archivo CSV
                    data = pd.read_csv(file_path)
                    data['SuperFamily'] = folder  # Agregar la etiqueta de superfamilia
                    consolidated_data.append(data)
                except Exception as e:
                    print(f"Error al procesar {file_path}: {e}")

    # Concatenar todos los datos
    if consolidated_data:
        final_data = pd.concat(consolidated_data, ignore_index=True)
        
        # Crear la carpeta de optimización si no existe
        os.makedirs(OPTIMIZATION_DIR, exist_ok=True)
        
        # Guardar el dataset consolidado
        final_data.to_csv(OUTPUT_FILE, index=False)
        print(f"Proyecciones consolidadas guardadas en: {OUTPUT_FILE}")
    else:
        print("No se encontraron datos para consolidar.")

if __name__ == "__main__":
    consolidate_forecasts()
