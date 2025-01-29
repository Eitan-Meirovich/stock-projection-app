import os
import pandas as pd

def consolidar_proyecciones():
    # Definir rutas de los archivos
    base_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed'
    bebe_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Bebé\forecast_product_2025.csv'
    invierno_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Invierno\forecast_product_invierno.csv'
    verano_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\Verano\forecast_product_2025.csv'

    # Leer los archivos
    try:
        # Leer archivos y asegurarse de limpiar duplicados o errores
        bebe_df = pd.read_csv(bebe_path)
        bebe_df["SuperFamily"] = "Bebé"
        bebe_df["Familia"] = bebe_df["Familia"].str.strip()  # Eliminar espacios
        bebe_df["Familia"] = bebe_df["Familia"].str.replace(r'\s+', ' ', regex=True)  # Corregir concatenaciones repetitivas
        bebe_df["Product_Code"] = bebe_df["Product_Code"].str.strip()

        invierno_df = pd.read_csv(invierno_path)
        invierno_df["SuperFamily"] = "Invierno"
        invierno_df["Familia"] = invierno_df["Familia"].str.strip()
        invierno_df["Familia"] = invierno_df["Familia"].str.replace(r'\s+', ' ', regex=True)  # Corregir concatenaciones repetitivas
        invierno_df["Product_Code"] = invierno_df["Product_Code"].str.strip()

        verano_df = pd.read_csv(verano_path)
        verano_df["SuperFamily"] = "Hilos Verano"
        verano_df["Familia"] = verano_df["Familia"].str.strip()
        verano_df["Familia"] = verano_df["Familia"].str.replace(r'\s+', ' ', regex=True)  # Corregir concatenaciones repetitivas
        verano_df["Product_Code"] = verano_df["Product_Code"].str.strip()

        # Consolidar en un único DataFrame
        consolidated_df = pd.concat([bebe_df, invierno_df, verano_df], ignore_index=True)

        # Convertir la columna Month al formato Year-Month-Day
        if "Month" in consolidated_df.columns:
            consolidated_df["Month"] = pd.to_datetime(consolidated_df["Month"], errors="coerce")
            consolidated_df = consolidated_df.dropna(subset=["Month"])  # Eliminar valores no convertibles
            consolidated_df["Month"] = consolidated_df["Month"].dt.strftime("%Y-%m-%d")

        # Validar columnas problemáticas y eliminar filas completamente duplicadas
        consolidated_df = consolidated_df.drop_duplicates(subset=["Month", "Familia", "Product_Code", "SuperFamily"])

        # Ordenar el DataFrame para consistencia
        consolidated_df = consolidated_df.sort_values(by=["Month", "SuperFamily", "Familia", "Product_Code"])
        
        consolidated_df.rename(columns={
         "Month": "Date","SuperFamily" : "Super Familia" ,
         "Family":"Familia","Product_Code" : "Codigo Producto", "Forecast_Product": "Projection"
    }, inplace=True)
        # Formatear la columna 'Projection' si existe
        if "Projection" in consolidated_df.columns:
            consolidated_df["Projection"] = pd.to_numeric(consolidated_df["Projection"], errors="coerce")
            
        # Definir la ruta del archivo consolidado
        consolidated_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\output\Consolidated_forecast.csv'

        # Guardar el DataFrame consolidado
        consolidated_df.to_csv(consolidated_path, index=False)
        print(f"Archivo consolidado guardado en: {consolidated_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    consolidar_proyecciones()
