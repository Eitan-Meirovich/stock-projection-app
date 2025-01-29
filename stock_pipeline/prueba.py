"""
pipeline.py - Ejemplo actualizado y completo

Este script define un pipeline con 4 pasos:
1. step_get_stock()            -> Lee datos de SQL y guarda CSV.
2. step_consolidate_forecasts()-> Une proyecciones de distintas superfamilias en un CSV.
3. step_run_model()            -> Combina stock, forecast y relación conos-ovillos para calcular flujo de stock.
4. step_consolidate_results()  -> Recorre la carpeta 'Results' con detalles y crea un CSV final consolidado.

Al final, run_pipeline() ejecuta todo en orden.
"""
from demand_forecasting_project.src.flow_details import generate_flow_conos
import os
import pandas as pd

# 1) Importar tus constantes y rutas desde config.py:
# Asegúrate de que stock_pipeline/__init__.py exista y config.py defina todas estas variables.
from stock_pipeline.config import (
    STOCK_DATA_PATH,
    CONSOLIDATED_FORECAST_PATH,
    RELATION_CONE_PATH,        # <-- Ajusta si la relación cono-ovillos está en Excel
    PROCESSED_DIR,
    DATA_DIR,
    OUTPUT_FILE,               # A veces llamado CONSOLIDATED_FORECAST_PATH
    RESULTS_DIR,
    SERVER,
    DATABASE,
    USERNAME,
    PASSWORD
)

# Opcional: si tienes otras variables, agrégalas aquí.
# Ejemplo: SAFETY_STOCK, etc.

