"""
pipeline.py - Versión Ajustada
--------------------------------

1. step_get_stock():
   - Lee datos de SQL (stock real = conos).
   - Guarda un CSV "stock_data.csv" con ["Product_Code", "Stock"].

2. step_consolidate_forecasts():
   - Une distintos "forecast_product_*.csv" (Invierno, Verano, Bebé...) en un CSV "consolidated_forecast.csv".
   - Agrega la columna "SuperFamily" a cada uno (por el nombre de la carpeta).

3. step_run_model():
   - Lee stock_data, forecast_data y relation_data (Cono→Ovillo).
   - Combina y genera archivos intermedios en subcarpetas de 'Results'.
   - (Opcional) Aplica lógica de simulación de consumo (Stock_Flow).

4. step_consolidate_results():
   - Recorre la carpeta 'Results' y busca '*_details.csv' para unificarlos en "stock_unificado.csv".

5. run_pipeline():
   - Ejecuta los pasos 1→2→3→4.
"""


import sys
import os
import pandas as pd

SERVER = '186.10.95.240'  # Reemplaza con el nombre de tu servidor
DATABASE = 'tasa_entel_srv'  # Reemplaza con el nombre de tu base de datos
USERNAME = 'tasa_entel_usr'  # Reemplaza con tu usuario
PASSWORD = 't4s43nt3l'  # Reemplaza con tu contraseña
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STOCK_DATA_PATH   = "Stock_Optimization/Data/stock_data.csv" 
FORECAST_DATA_PATH = "Stock_Optimization/Data/consolidated_forecast.csv" 
RELATION_CONE_PATH = "Stock_Optimization/Data/relation_cone_skein.xlsx"
PROCESSED_DIR = os.path.join(BASE_DIR, "..", "demand_forecasting_project", "data", "processed")
RESULTS_DIR = os.path.join(BASE_DIR, "..", "Stock_Optimization", "Results")

# Agregar la raíz del proyecto al sys.path
project_root = BASE_DIR
if project_root not in sys.path:
    sys.path.append(project_root)

# Archivo final unificado que el dashboard leerá

# ------------------------------------------------------------------------------
# 1) step_get_stock
# ------------------------------------------------------------------------------
def step_get_stock():
    """
    Conecta a SQL Server para leer el stock real (asumiendo que son conos).
    Guarda un CSV en STOCK_DATA_PATH con col ["Product_Code", "Stock"].
    """
    import pyodbc

    QUERY = """
    SELECT 
        KOPR AS 'Product_Code', 
        STFI1 AS 'Stock'
    FROM MAEPR
    WHERE RUPR IN ('R10','R20') 
      AND TIPR = 'FPN'
    """

    try:
        connection = pyodbc.connect(
            f"DRIVER={{SQL Server}};"
            f"SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
        )
        print("[step_get_stock] Conexión a SQL Server exitosa.")
        df_stock = pd.read_sql_query(QUERY, connection)
        connection.close()

        # Guardamos en CSV
        os.makedirs(os.path.dirname(STOCK_DATA_PATH), exist_ok=True)
        df_stock.to_csv(STOCK_DATA_PATH, index=False)
        print(f"[step_get_stock] Stock data guardada en: {STOCK_DATA_PATH}")

    except Exception as e:
        print(f"[step_get_stock] Error al conectarse a SQL o ejecutar la consulta: {e}")
