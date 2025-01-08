import subprocess
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Configuración de la página (debe ser la primera línea de Streamlit)
st.set_page_config(layout="wide", page_title="Dashboard de Proyección y Ventas")

file_path = './demand_forecasting_project/data/output/merged_data.csv'

# Cargar los datos ya procesados y reestructurarlos
@st.cache_data
def load_data():
    # Leer el archivo original
    merged_data = pd.read_csv(file_path)
    # Convertir la columna Date a formato datetime y extraer el mes
    merged_data['Date'] = pd.to_datetime(merged_data['Date'])
    merged_data['Mes'] = merged_data['Date'].dt.month
    # Crear columnas para las ventas históricas según el año
    merged_data['Venta 2024'] = merged_data['Sales'].where(merged_data['Date'].dt.year == 2024, None)
    merged_data['Venta 2023'] = merged_data['Sales'].where(merged_data['Date'].dt.year == 2023, None)
    merged_data['Venta 2022'] = merged_data['Sales'].where(merged_data['Date'].dt.year == 2022, None)
    # Seleccionar y reestructurar columnas
    restructured_data = merged_data[[
        'Mes', 'SuperFamily', 'Familia', 'Codigo Producto',
        'Projection', 'Venta 2024', 'Venta 2023', 'Venta 2022'
    ]]
    return restructured_data

data = load_data()

# Título del Dashboard
st.title("Dashboard de Proyección y Ventas")

# Barra lateral para filtros
st.sidebar.header("Filtros")

# Selección del nivel de agrupación
grouping_level = st.sidebar.radio(
    "Selecciona el nivel de agrupación:",
    ("Super Familia", "Familia", "Codigo Producto"),
    index=0
)

# Selección de vista: Trimestre o Mes
view_type = st.sidebar.radio(
    "Selecciona la vista de la tabla:",
    ("Trimestres", "Meses"),
    index=0
)

# Filtros dinámicos según el nivel de agrupación
if grouping_level == "Super Familia":
    superfamily_filter = st.sidebar.multiselect(
        "Selecciona Super Familia(s):", options=data["SuperFamily"].unique(), default=data["SuperFamily"].unique()
    )
    filtered_data = data[data["SuperFamily"].isin(superfamily_filter)]
    filtered_data = filtered_data.copy()
    if view_type == "Trimestres":
        filtered_data["Trimestre"] = ((filtered_data["Mes"] - 1) // 3) + 1
        table_data = filtered_data.groupby(["SuperFamily", "Trimestre"], as_index=False).agg({
            "Projection": "sum",
            "Venta 2024": "sum",
            "Venta 2023": "sum",
            "Venta 2022": "sum"
        })
    else:
        table_data = filtered_data.groupby(["SuperFamily", "Mes"], as_index=False).agg({
            "Projection": "sum",
            "Venta 2024": "sum",
            "Venta 2023": "sum",
            "Venta 2022": "sum"
        })

elif grouping_level == "Familia":
    superfamily_filter = st.sidebar.multiselect(
        "Selecciona Super Familia(s):", options=data["SuperFamily"].unique(), default=data["SuperFamily"].unique()
    )
    family_filter = st.sidebar.multiselect(
        "Selecciona Familia(s):", options=data["Familia"].unique(), default=data["Familia"].unique()
    )
    filtered_data = data[
        (data["SuperFamily"].isin(superfamily_filter)) &
        (data["Familia"].isin(family_filter))
    ]
    filtered_data = filtered_data.copy()
    if view_type == "Trimestres":
        filtered_data["Trimestre"] = ((filtered_data["Mes"] - 1) // 3) + 1
        table_data = filtered_data.groupby(["Familia", "Trimestre"], as_index=False).agg({
            "Projection": "sum",
            "Venta 2024": "sum",
            "Venta 2023": "sum",
            "Venta 2022": "sum"
        })
    else:
        table_data = filtered_data.groupby(["Familia", "Mes"], as_index=False).agg({
            "Projection": "sum",
            "Venta 2024": "sum",
            "Venta 2023": "sum",
            "Venta 2022": "sum"
        })

elif grouping_level == "Codigo Producto":
    family_filter = st.sidebar.selectbox(
        "Selecciona una Familia:", options=data["Familia"].unique()
    )
    product_filter = st.sidebar.multiselect(
        "Selecciona Codigo Producto(s):", 
        options=data[data["Familia"] == family_filter]["Codigo Producto"].unique(),
        default=data[data["Familia"] == family_filter]["Codigo Producto"].unique()
    )
    filtered_data = data[
        (data["Familia"] == family_filter) &
        (data["Codigo Producto"].isin(product_filter))
    ]
    filtered_data = filtered_data.copy()
    if view_type == "Trimestres":
        filtered_data["Trimestre"] = ((filtered_data["Mes"] - 1) // 3) + 1
        table_data = filtered_data.groupby(["Trimestre", "Codigo Producto"], as_index=False).agg({
            "Projection": "sum",
            "Venta 2024": "sum",
            "Venta 2023": "sum",
            "Venta 2022": "sum"
        })
    else:
        table_data = filtered_data.groupby(["Mes", "Codigo Producto"], as_index=False).agg({
            "Projection": "sum",
            "Venta 2024": "sum",
            "Venta 2023": "sum",
            "Venta 2022": "sum"
        })

# Formatear columnas numéricas
columns_to_format = ["Projection", "Venta 2024", "Venta 2023", "Venta 2022"]
for column in columns_to_format:
    if column in table_data.columns:
        table_data[column] = table_data[column].apply(
            lambda x: f"{int(x):,}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) else x
        )

# Mostrar métricas clave
st.header("Indicadores Clave")
# Calcular los totales
total_projection = table_data["Projection"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float).sum()
total_sales_2024 = table_data["Venta 2024"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float).sum()

# Formatear los totales
formatted_total_projection = f"{total_projection:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
formatted_total_sales_2024 = f"{total_sales_2024:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.metric(label="Total Proyección", value=f"{formatted_total_projection} Kg")
st.metric(label="Total Ventas 2024", value=f"{formatted_total_sales_2024} Kg")

# Tabs para mostrar la tabla y la gráfica
st.header("Resultados")
tab1, tab2 = st.tabs(["Tabla", "Gráfica"])

with tab1:
    st.subheader("Tabla de Proyecciones y Ventas")
    st.dataframe(table_data, height=300)

with tab2:
    st.subheader("Gráfica de Proyección vs. Ventas")
    fig = px.line(table_data, x=("Trimestre" if view_type == "Trimestres" else "Mes"), y=["Projection", "Venta 2024", "Venta 2023"],
                  labels={"value": "Kg", "variable": "Categoría"},
                  title="Proyección vs. Ventas", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# Descargar la tabla filtrada como Excel
def download_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        data.to_excel(writer, index=False, sheet_name="Proyecciones y Ventas")
    processed_data = output.getvalue()
    return processed_data

st.subheader("Descargar Datos Filtrados")
excel_data = download_excel(table_data)
st.download_button(
    label="Descargar Tabla en Excel",
    data=excel_data,
    file_name="Proyecciones_y_Ventas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