# ---------------------------------------------------------------------
#                 Paso 1: Obtener stock desde SQL
# ---------------------------------------------------------------------
def step_get_stock():
    """
    Paso 1: Conexión a SQL Server para leer el stock de productos, 
    y guardar el resultado en STOCK_DATA_PATH (CSV).
    """
    import pyodbc

    QUERY = """
        SELECT KOPR AS 'Product_Code', 
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
        stock_data = pd.read_sql_query(QUERY, connection)
        connection.close()

        # Guardamos DataFrame a CSV
        stock_data.to_csv(STOCK_DATA_PATH, index=False)
        print(f"[step_get_stock] Stock data guardada en: {STOCK_DATA_PATH}")
    except Exception as e:
        print(f"[step_get_stock] Error: {e}")

# ---------------------------------------------------------------------
#    Carpetas para proyecciones - Ajustar si cambian superfamilias
# ---------------------------------------------------------------------
folders = ["Invierno", "Verano", "Bebé"]

# ---------------------------------------------------------------------
#         Paso 2: Consolidar proyecciones de múltiples carpetas
# ---------------------------------------------------------------------
def step_consolidate_forecasts():
    """
    Une archivos 'forecast_product_*.csv' de cada carpeta (Invierno, Verano, etc.)
    en un CSV único, guardado en OUTPUT_FILE.
    """
    consolidated_data = []

    for folder in folders:
        folder_path = os.path.join(PROCESSED_DIR, folder)
        if not os.path.exists(folder_path):
            print(f"[step_consolidate_forecasts] Advertencia: {folder_path} no existe. Omitiendo.")
            continue

        for file in os.listdir(folder_path):
            if file.startswith("forecast_product_") and file.endswith(".csv"):
                file_path = os.path.join(folder_path, file)
                try:
                    data = pd.read_csv(file_path)
                    # Agregamos la etiqueta de superfamilia
                    data["SuperFamily"] = folder
                    consolidated_data.append(data)
                except Exception as e:
                    print(f"[step_consolidate_forecasts] Error procesando {file_path}: {e}")

    if consolidated_data:
        final_data = pd.concat(consolidated_data, ignore_index=True)

        # Crear la carpeta DATA_DIR si no existe
        os.makedirs(DATA_DIR, exist_ok=True)

        # Guardar el CSV final de las proyecciones consolidadas
        # OUTPUT_FILE suele equivaler a CONSOLIDATED_FORECAST_PATH, 
        # revisa en tu config.py si es el mismo o lo cambias por CONSOLIDATED_FORECAST_PATH
        final_data.to_csv(OUTPUT_FILE, index=False)

        print(f"[step_consolidate_forecasts] Proyecciones consolidadas guardadas en: {OUTPUT_FILE}")
    else:
        print("[step_consolidate_forecasts] No se encontraron datos de proyecciones para consolidar.")

# ---------------------------------------------------------------------
#         Paso 3: Correr el modelo de stock (conos vs. ovillos)
# ---------------------------------------------------------------------
def step_run_model():
    """
    Lee:
      - Stock data (CSV)         -> STOCK_DATA_PATH
      - Forecast data (CSV)      -> CONSOLIDATED_FORECAST_PATH (o OUTPUT_FILE, si es el mismo)
      - Relation data (Excel)    -> RELATION_CONE_PATH  (si aplica)
    Calcula stock total y flujo de stock. Genera CSVs _details.csv en carpeta 'Results'.
    """

    # 1) Leer Stock data
    try:
        stock_data = pd.read_csv(STOCK_DATA_PATH)
        print(f"[step_run_model] Leído stock_data de {STOCK_DATA_PATH}, filas={len(stock_data)}")
    except Exception as e:
        print(f"[step_run_model] Error leyendo STOCK_DATA_PATH: {e}")
        return

    # 2) Leer Forecast data (consolidada)
    try:
        forecast_data = pd.read_csv(CONSOLIDATED_FORECAST_PATH)  # o OUTPUT_FILE si es lo mismo
        print(f"[step_run_model] Leído forecast_data de {CONSOLIDATED_FORECAST_PATH}, filas={len(forecast_data)}")
    except Exception as e:
        print(f"[step_run_model] Error leyendo CONSOLIDATED_FORECAST_PATH: {e}")
        return

    # 3) Leer Relationship data (Cone-Ovillo), si aplica
    try:
        relation_data = pd.read_excel(RELATION_CONE_PATH)
        print(f"[step_run_model] Leído relation_data de {RELATION_CONE_PATH}, filas={len(relation_data)}")
    except Exception as e:
        print(f"[step_run_model] Error leyendo RELATION_CONE_PATH: {e}")
        return

    # 4) Ajustar nombres en relation_data
    #    Asumimos que viene con columns: Ovillo_Code, Cono_Code
    #    Ajusta según tu Excel real
    relation_data = relation_data.rename(columns={
        "Ovillo_Code": "Product_Code", 
        "Cono_Code": "Cone_Code"
    })

    # 5) Renombrar stock_data para poder hacer merge
    #    Tienes 'Product_Code' en stock_data, 
    #    pero si stock_data representa conos, te corresponde renombrar:
    #    Sin embargo, en tu SQL, sale KOPR='Product_Code'. 
    #    Depende de tu lógica: 
    #    * SÍ tu stock_data es de conos => rename Product_Code -> Cone_Code
    #    * Si stock_data es ya ovillos => deja tal cual.
    # 
    # Ejemplo para conos:
    stock_data = stock_data.rename(columns={
        "Product_Code": "Cone_Code", 
        "Stock": "Stock_Cones"
    })

    # 6) Hacer el merge => relation_data + stock_data => saber cuántos conos hay por cada Ovillo
    #    grouping y sum
    relation_with_stock = pd.merge(
        relation_data, 
        stock_data, 
        on='Cone_Code', 
        how='left'
    )
    # Sumar stock de conos por Product_Code
    relation_with_stock = relation_with_stock.groupby('Product_Code')["Stock_Cones"].sum().reset_index()

    # 7) Merge forecast_data con relation_with_stock para obtener Stock_Cones en el DF final
    combined_data = pd.merge(
        forecast_data, 
        relation_with_stock, 
        on='Product_Code', 
        how='left'
    )
    combined_data["Stock_Cones"] = combined_data["Stock_Cones"].fillna(0)

    # 8) Chequea si en forecast_data ya existe un 'Stock' de ovillos. 
    #    A veces, lo lees de otra tabla. 
    #    Supondré que forecast_data trae una columna "Stock" (ovillos). Si no, ajusta.
    if "Stock" not in combined_data.columns:
        # Si no hay Stock de ovillos, créalo en 0
        combined_data["Stock"] = 0

    # 9) Stock_Total = Stock (ovillos) + Stock_Cones
    combined_data["Stock_Total"] = combined_data["Stock"] + combined_data["Stock_Cones"]

    # 10) Calculamos proyección. 
    #     Asumo forecast_data tiene "Forecast_Product". 
    combined_data["Total_Projection"] = combined_data["Forecast_Product"]

    # 11) Función para calcular el flujo
    def calculate_stock_flow(subdf):
        """
        Resta la demanda (Total_Projection) de Stock_Total de manera acumulativa.
        Retorna una lista con el flujo resultante mes a mes.
        """
        stock_flow = []
        # Tomamos la 1ra fila para saber stock inicial
        available_stock = subdf["Stock_Total"].iloc[0]  
        for projection in subdf["Total_Projection"]:
            available_stock -= projection
            stock_flow.append(available_stock)
        return stock_flow

    # 12) Crear carpeta de resultados si no existe
    results_path = "Results"  # O usa RESULTS_DIR
    os.makedirs(results_path, exist_ok=True)

    # 13) Asumimos que en forecast_data hay columnas: SuperFamily, Familia, Product_Code, Month, etc.
    #     Recorrer SuperFamily -> Familia -> Product_Code
    if "SuperFamily" not in combined_data.columns:
        combined_data["SuperFamily"] = "UndefinedSF"

    if "Familia" not in combined_data.columns:
        combined_data["Familia"] = "UndefinedFam"

    if "Month" not in combined_data.columns:
        # Tal vez la forecast no usa Month, sino Fecha. Ajusta a tu data real
        combined_data["Month"] = 1  

    for super_familia in combined_data["SuperFamily"].unique():
        sf_data = combined_data[combined_data["SuperFamily"] == super_familia]
        super_familia_path = os.path.join(results_path, super_familia)
        os.makedirs(super_familia_path, exist_ok=True)

        for familia in sf_data["Familia"].unique():
            fam_data = sf_data[sf_data["Familia"] == familia]
            familia_path = os.path.join(super_familia_path, familia)
            os.makedirs(familia_path, exist_ok=True)

            for product_code in fam_data["Product_Code"].unique():
                product_data = fam_data[fam_data["Product_Code"] == product_code]

                # Agrupamos por "Month" para sumar proyección, stock, etc.
                product_monthly = product_data.groupby("Month").agg({
                    "Total_Projection": "sum",
                    "Stock_Total": "sum"
                }).reset_index().sort_values("Month")

                # Calculamos el flujo
                product_monthly["Stock_Flow"] = calculate_stock_flow(product_monthly)

                # Guardar CSV
                product_file = os.path.join(familia_path, f"{product_code}_details.csv")
                product_monthly.to_csv(product_file, index=False)

    print("[step_run_model] Modelo de stock finalizado. Archivos _details.csv creados en /Results")

# ---------------------------------------------------------------------
#         Paso 4: Consolidar resultados finales en un CSV
# ---------------------------------------------------------------------
def step_consolidate_results():
    """
    Recorre la carpeta 'Results' y sus subcarpetas, buscando archivos '*_details.csv'.
    Combina todo en un CSV final en la carpeta de RESULTS_DIR.
    """
    root_folder = "Results"   # O usa RESULTS_DIR si quieres la misma

    normalized_data = []

    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith("_details.csv"):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)

                    # Renombrar columnas para normalización
                    df.rename(columns={
                        "Month": "Fecha",
                        "Total_Projection": "Projection",
                        "Stock_Total": "Stock Total",
                        "Stock_Flow": "Stock_Flow"
                    }, inplace=True)

                    # Extraer info de la estructura de carpetas
                    path_parts = root.split(os.sep)
                    # root/.../<super_familia>/<familia>
                    if len(path_parts) >= 2:
                        super_familia = path_parts[-2]
                        familia       = path_parts[-1]
                    else:
                        super_familia = "UndefinedSF"
                        familia       = "UndefinedFam"

                    # Extraer product_code
                    codigo_producto = file.split("_")[0]  # antes del primer '_'
                    
                    df["Super Familia"] = super_familia
                    df["Familia"]       = familia
                    df["Codigo Producto"] = codigo_producto

                    columns_to_keep = [
                        "Fecha", "Super Familia", "Familia", "Codigo Producto",
                        "Projection", "Stock Total", "Stock_Flow"
                    ]
                    normalized_df = df[[c for c in columns_to_keep if c in df.columns]]

                    normalized_data.append(normalized_df)

                except Exception as e:
                    print(f"[step_consolidate_results] Error procesando {file_path}: {e}")

    if normalized_data:
        consolidated_df = pd.concat(normalized_data, ignore_index=True)
        # Guardar en CSV final
        final_csv = os.path.join(RESULTS_DIR, "consolidado_datos.csv")  # Ajusta nombre si quieres
        consolidated_df.to_csv(final_csv, index=False)
        print(f"[step_consolidate_results] Archivo consolidado generado en: {final_csv}")
    else:
        print("[step_consolidate_results] No se encontraron archivos '_details.csv' para consolidar.")

def step_flow_conos():
    print("[step_flow_conos] Generando stock_flow_details.csv usando Conos+Ovillos.")
    generate_flow_conos()
# ---------------------------------------------------------------------
#                 run_pipeline() - Ejecuta todo en orden
# ---------------------------------------------------------------------
def run_pipeline():
    print("=== EJECUTANDO PIPELINE ===")
    step_get_stock()               # 1) Leer stock de SQL -> CSV
    step_consolidate_forecasts()   # 2) Consolidar proyecciones
    step_run_model()               # 3) Combinar Stock + Forecast + Relación -> detalles
    step_flow_conos()              # 3.5) Generar stock_flow_details.csv
    step_consolidate_results()     # 4) Unir todo en un gran consolidado
    print("=== PIPELINE COMPLETADA ===")

# ---------------------------------------------------------------------
#   Punto de entrada principal
# ---------------------------------------------------------------------
if __name__ == "__main__":
    run_pipeline()