pass
# ------------------------------------------------------------------------------
# 2) step_consolidate_forecasts
# ------------------------------------------------------------------------------
def step_consolidate_forecasts():
    """
    Une archivos "forecast_product_*.csv" de cada carpeta (Invierno, Verano, Bebé, etc.)
    en un CSV único (CONSOLIDATED_FORECAST_PATH).
    """
    folders = ["Invierno", "Verano", "Bebé"]  # Ajusta según tus superfamilias
    consolidated_data = []

    for folder in folders:
        folder_path = os.path.join(PROCESSED_DIR, folder)
        if not os.path.exists(folder_path):
            print(f"[step_consolidate_forecasts] Carpeta {folder_path} no existe. Omitiendo '{folder}'.")
            continue

        for file in os.listdir(folder_path):
            if file.startswith("forecast_product_") and file.endswith(".csv"):
                file_path = os.path.join(folder_path, file)
                try:
                    df_temp = pd.read_csv(file_path)
                    # Agregar columna "SuperFamily" para saber de cuál de las 3 (Invierno, Verano, etc.)
                    df_temp["SuperFamily"] = folder
                    consolidated_data.append(df_temp)
                except Exception as e:
                    print(f"[step_consolidate_forecasts] Error procesando {file_path}: {e}")

    if consolidated_data:
        df_final_forecast = pd.concat(consolidated_data, ignore_index=True)

        # Asegúrate de que exista la columna "Familia" en df_final_forecast
        # (Sino, haz un print de diagnóstico o crea una columna ficticia)
        if "Familia" not in df_final_forecast.columns:
            print("[step_consolidate_forecasts] WARNING: No existe la columna 'Familia' en las proyecciones. Se creará vacía.")
            df_final_forecast["Familia"] = "Desconocida"  # Ajusta según tu caso

        # Lo mismo para "Month" (o la que uses). 
        # if "Month" not in df_final_forecast.columns:
        #     print("[step_consolidate_forecasts] WARNING: No existe la columna 'Month'. Se creará con un valor ficticio.")
        #     df_final_forecast["Month"] = "2023-01"  # Ajustar según tu caso

        os.makedirs(os.path.dirname(FORECAST_DATA_PATH), exist_ok=True)
        df_final_forecast.to_csv(FORECAST_DATA_PATH, index=False)
        print(f"[step_consolidate_forecasts] Proyecciones consolidadas en {FORECAST_DATA_PATH}")
    else:
        print("[step_consolidate_forecasts] No se encontraron datos de proyecciones para consolidar.")
pass
# ------------------------------------------------------------------------------
# 3) step_run_model (genera archivos intermedios y, luego, usaremos la 4 para unificar)
# ------------------------------------------------------------------------------
def step_run_model():
    """
    1) Lee stock_data (conos) => STOCK_DATA_PATH
    2) Lee forecast_data => CONSOLIDATED_FORECAST_PATH
    3) Lee relation_data => RELATION_CONE_PATH (Cone_Code -> Ovillo_Code)
    4) Combina y produce un DF con, al menos:
       [Product_Code, Stock (ovillos?), Stock_Cones, Stock_Total,
        Forecast_Product, Month, Familia, SuperFamily, ...]
    5) Genera archivos *_details.csv en subcarpetas de ./Results/<SuperFamily>/<Familia>/
    """

    # 1) Leer stock_data (conos)
    try:
        df_stock_raw = pd.read_csv(STOCK_DATA_PATH)
        print(f"[step_run_model] Leído stock_data con {len(df_stock_raw)} filas.")
    except Exception as e:
        print(f"[step_run_model] Error leyendo STOCK_DATA_PATH: {e}")
        return

    # 2) Leer forecast_data (demanda)
    try:
        df_forecast_raw = pd.read_csv(FORECAST_DATA_PATH)
        print(f"[step_run_model] Leído forecast_data con {len(df_forecast_raw)} filas.")
    except Exception as e:
        print(f"[step_run_model] Error leyendo CONSOLIDATED_FORECAST_PATH: {e}")
        return

    # 3) Leer relación Cono→Ovillo (Excel)
    try:
        df_relation_raw = pd.read_excel(RELATION_CONE_PATH)
        print(f"[step_run_model] Leído relation_data con {len(df_relation_raw)} filas.")
    except Exception as e:
        print(f"[step_run_model] Error leyendo RELATION_CONE_PATH: {e}")
        return

    # Mergear las tablas utilizando la relación entre Cono_Code y Ovillo_Code
    merged_data = df_relation_raw.merge(
        df_stock_raw, left_on='Cono_Code', right_on='Product_Code', how='left'
    ).rename(columns={'Stock': 'Cono_Stock'})

    merged_data = merged_data.merge(
        df_stock_raw, left_on='Ovillo_Code', right_on='Product_Code', how='left'
    ).rename(columns={'Stock': 'Ovillo_Stock'})

    # Calcular el Stock_total
    merged_data['Stock_total'] = merged_data['Cono_Stock'].fillna(0) + merged_data['Ovillo_Stock'].fillna(0)

    # Seleccionar las columnas relevantes para el resultado final
    final_data = merged_data[['Ovillo_Code', 'Cono_Stock', 'Ovillo_Stock', 'Stock_total']]
    final_data.rename(columns={"Ovillo_Code": "Product_Code"}, inplace=True)
    # Hacemos un merge base: forecast con stock_ovillos
    # OJO: asumiendo que df_stock_raw son conos => si stock_data.csv está en conos,
    #       entonces "Product_Code" ya es el del cono. Dependiendo tu caso, ajusta:

    # En tu query, dijiste que "KOPR" = "Product_Code" y "STFI1" = "Stock".
    # Aquí supongo que en realidad es stock de conos (no ovillos). Ajusta si es distinto.

    # A) Merge forecast <-> forecast on Product_Code
    df_combined = pd.merge(
        df_forecast_raw,
        final_data,  # supuestamente "conos"
        on="Product_Code",
        how="left"  # Los que no estén en stock, quedarán con NaN
    )


    # Forecast_Product = la columna de proyección (asegúrate que exista)
    if "Forecast_Product" not in df_combined.columns:
        print("[step_run_model] WARNING: No existe la columna 'Forecast_Product'. Se creará con 0.")
        df_combined["Forecast_Product"] = 0

    # (Opcional) rename a "Total_Projection"
    df_combined["Total_Projection"] = df_combined["Forecast_Product"]

    # Para simular el flujo de stock (Stock_Flow):
    def calculate_stock_flow(data):
        stock_flow = []
        # Partimos del stock inicial (primera fila)
        available_stock = data["Stock_Total"].iloc[0]

        for projection in data["Total_Projection"]:
            available_stock -= projection
            stock_flow.append(available_stock)

        return stock_flow

    # Creamos la carpeta Results para ir guardando subcarpetas
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Debugear: ver columnas finales
    print("[DEBUG] Columnas en df_combined:", df_combined.columns.tolist())

    # Recorremos SuperFamily
    if "SuperFamily" not in df_combined.columns:
        print("[step_run_model] WARNING: No existe la columna 'SuperFamily'. Se creará con 'UndefinedSF'.")
        df_combined["SuperFamily"] = "UndefinedSF"

    for super_familia in df_combined["SuperFamily"].unique():
        df_sf = df_combined[df_combined["SuperFamily"] == super_familia]

        super_familia_path = os.path.join(RESULTS_DIR, super_familia)
        os.makedirs(super_familia_path, exist_ok=True)

        # Asegurarnos de que exista "Familia"
        if "Familia" not in df_sf.columns:
            print(f"[step_run_model] WARNING: No existe columna 'Familia' en {super_familia}. Creando una ficticia.")
            df_sf["Familia"] = "Desconocida"

        # Recorremos Familia
        for familia in df_sf["Familia"].unique():
            df_fam = df_sf[df_sf["Familia"] == familia]

            familia_path = os.path.join(super_familia_path, familia)
            os.makedirs(familia_path, exist_ok=True)

            # Recorremos Product_Code
            for product_code in df_fam["Product_Code"].unique():
                df_prod = df_fam[df_fam["Product_Code"] == product_code]


                # Agrupamos por Month
                df_prod_monthly = df_prod.groupby("Month").agg({
                    "Total_Projection":"sum",
                    "Cono_Stock":"sum",
                    "Ovillo_Stock":"sum",
                    "Stock_Total":"sum"
                }).reset_index()

                # Calculamos el flujo
                df_prod_monthly["Stock_Flow"] = calculate_stock_flow(df_prod_monthly)

                # Guardamos
                product_file = os.path.join(familia_path, f"{product_code}_details.csv")
                df_prod_monthly.to_csv(product_file, index=False)
