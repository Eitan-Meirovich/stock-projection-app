import pandas as pd

# Rutas de los archivos
projections_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\output\Consolidated_forecast.csv'
sales_paths = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\input\demand_data.csv'

# Cargar datos de proyecciones
forecast_df = pd.read_csv(projections_path)
forecast_df = forecast_df.rename(columns={"Super Familia": "SuperFamily"})
forecast_df["Projection"] = pd.to_numeric(forecast_df["Projection"], errors="coerce")
forecast_df["Date"] = pd.to_datetime(forecast_df["Date"], errors="coerce")
forecast_df = forecast_df.dropna(subset=["Date"])
forecast_df["Mes"] = forecast_df["Date"].dt.month
forecast_df["Year"] = forecast_df["Date"].dt.year

# Agrupar datos
grouped_data = forecast_df.groupby(
    ['Mes', 'SuperFamily', 'Familia', 'Codigo Producto', 'Year']
)['Projection'].sum().reset_index()

# Separar datos por año
data_2025 = grouped_data[grouped_data['Year'] == 2025].copy()
data_2026 = grouped_data[grouped_data['Year'] == 2026].copy()

# Crear DataFrame base
base_keys = ['Mes', 'SuperFamily', 'Familia', 'Codigo Producto']
base_df = grouped_data[base_keys].drop_duplicates()

# Preparar datos 2025 y 2026
data_2025_clean = data_2025.drop('Year', axis=1).rename(columns={'Projection': 'Projection 2025'})
data_2026_clean = data_2026.drop('Year', axis=1).rename(columns={'Projection': 'Projection 2026'})

# Unir los datos
final_data = base_df.merge(
    data_2025_clean, 
    on=base_keys, 
    how='left'
).merge(
    data_2026_clean,
    on=base_keys,
    how='left'
)

# Llenar NaN con 0
final_data = final_data.fillna(0)

# Procesar datos de ventas
def process_sales_data(path):
    df = pd.read_csv(path)
    df = df.rename(columns={
        "Fecha": "Date",
        "codigoProducto": "Codigo Producto",
        "Demanda": "Sales"
    })
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Mes"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year
    numeric_cols = [col for col in df.columns if col not in ["Date", "Codigo Producto", "Mes", "Year"]]
    df = df.groupby(["Date", "Mes", "Year", "Codigo Producto"])[numeric_cols].sum().reset_index()
    return df

# Procesar ventas
sales_data = process_sales_data(sales_paths)
sales_data = sales_data.pivot_table(
    index=["Mes", "Codigo Producto"],
    columns="Year",
    values="Sales"
).reset_index()
sales_data.columns = ["Mes", "Codigo Producto"] + [f"Venta {col}" for col in sales_data.columns[2:]]

# Combinar con datos de ventas
merged_data = pd.merge(
    sales_data,
    final_data,
    on=["Mes", "Codigo Producto"],
    how="inner"
)

# Reordenar columnas
columns_order = [
    "Mes", "SuperFamily", "Familia", "Codigo Producto",
    "Venta 2025", "Venta 2024", "Venta 2023", "Venta 2022",
    "Projection 2025", "Projection 2026"
]
merged_data = merged_data.reindex(columns=columns_order, fill_value=0)

# Eliminar registros con Mes nulo
merged_data = merged_data.dropna(subset=['Mes'])

print("\nVerificación antes de guardar:")
print("Número total de registros:", len(merged_data))
print("Registros por mes:")
print(merged_data['Mes'].value_counts().sort_index())
print("\nBuscando valores nulos:")
print(merged_data.isnull().sum())

# Guardar los datos combinados
output_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\output\merged2.csv'
merged_data.to_csv(output_path, index=False)

print(f"\nArchivo combinado guardado exitosamente en: {output_path}")