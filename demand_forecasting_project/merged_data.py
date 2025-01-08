import pandas as pd

# Rutas de los archivos
projections_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\output\Consolidated_forecast.csv'
sales_paths = {
    "bebé": r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\processed_data_bebé.csv',
    "hilos_verano": r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\processed_data_hilos verano.csv',
    "invierno": r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed\processed_data_invierno.csv'
}

# Procesar datos de ventas
def process_sales_data(path, super_family_name):
    df = pd.read_csv(path)
    df = df.rename(columns={
        "Super Familia": "SuperFamily",
        "Product_Code": "Codigo Producto",
        "Familia": "Familia",
        "Sales": "Sales"
    })
    df["SuperFamily"] = super_family_name
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # Convertir a datetime64[ns]
    return df[["Date", "Familia", "SuperFamily", "Codigo Producto", "Sales"]]

# Cargar y procesar datos de ventas
bebe_sales = process_sales_data(sales_paths["bebé"], "Bebé")
verano_sales = process_sales_data(sales_paths["hilos_verano"], "Hilos Verano")
invierno_sales = process_sales_data(sales_paths["invierno"], "Invierno")

# Consolidar datos de ventas
sales_data = pd.concat([bebe_sales, verano_sales, invierno_sales], ignore_index=True)

    
# Cargar y procesar datos de proyecciones
forecast_df = pd.read_csv(projections_path)
forecast_df = forecast_df.rename(columns={"Super Familia": "SuperFamily"})
forecast_df["Date"] = pd.to_datetime(forecast_df["Date"], errors="coerce")  # Convertir a datetime64[ns]

# Fusionar datos de proyecciones y ventas
merged_data = pd.merge(
    forecast_df,
    sales_data,
    on=["Date", "Familia", "SuperFamily", "Codigo Producto"],
    how="outer"
)

# Seleccionar columnas clave
# Seleccionar columnas clave
final_columns = ["Date", "SuperFamily", "Familia", "Codigo Producto", "Projection", "Sales"]
final_data = merged_data[final_columns]

# Formatear la columna 'Sales' si existe
if "Sales" in final_data.columns:
    final_data["Sales"] = final_data["Sales"].apply(
        lambda x: f"{int(x):,}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) else x
    )

    
# Exportar el archivo consolidado
output_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\output\merged_data.csv'
final_data.to_csv(output_path, index=False)

print(f"Archivo consolidado generado exitosamente: {output_path}")