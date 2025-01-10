import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def main():

    st.markdown(
        """
        <style>
        body {
            background-color: #e6f7ff;
        }
        h1, h2, h3 {
            color: #003366;
            font-family: 'Arial', sans-serif;
            text-align: center;
        }
        .metric-container {
            display: flex;
            justify-content: space-around;
            margin: 40px 0;
        }
        .metric {
            width: 20%;
            padding: 40px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            font-weight: bold;
            font-color: Black;
        }
        .metric h2 {
            margin: 0;
            font-size: 18px;
            color: #003366;
        }
        .metric p {
            margin: 5px 0 0;
            font-size: 40px;
            color: black;
        }
        .metric .growth-positive {
            color: #003366;
        }
        .metric .growth-negative {
            color: red;
        }
        .content {
            text-align: center;
        }
        .stTabs {
            margin-top: 20px;
        }
        .stDataFrame {
            margin: auto;
            width: 90%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    file_path = './demand_forecasting_project/data/output/merged.csv'

    @st.cache_data
    def load_data():
        return pd.read_csv(file_path)

    data = load_data()

    st.title("Dashboard de Proyección y Ventas")

    st.sidebar.header("Filtros")

    grouping_level = st.sidebar.radio(
        "Selecciona el nivel de agrupación:",
        ("Super Familia", "Familia", "Codigo Producto"),
        index=0
    )

    view_type = st.sidebar.radio(
        "Selecciona la vista de la tabla:",
        ("Trimestres", "Meses"),
        index=0
    )

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

    columns_to_format = ["Projection", "Venta 2024", "Venta 2023", "Venta 2022"]
    for column in columns_to_format:
        if column in table_data.columns:
            table_data[column] = table_data[column].apply(
                lambda x: f"{int(x):,}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) else x
            )

    st.header("Indicadores Clave")

    total_projection = table_data["Projection"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float).sum()
    total_sales_2024 = table_data["Venta 2024"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float).sum()
    growth_percentage = ((  total_projection-total_sales_2024) / total_sales_2024) * 100 if total_sales_2024 != 0 else 0

    formatted_total_projection = f"{total_projection:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    formatted_total_sales_2024 = f"{total_sales_2024:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    formatted_growth_percentage = f"{growth_percentage:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric">
                <h2>Proyección</h2>
                <p>{formatted_total_projection} Kg</p>
            </div>
            <div class="metric">
                <h2>2024</h2>
                <p>{formatted_total_sales_2024} Kg</p>
            </div>
            <div class="metric">
                <h2>% Crecimiento</h2>
                <p class="{'growth-positive' if growth_percentage >= 0 else 'growth-negative'}">{formatted_growth_percentage}%</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.header("Resultados")
    tab1, tab2 = st.tabs(["Tabla", "Gráfica"])

    with tab1:
        st.subheader("Tabla de Proyecciones y Ventas")
        st.dataframe(table_data.style.set_properties(**{'text-align': 'center'}), height=400,width=1000)

    with tab2:
        st.subheader("Gráfica de Proyección vs. Ventas")
        fig = px.line(table_data, x=("Trimestre" if view_type == "Trimestres" else "Mes"), y=["Projection", "Venta 2024", "Venta 2023","Venta 2022"],
                      labels={"value": "Kg", "variable": "Categoría"},
                      title="Proyección vs. Ventas", markers=True)
        st.plotly_chart(fig, use_container_width=True)

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