pass
# ------------------------------------------------------------------------------
# 4) step_consolidate_results: Unir *_details.csv en un CSV final
# ------------------------------------------------------------------------------
def step_consolidate_results():
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
                                      'Projection','Cono_Stock','Ovillo_Stock', 'Stock Total', 'Stock_Flow']
                    normalized_df = df[[col for col in columns_to_keep if col in df.columns]]
                
                    # Agregar a la lista de datos consolidados
                    normalized_data.append(normalized_df)
                except Exception as e:
                    print(f"Error procesando el archivo {file_path}: {e}")

    # Consolidar los datos
    if normalized_data:
        consolidated_df = pd.concat(normalized_data, ignore_index=True)
    
        # Exportar a un archivo CSV consolidado
        output_path = "Stock_Optimization/Results/stock_unificado.csv"  # Cambia el nombre y la ubicación según lo necesites
        consolidated_df.to_csv(output_path, index=False)
        print(f"Archivo consolidado generado en: {output_path}")
    else:
        print("No se encontraron datos para consolidar.")
        pass
    # ------------------------------------------------------------------------------
    # 5) run_pipeline
# ------------------------------------------------------------------------------
def run_pipeline():
    print("=== EJECUTANDO PIPELINE ===")
    step_get_stock()               # 1) Extraer stock real de DB (conos)
    step_consolidate_forecasts()   # 2) Unir proyecciones
    step_run_model()               # 3) Combinar todo y generar archivos intermedios
    step_consolidate_results()     # 4) Unir los *_details.csv en stock_unificado.csv
    print("=== PIPELINE COMPLETADA ===")


if __name__ == "__main__":
    run_pipeline()
