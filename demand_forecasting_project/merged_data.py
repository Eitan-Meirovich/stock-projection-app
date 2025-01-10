import pandas as pd

# Rutas de los archivos
projections_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\output\Consolidated_forecast.csv'
sales_paths = {
    "bebé": r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\input\Bebé.xlsx',
    "hilos_verano": r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\input\Hilos Verano.xlsx',
    "invierno": r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\input\Invierno.xlsx'
}

# Procesar datos de ventas
def process_sales_data(path, super_family_name):
    df = pd.read_excel(path)
    df = df.rename(columns={
        "Fecha": "Date",
        "Super Familia": "SuperFamily",
        "Codigo Producto": "Codigo Producto",
        "Familia": "Familia",
        "Venta": "Sales"
    })
    df["SuperFamily"] = super_family_name
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])  # Eliminar filas con fechas no válidas
    df["Mes"] = df["Date"].dt.month  # Extraer solo el número del mes
    df["Year"] = df["Date"].dt.year  # Extraer el año
    # Seleccionar solo columnas numéricas para la suma
    numeric_cols = [col for col in df.columns if col not in ["Date", "Mes", "Year", "SuperFamily", "Familia", "Codigo Producto"]]
    df = df.groupby(["Mes", "Year", "SuperFamily", "Familia", "Codigo Producto"])[numeric_cols].sum().reset_index()
    return df

# Cargar y procesar datos de ventas
bebe_sales = process_sales_data(sales_paths["bebé"], "Bebé")
verano_sales = process_sales_data(sales_paths["hilos_verano"], "Hilos Verano")
invierno_sales = process_sales_data(sales_paths["invierno"], "Invierno")

# Consolidar datos de ventas
sales_data = pd.concat([bebe_sales, verano_sales, invierno_sales], ignore_index=True)
sales_data = sales_data.pivot_table(
    index=["Mes", "SuperFamily", "Familia", "Codigo Producto"],
    columns="Year",
    values="Sales"
).reset_index()
sales_data.columns = ["Mes", "SuperFamily", "Familia", "Codigo Producto"] + [f"Venta {col}" for col in sales_data.columns[4:]]

# Cargar y procesar datos de proyecciones
forecast_df = pd.read_csv(projections_path)
forecast_df = forecast_df.rename(columns={"Super Familia": "SuperFamily"})
forecast_df["Date"] = pd.to_datetime(forecast_df["Date"], errors="coerce")
forecast_df = forecast_df.dropna(subset=["Date"])
forecast_df["Mes"] = forecast_df["Date"].dt.month  # Extraer solo el número del mes
forecast_df = forecast_df[["Mes", "SuperFamily", "Familia", "Codigo Producto", "Projection"]]

# Combinar proyecciones y ventas
merged_data = pd.merge(
    sales_data,
    forecast_df,
    on=["Mes", "SuperFamily", "Familia", "Codigo Producto"],
    how="outer"
)

# Reordenar columnas
columns_order = ["Mes", "SuperFamily", "Familia", "Codigo Producto", "Venta 2024", "Venta 2023", "Venta 2022", "Projection"]
merged_data = merged_data.reindex(columns=columns_order, fill_value=0)

# Guardar los datos combinados
output_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\output\merged.csv'
merged_data.to_csv(output_path, index=False)

print(f"Archivo combinado guardado exitosamente en: {output_path}")
