import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
def main():
    # Estilo personalizado
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


    file_path = './Stock_Optimization/Results/consolidado_datos.csv'

    def load_data():
        try:
            data = pd.read_csv(file_path)
            data['Fecha'] = pd.to_datetime(data['Fecha'], errors='coerce')
            data['Mes'] = data['Fecha'].dt.month

            meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            data['Mes Nombre'] = data['Mes'].map({i + 1: mes for i, mes in enumerate(meses)})

            if 'Stock Total' not in data.columns:
                data['Stock Total'] = 0

            grouped = data.groupby(['Super Familia', 'Familia', 'Codigo Producto', 'Stock Total', 'Mes Nombre']).agg({
                'Projection': 'sum'
            }).reset_index()

            pivoted = grouped.pivot(index=['Super Familia', 'Familia', 'Codigo Producto', 'Stock Total'], columns='Mes Nombre', values='Projection').fillna(0).reset_index()

            for mes in meses:
                if mes not in pivoted.columns:
                    pivoted[mes] = 0

            return pivoted
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            return None

    def process_data(df, safety_stock, grouping_option, view_type):
        
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        for i, mes in enumerate(meses):
            if i == 0:
                df[mes] = df['Stock Total'] - df[mes]+ safety_stock
            else:
                prev_month = meses[i - 1]
                df[mes] = df[prev_month] - df[mes]

        df['Primer Trimestre'] = df[['Enero', 'Febrero', 'Marzo']].sum(axis=1)
        df['Segundo Trimestre'] = df[['Abril', 'Mayo', 'Junio']].sum(axis=1)
        df['Tercer Trimestre'] = df[['Julio', 'Agosto', 'Septiembre']].sum(axis=1)
        df['Cuarto Trimestre'] = df[['Octubre', 'Noviembre', 'Diciembre']].sum(axis=1)

        if grouping_option == 'Super Familia':
            grouped_data = df.groupby('Super Familia', as_index=False).agg(
               {   
                    'Stock Total': 'sum',
                    'Primer Trimestre': 'sum',
                    'Segundo Trimestre': 'sum',
                    'Tercer Trimestre': 'sum',
                    'Cuarto Trimestre': 'sum',
                    **({mes: 'sum' for mes in meses} if view_type == 'Meses' else {})
                }
            )
        elif grouping_option == 'Familia':
            grouped_data = df.groupby(['Super Familia', 'Familia'], as_index=False).agg(
                {
                    'Stock Total': 'sum',
                    'Primer Trimestre': 'sum',
                    'Segundo Trimestre': 'sum',
                    'Tercer Trimestre': 'sum',
                    'Cuarto Trimestre': 'sum',
                    **({mes: 'sum' for mes in meses} if view_type == 'Meses' else {})
                }
            )
        elif grouping_option == 'Codigo Producto':
            grouped_data = df.groupby(['Super Familia', 'Familia', 'Codigo Producto'], as_index=False).agg(
                {
                    'Stock Total': 'sum',
                    'Primer Trimestre': 'sum',
                    'Segundo Trimestre': 'sum',
                    'Tercer Trimestre': 'sum',
                    'Cuarto Trimestre': 'sum',
                    **({mes: 'sum' for mes in meses} if view_type == 'Meses' else {})
                }
            )

        return grouped_data

    def download_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos Procesados')
        return output.getvalue()

    def simulate_stock_with_safety(df, safety_stock):
        simulated_df = df.copy()
        simulated_df['Stock Total Ajustado'] = simulated_df['Stock Total'] + safety_stock
        cols = list(simulated_df.columns)
        cols.insert(cols.index('Stock Total') + 1, cols.pop(cols.index('Stock Total Ajustado')))
        simulated_df = simulated_df[cols]
        return simulated_df

    def format_numbers(df):
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            df[col] = df[col].apply(lambda x: f"{x:,.0f}".replace(",", "#").replace(".", ",").replace("#", "."))
        return df

    def style_data(df):
        def apply_styles(val):
            try:
                val = float(val.replace(".", "").replace(",", "."))
                if val < 0:
                    return "color: red; font-weight: bold;"
                else:
                    return "color: blue; font-weight: bold;"
            except:
                return ""

        styled_df = df.style.applymap(apply_styles, subset=df.columns[1:])
        return styled_df

    data = load_data()
    if data is not None:
        st.title("Dashboard de Flujo de Stock")

        st.sidebar.header("Filtros")
        
        safety_stock = st.sidebar.number_input("Ingresa el Stock de Seguridad:", min_value=0, value=0)
        
        grouping_option = st.sidebar.radio(
            "Selecciona el nivel de agrupación:",
            ["Super Familia", "Familia", "Codigo Producto"]
        )

        view_option = st.sidebar.radio(
            "Selecciona la vista de la tabla:",
            ["Trimestres", "Meses"]
        )

        if grouping_option == "Super Familia":
            superfamily_filter = st.sidebar.multiselect(
                "Selecciona Super Familia(s):", options=data["Super Familia"].unique(), default=data["Super Familia"].unique()
            )
            filtered_data = data[data["Super Familia"].isin(superfamily_filter)]

        elif grouping_option == "Familia":
            superfamily_filter = st.sidebar.selectbox(
                "Selecciona una Super Familia:", options=data["Super Familia"].unique()
            )
            family_filter = st.sidebar.multiselect(
                "Selecciona Familia(s):", 
                options=data[data["Super Familia"] == superfamily_filter]["Familia"].unique(),
                default=data[data["Super Familia"] == superfamily_filter]["Familia"].unique()
            )
            filtered_data = data[(data["Super Familia"] == superfamily_filter) & (data["Familia"].isin(family_filter))]

        elif grouping_option == "Codigo Producto":
            family_filter = st.sidebar.selectbox(
                "Selecciona una Familia:", options=data["Familia"].unique()
            )
            product_filter = st.sidebar.multiselect(
                "Selecciona Codigo Producto(s):", 
                options=data[data["Familia"] == family_filter]["Codigo Producto"].unique(),
                default=data[data["Familia"] == family_filter]["Codigo Producto"].unique()
            )
            filtered_data = data[(data["Familia"] == family_filter) & (data["Codigo Producto"].isin(product_filter))]

        grouped_data = process_data(filtered_data, safety_stock, grouping_option, view_option)
        grouped_data['Stock Total'] = grouped_data['Stock Total'] + safety_stock
        tab1, tab2 = st.tabs(["Tabla Consolidada", "Gráficos"])

        with tab1:
            st.subheader("Stock de Seguridad y Datos Consolidados")
            simulated_data = simulate_stock_with_safety(grouped_data, safety_stock)
        
            if view_option == "Trimestres":
                columns_to_display = [col for col in (['Super Familia', 'Familia', 'Codigo Producto', 'Stock Total', 'Primer Trimestre', 'Segundo Trimestre', 'Tercer Trimestre', 'Cuarto Trimestre'] if view_option == "Trimestres" else ['Super Familia', 'Familia', 'Codigo Producto', 'Stock Total'] + ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']) if col in simulated_data.columns]
            elif view_option == "Meses":
                 columns_to_display = [col for col in (['Super Familia', 'Familia', 'Codigo Producto', 'Stock Total'] + ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'] if view_option == "Meses" else ['Super Familia', 'Familia', 'Codigo Producto', 'Stock Total', 'Primer Trimestre', 'Segundo Trimestre', 'Tercer Trimestre', 'Cuarto Trimestre']) if col in simulated_data.columns]
            formatted_data = format_numbers(simulated_data[columns_to_display])
            styled_data = style_data(formatted_data)

            st.write(styled_data, unsafe_allow_html=True)


            st.download_button(
                label="Descargar Datos en Excel",
                data=download_excel(simulated_data),
                file_name="Simulacion_Stock.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
           )

        with tab2:
            st.subheader("Visualización de Datos")

            metric_option = st.selectbox(
                "Selecciona la métrica a graficar:",
                ["Stock Total", "Primer Trimestre", "Segundo Trimestre", "Tercer Trimestre", "Cuarto Trimestre"] if view_option == "Trimestres" else ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            ) 

            fig = px.bar(
                grouped_data,
                x=grouping_option,
                y=metric_option,
                title=f"{metric_option} por {grouping_option}",
                labels={metric_option: "Stock", grouping_option: grouping_option},
                text_auto=True
          )

            st.plotly_chart(fig, use_container_width=True)
