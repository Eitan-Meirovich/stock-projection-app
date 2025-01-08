import subprocess
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
file_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\output\merged_data.csv'

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

# Selección del nivel de agrupación
st.sidebar.header("Tabla de datos consolidada")
grouping_level = st.sidebar.radio(
    "Selecciona el nivel de agrupación:",
    ("Super Familia", "Familia", "Codigo Producto"),
    index=0
)


# Selección de vista: Trimestre o Mes
st.sidebar.header("Vista de datos")
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
        table_data = filtered_data.groupby(["SuperFamily","Trimestre" ], as_index=False).agg({
            "Projection": "sum",
            "Venta 2024": "sum",
            "Venta 2023": "sum",
            "Venta 2022": "sum"
        })
    else:
        table_data = filtered_data.groupby(["SuperFamily","Mes" ], as_index=False).agg({
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
        table_data = filtered_data.groupby([ "Familia","Trimestre"], as_index=False).agg({
            "Projection": "sum",
            "Venta 2024": "sum",
            "Venta 2023": "sum",
            "Venta 2022": "sum"
        })
    else:
        table_data = filtered_data.groupby(["Familia","Mes" ], as_index=False).agg({
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

# Formatear los números de la tabla
table_data["Projection"] = table_data["Projection"].apply(lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
table_data["Venta 2024"] = table_data["Venta 2024"].apply(lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
table_data["Venta 2023"] = table_data["Venta 2023"].apply(lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
table_data["Venta 2022"] = table_data["Venta 2022"].apply(lambda x: f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Mostrar la tabla
st.subheader("Tabla de Proyecciones y Ventas")
columns_to_display = table_data.columns.tolist()
st.dataframe(table_data)

# Gráfica de líneas
st.subheader("Gráfica de Proyección vs. Ventas")
fig, ax = plt.subplots()
x_axis = "Trimestre" if view_type == "Trimestres" else "Mes"
if grouping_level == "Super Familia":
    for superfamily in table_data["SuperFamily"].unique():
        superfamily_data = table_data[table_data["SuperFamily"] == superfamily]
        ax.plot(superfamily_data[x_axis], superfamily_data["Projection"].str.replace(".", "").str.replace(",", ".").astype(float), label=f"Proyección {superfamily}", linestyle="--")
        ax.plot(superfamily_data[x_axis], superfamily_data["Venta 2024"].str.replace(".", "").str.replace(",", ".").astype(float), label=f"Ventas 2024 {superfamily}", linestyle="-")
        ax.plot(superfamily_data[x_axis], superfamily_data["Venta 2023"].str.replace(".", "").str.replace(",", ".").astype(float), label=f"Ventas 2023 {superfamily}", linestyle="-")
elif grouping_level == "Familia":
    for family in table_data["Familia"].unique():
        family_data = table_data[table_data["Familia"] == family]
        ax.plot(family_data[x_axis], family_data["Projection"].str.replace(".", "").str.replace(",", ".").astype(float), label=f"Proyección {family}", linestyle="--")
        ax.plot(family_data[x_axis], family_data["Venta 2024"].str.replace(".", "").str.replace(",", ".").astype(float), label=f"Ventas 2024 {family}", linestyle="-")
        ax.plot(family_data[x_axis], family_data["Venta 2023"].str.replace(".", "").str.replace(",", ".").astype(float), label=f"Ventas 2023 {family}", linestyle="-")
else:
    for product in table_data["Codigo Producto"].unique():
        product_data = table_data[table_data["Codigo Producto"] == product]
        ax.plot(product_data[x_axis], product_data["Projection"].str.replace(".", "").str.replace(",", ".").astype(float), label=f"Proyección {product}", linestyle="--")
        ax.plot(product_data[x_axis], product_data["Venta 2024"].str.replace(".", "").str.replace(",", ".").astype(float), label=f"Ventas 2024 {product}", linestyle="-")
        ax.plot(product_data[x_axis], product_data["Venta 2023"].str.replace(".", "").str.replace(",", ".").astype(float), label=f"Ventas 2023 {product}", linestyle="-")

ax.set_xlabel("Trimestre" if view_type == "Trimestres" else "Mes")
ax.set_ylabel("Kg")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3)
ax.grid(True)
st.pyplot(fig)

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
    label="Descargar Excel",
    data=excel_data,
    file_name="Proyecciones_y_Ventas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
