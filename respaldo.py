import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import matplotlib.pyplot as plt

def main():

    st.markdown("""
    <style>
        /* Modern color scheme */
        :root {
            --primary: #1E40AF;
            --secondary: #3B82F6;
            --accent: #60A5FA;
            --background: #F8FAFC;
        }
        h1, h2, h3 {
            color: var(--primary) !important;
            font-family: 'Arial', sans-serif;

        }
        h1 {
            font-size: 2.5rem !important;
            text-align: center;
            margin-bottom: 2rem !important;
        }
        h2 {
            font-size: 1.8rem !important;
            margin-bottom: 1.5rem !important;
        }        
                        
        .main {
            padding: 0rem 1rem;
        }
        .block-container {
            padding: 1rem 1rem 10rem;
            max-width: 95rem;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 2rem;
            width: 25rem !important;
        }
        .main .block-container {
            padding: 2rem 3rem;
            max-width: none;
        }
        /* Info messages */
        .stInfo {
            background-color: #EFF6FF !important;
            color: #1E40AF !important;
            border: 1px solid #BFDBFE !important;
            padding: 1rem !important;
            border-radius: 8px !important;
        }
               /* Button styling */
        .stButton > button {
            background-color: var(--primary);
            color: white;
            border-radius: 6px;
            padding: 0.5rem 1.5rem;
            border: none;
            font-weight: 600;
        }
        .stButton > button:hover {
            background-color: var(--secondary);
            border: none;
        }
             /* KPI Cards */
        div.metric-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        div.metric-container > div {
            background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
    
        div.metric-container > div:hover {
            transform: translateY(-2px);
        }
    
        .metric-container h2 {
            font-size: 1.2rem;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }
    
        .metric-container p {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--secondary);
            margin: 0;
        }
    
        .growth-positive {
            color: #059669 !important;
        }
    
        .growth-negative {
            color: #DC2626 !important;
        }        
           /* Data Tables */
        .dataframe {
            font-size: 14px !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
            margin: 1rem 0 !important;
            align text: center !important;        
        }
        .dataframe thead th {
            background-color: var(--primary) !important;
            color: White!important;
            font-size: 20px !important;   
            font-weight: 700 !important;
            padding: 12px !important;
            text-align: center !important;
        }
        .dataframe tbody td {
            padding: 10px !important;
            font-size: 20px !important;
            font-color: black !important;
            border-bottom: 1px solid #E2E8F0 !important;
            text-align: Center !important;
        }
    
        .dataframe tr:nth-child(even) {
            background-color: #F8FAFC !important;
            text-align: center !important;
        }
    
        .dataframe tr:hover {
            background-color: #EFF6FF !important;
        }  
                   /* Tabs */
        .stTabs {
            background-color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
    
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            border-bottom: 2px solid #E2E8F0;
        }
    
        .stTabs [data-baseweb="tab"] {
            height: auto !important;
            padding: 1rem 2rem !important;
            font-weight: 600 !important;
            color: var(--primary) !important;
            border: none !important;
            background-color: transparent !important;
        }
    
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: var(--primary) !important;
        }
    
        .stTabs [aria-selected="true"] {
            color: var(--primary) !important;
            border-bottom: 2px solid var(--primary) !important;
        }       
                  /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #F1F5F9;
            padding: 2rem 1rem;
            width: 25rem !important;
        }
    
        section[data-testid="stSidebar"] .block-container {
            border-radius: 12px;
            background: white;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
    
        section[data-testid="stSidebar"] h2 {
            color: var(--primary) !important;
            font-size: 1.5rem !important;
            margin-bottom: 1.5rem !important;
        }
    
        /* Radio buttons in sidebar */
        .stRadio > label {
            padding: 1rem;
            background-color: #F8FAFC;
            border-radius: 6px;
            margin-bottom: 0.5rem;
            transition: all 0.2s;
        }
    
        .stRadio > label:hover {
            background-color: #EFF6FF;
        }
                      

    </style>
    """, unsafe_allow_html=True)


    # ------------------------------------------------
    #   CARGA DE DATOS DESDE CSV (usando cache_data)
    # ------------------------------------------------
    file_path = './demand_forecasting_project/data/output/merged2.csv'

    @st.cache_data
    def load_data():
        return pd.read_csv(file_path)

    data = load_data()

    st.title("🧶Dashboard de Proyección y Ventas")
    st.write(
        "Este dashboard te permite visualizar las proyecciones de ventas del año en curso (por ejemplo, 2025) "
        "y compararlas con años anteriores, además de mostrar un cálculo acumulado (YTD) para analizar el avance "
        "hasta la fecha."
    )

    # ------------------------------------------------
    #            FILTROS EN LA SIDEBAR
    # ------------------------------------------------
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

    # ------------------------------------------------
    #   AGRUPACIÓN DE DATOS SEGÚN FILTROS SELECCIONADOS
    # ------------------------------------------------
    if grouping_level == "Super Familia":
        superfamily_filter = st.sidebar.multiselect(
            "Selecciona Super Familia(s):", 
            options=sorted(data["SuperFamily"].unique()),
            default=[]
        )
        if not superfamily_filter:
            st.warning("Por favor selecciona al menos una Super Familia.")
            st.stop()

        filtered_data = data[data["SuperFamily"].isin(superfamily_filter)]
        filtered_data = filtered_data.copy()

        if view_type == "Trimestres":
            filtered_data["Trimestre"] = ((filtered_data["Mes"] - 1) // 3) + 1
            table_data = filtered_data.groupby(["SuperFamily", "Trimestre"], as_index=False).agg({
                "Projection": "sum",
                "Venta 2025": "sum",
                "Venta 2024": "sum",
                "Venta 2023": "sum",
                "Venta 2022": "sum"
            })
        else:
            table_data = filtered_data.groupby(["SuperFamily", "Mes"], as_index=False).agg({
                "Projection": "sum",
                "Venta 2025": "sum",
                "Venta 2024": "sum",
                "Venta 2023": "sum",
                "Venta 2022": "sum"
            })

    elif grouping_level == "Familia":
        superfamily_filter = st.sidebar.multiselect(
            "Selecciona Super Familia(s):", 
            options=data["SuperFamily"].unique(),
            default=data["SuperFamily"].unique()
        )
        family_filter = st.sidebar.multiselect(
            "Selecciona Familia(s):", 
            options=sorted(data["Familia"].unique()),
            default=[]
        )
        if not family_filter:
            st.warning("Por favor selecciona al menos una Familia.")
            st.stop()

        filtered_data = data[
            (data["SuperFamily"].isin(superfamily_filter)) &
            (data["Familia"].isin(family_filter))
        ]
        filtered_data = filtered_data.copy()

        if view_type == "Trimestres":
            filtered_data["Trimestre"] = ((filtered_data["Mes"] - 1) // 3) + 1
            table_data = filtered_data.groupby(["Familia", "Trimestre"], as_index=False).agg({
                "Projection": "sum",
                "Venta 2025": "sum",
                "Venta 2024": "sum",
                "Venta 2023": "sum",
                "Venta 2022": "sum"
            })
        else:
            table_data = filtered_data.groupby(["Familia", "Mes"], as_index=False).agg({
                "Projection": "sum",
                "Venta 2025": "sum",
                "Venta 2024": "sum",
                "Venta 2023": "sum",
                "Venta 2022": "sum"
            })

    elif grouping_level == "Codigo Producto":
        family_filter = st.sidebar.selectbox(
            "Selecciona una Familia:", 
            options=data["Familia"].unique()
        )
        product_filter = st.sidebar.multiselect(
            "Selecciona Codigo Producto(s):", 
            options=sorted(data[data["Familia"] == family_filter]["Codigo Producto"].unique()),
            default=[]
        )
        if not product_filter:
            st.warning("Por favor selecciona al menos un Codigo Producto.")
            st.stop()    
        
        filtered_data = data[
            (data["Familia"] == family_filter) &
            (data["Codigo Producto"].isin(product_filter))
        ]
        filtered_data = filtered_data.copy()

        if view_type == "Trimestres":
            filtered_data["Trimestre"] = ((filtered_data["Mes"] - 1) // 3) + 1
            table_data = filtered_data.groupby(["Trimestre", "Codigo Producto"], as_index=False).agg({
                "Projection": "sum",
                "Venta 2025": "sum",
                "Venta 2024": "sum",
                "Venta 2023": "sum",
                "Venta 2022": "sum"
            })
        else:
            table_data = filtered_data.groupby(["Mes", "Codigo Producto"], as_index=False).agg({
                "Projection": "sum",
                "Venta 2025": "sum",
                "Venta 2024": "sum",
                "Venta 2023": "sum",
                "Venta 2022": "sum"
            })

    # ------------------------------------------------
    #     FORMATEO DE MILES (.,) PARA LA TABLA
    # ------------------------------------------------
    columns_to_format = ["Projection","Venta 2025", "Venta 2024", "Venta 2023", "Venta 2022"]
    for column in columns_to_format:
        if column in table_data.columns:
            table_data[column] = table_data[column].apply(
                lambda x: f"{int(x):,}".replace(",", "X").replace(".", ",").replace("X", ".") 
                if pd.notnull(x) else x
            )

    # ------------------------------------------------
    #            INDICADORES CLAVE (KPI)
    # ------------------------------------------------
    st.header("Indicadores Clave")
    st.info("Los siguientes KPIs muestran la proyección total vs. las ventas reales de 2025 y 2024, así como el crecimiento estimado.")

    # Convertir a float para la suma
    total_projection = table_data["Projection"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float).sum()
    total_sales_2025 = table_data["Venta 2025"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float).sum()
    total_sales_2024 = table_data["Venta 2024"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float).sum()

    growth_percentage = ((total_projection - total_sales_2024) / total_sales_2024) * 100 if total_sales_2024 != 0 else 0

    formatted_total_projection = f"{total_projection:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    formatted_total_sales_2025 = f"{total_sales_2025:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    formatted_total_sales_2024 = f"{total_sales_2024:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    formatted_growth_percentage = f"{growth_percentage:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Tarjetas KPI
    st.markdown(
        f"""
        <div class="metric-container">
            <div>
                <h2>Proyección</h2>
                <p>{formatted_total_projection} Kg</p>
            </div>
            <div>
                <h2>Venta 2025</h2>
                <p>{formatted_total_sales_2025} Kg</p>
            </div>
            <div>
                <h2>Venta 2024</h2>
                <p>{formatted_total_sales_2024} Kg</p>
            </div>
            <div>
                <h2>% Crecimiento</h2>
                <p class="{'growth-positive' if growth_percentage >= 0 else 'growth-negative'}">{formatted_growth_percentage}%</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------
    #        4 PESTAÑAS DE VISUALIZACIÓN
    # ------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈Tabla Resumida", 
        "📈Tabla Detallada",
        "📊Gráfica", 
        "📊Acumulados (YTD)"])

    # =========================================================
    #   1) TABLA RESUMIDA
    # =========================================================
    with tab1:
        st.markdown("<h3 style='text-align: center'>Tabla Resumida</h3>", unsafe_allow_html=True)
        st.info("Vista más sencilla con las columnas más importantes (Proyección, Venta 2025, Venta 2024).")

        # Elegimos algunas columnas clave
        resumen_cols = []
        if "Familia" in table_data.columns:
            resumen_cols.append("Familia")
        elif "SuperFamily" in table_data.columns:
            resumen_cols.append("SuperFamily")
        elif "Codigo Producto" in table_data.columns:
            resumen_cols.append("Codigo Producto")

        # Dependiendo si es Trimestre o Mes
        if view_type == "Trimestres" and "Trimestre" in table_data.columns:
            resumen_cols.append("Trimestre")
        elif "Mes" in table_data.columns:
            resumen_cols.append("Mes")

        for c in ["Projection", "Venta 2025", "Venta 2024"]:
            if c in table_data.columns:
                resumen_cols.append(c)

        table_data_resumida = table_data[resumen_cols].copy()

        # Renombrar columnas a nombres amigables
        rename_map_resum = {
            "Familia": "Familia",
            "SuperFamily": "Super Familia",
            "Codigo Producto": "Código Producto",
            "Trimestre": "Trimestre",
            "Mes": "Mes",
            "Projection": "Proyección (Kg)",
            "Venta 2025": "Venta 2025 (Kg)",
            "Venta 2024": "Venta 2024 (Kg)"
        }
        table_data_resumida.rename(columns=rename_map_resum, inplace=True)

        st.dataframe(table_data_resumida, use_container_width=True)

    # =========================================================
    #   2) TABLA DETALLADA
    # =========================================================
    with tab2:
        st.subheader("Tabla Detallada")
        st.info("Aquí se incluyen todas las columnas disponibles, incluidas ventas de años anteriores.")

        table_data_detallada = table_data.copy()

        # Reordenar para que Proyección y Venta 2025 vayan primero, luego Venta 2024, etc.
        desired_order = []
        if "SuperFamily" in table_data_detallada.columns:
            desired_order.append("SuperFamily")
        if "Familia" in table_data_detallada.columns:
            desired_order.append("Familia")
        if "Codigo Producto" in table_data_detallada.columns:
            desired_order.append("Codigo Producto")
        if "Trimestre" in table_data_detallada.columns:
            desired_order.append("Trimestre")
        elif "Mes" in table_data_detallada.columns:
            desired_order.append("Mes")

        # Luego las columnas de proyección y ventas
        for c in ["Projection", "Venta 2025", "Venta 2024", "Venta 2023", "Venta 2022"]:
            if c in table_data_detallada.columns:
                desired_order.append(c)

        # Dejamos en la tabla sólo las que existan
        desired_order = [c for c in desired_order if c in table_data_detallada.columns]
        table_data_detallada = table_data_detallada[desired_order]

        # Renombrar
        rename_map_detail = {
            "SuperFamily": "Super Familia",
            "Familia": "Familia",
            "Codigo Producto": "Código Producto",
            "Trimestre": "Trimestre",
            "Mes": "Mes",
            "Projection": "Proyección (Kg)",
            "Venta 2025": "Venta 2025 (Kg)",
            "Venta 2024": "Venta 2024 (Kg)",
            "Venta 2023": "Venta 2023 (Kg)",
            "Venta 2022": "Venta 2022 (Kg)"
        }
        table_data_detallada.rename(columns=rename_map_detail, inplace=True)

        st.dataframe(table_data_detallada, use_container_width=True)

    # =========================================================
    #   3) GRÁFICA
    # =========================================================
    with tab3:
        st.subheader("Gráfica de Proyección vs. Ventas")
        st.info("Comparativa visual para entender la relación entre Proyección y Ventas históricas.")

        # Convertir a float para graficar
        numeric_cols_plot = ["Projection","Venta 2025", "Venta 2024", "Venta 2023", "Venta 2022"]
        table_plot = table_data.copy()
        for col in numeric_cols_plot:
            if col in table_plot.columns:
                table_plot[col] = (
                    table_plot[col]
                    .astype(str)
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                    .astype(float)
                )

        # Determinar el eje X
        x_col = "Trimestre" if ("Trimestre" in table_plot.columns and view_type=="Trimestres") else "Mes"

        chart_type = st.radio(
            "Selecciona el tipo de gráfico:",
            options=["Líneas", "Barras"],
            index=0
        )

        if chart_type == "Líneas":
            fig = px.line(
                table_plot, 
                x=x_col, 
                y=["Projection", "Venta 2025", "Venta 2024", "Venta 2023", "Venta 2022"],
                labels={"value": "Kg", "variable": "Categoría", x_col:"Período"},
                title="Proyección vs. Ventas", 
                markers=True
            )
            # Destacar la línea de 'Projection' con estilo punteado
            fig.update_traces(mode="lines+markers", selector=dict(name="Projection"), line=dict(width=3, dash="dash"))
        else:
            df_melt = table_plot.melt(
                id_vars=[x_col],
                value_vars=["Projection", "Venta 2025", "Venta 2024", "Venta 2023", "Venta 2022"],
                var_name="Categoría", 
                value_name="Kg"
            )
            fig = px.bar(
                df_melt,
                x=x_col,
                y="Kg",
                color="Categoría",
                labels={"Kg": "Kg", x_col:"Período"},
                title="Proyección vs. Ventas",
                text_auto=True,
                barmode="group"
            )
        st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    #   4) ACUMULADOS (YTD)
    # =========================================================
    with tab4:
        st.info(
            "Se muestra la Proyección y Ventas 2025 de manera acumulada (YTD), "
            "para ver el avance parcial en comparación con la meta y contra 2024."
        )

        table_data_ytd = table_data.copy()

        # Convertir Trimestre/Mes a int para ordenar
        x_col = "Trimestre" if ("Trimestre" in table_data_ytd.columns and view_type=="Trimestres") else "Mes"
        if x_col not in table_data_ytd.columns:
            st.warning("No se puede calcular YTD: falta columna Mes o Trimestre.")
        else:
            table_data_ytd[x_col] = table_data_ytd[x_col].astype(int)
            table_data_ytd = table_data_ytd.sort_values(by=x_col)

            # Invertir formateo para hacer cumsum
            for c in ["Projection", "Venta 2025", "Venta 2024"]:
                if c in table_data_ytd.columns:
                    table_data_ytd[c] = (
                        table_data_ytd[c]
                        .astype(str)
                        .str.replace(".", "", regex=False)
                        .str.replace(",", ".", regex=False)
                        .astype(float)
                    )

            # Calcular cumsum
            for c in ["Projection", "Venta 2025", "Venta 2024"]:
                if c in table_data_ytd.columns:
                    ytd_col = c + "_YTD"
                    table_data_ytd[ytd_col] = table_data_ytd[c].cumsum()

            # % de cumplimiento
            if "Venta 2025_YTD" in table_data_ytd.columns and "Projection_YTD" in table_data_ytd.columns:
                table_data_ytd["%_Cumplimiento_2025"] = (
                    table_data_ytd["Venta 2025_YTD"] / table_data_ytd["Projection_YTD"] * 100
                ).fillna(0)

            # Comparación vs. 2024
            if "Venta 2025_YTD" in table_data_ytd.columns and "Venta 2024_YTD" in table_data_ytd.columns:
                table_data_ytd["%_Crecimiento_2025_vs_2024"] = (
                    (table_data_ytd["Venta 2025_YTD"] - table_data_ytd["Venta 2024_YTD"])
                    / table_data_ytd["Venta 2024_YTD"] * 100
                ).fillna(0)
                # CORRECCIÓN: tu CSV es "Venta 2024", así que la col YTD es "Venta 2024_YTD", no "Venta 24_YTD" (typo).
                # Reemplaza la línea anterior con:
                # table_data_ytd["%_Crecimiento_2025_vs_2024"] = (
                #     (table_data_ytd["Venta 2025_YTD"] - table_data_ytd["Venta 2024_YTD"])
                #     / table_data_ytd["Venta 2024_YTD"] * 100
                # ).fillna(0)

            # ==============
            # SEPARAR TABLAS
            # ==============
 
            # B) Tabla con valores acumulados (YTD)
            table_acumulada_cols = []
            if "SuperFamily" in table_data_ytd.columns:
                table_acumulada_cols.append("SuperFamily")
            if "Familia" in table_data_ytd.columns:
                table_acumulada_cols.append("Familia")
            table_acumulada_cols.append(x_col)

            for c in ["Projection_YTD", "Venta 2025_YTD", "Venta 2024_YTD", "%_Cumplimiento_2025", "%_Crecimiento_2025_vs_2024"]:
                if c in table_data_ytd.columns:
                    table_acumulada_cols.append(c)

            table_acumulada = table_data_ytd[table_acumulada_cols].copy()

            rename_acumulada = {
                "Projection_YTD": "Proyección (YTD)",
                "Venta 2025_YTD": "Venta 2025 (YTD)",
                "Venta 2024_YTD": "Venta 2024 (YTD)",
                "%_Cumplimiento_2025": "% Cumplimiento vs. Proy",
                "%_Crecimiento_2025_vs_2024": "% Crecimiento vs. 2024",
                "Trimestre": "Trimestre",
                "Mes": "Mes"
            }
            table_acumulada.rename(columns=rename_acumulada, inplace=True)
            st.write("### Tabla con valores acumulados (YTD)")
            st.write("Esta tabla muestra la suma acumulada (cumsum) de la Proyección y Ventas desde el primer período hasta el actual.")
            st.dataframe(table_acumulada, use_container_width=True)

            # ------------------------------------------------
            # GRÁFICO DE ACUMULADOS
            # ------------------------------------------------
            # Graficamos "Proyección (YTD)" vs. "Venta 2025 (YTD)"
            fig_ytd = px.line(
                table_acumulada,
                x=("Trimestre" if view_type == "Trimestres" else "Mes"),  # ya renombrado
                y=["Proyección (YTD)", "Venta 2025 (YTD)"],
                labels={"value": "Kg", "variable": "Categoría", ("Trimestre" if view_type == "Trimestres" else "Mes"): "Período"},
                title="Acumulado (YTD): Proyección vs. Venta 2025",
                markers=True
            )
            # Destacamos la línea de proyección en punteado
            fig_ytd.update_traces(mode="lines+markers", selector=dict(name="Proyección (YTD)"), line=dict(width=3, dash="dash"))
            st.write("### Acumulado (YTD): Proyección vs. Venta 2025")
            st.plotly_chart(fig_ytd, use_container_width=True)

            st.write(
                "Nota: La venta 2025 puede ser baja si estamos recién iniciando el año. "
                "Esta gráfica muestra la evolución acumulada para comparar con la proyección."
            )

    # ------------------------------------------------
    # BOTÓN DE DESCARGA (EXCEL) - USAMOS LA TABLA DETALLADA
    # ------------------------------------------------
    def download_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            dataframe.to_excel(writer, index=False, sheet_name="Proyecciones y Ventas")
        processed_data = output.getvalue()
        return processed_data

    st.subheader("Descargar Datos Filtrados")
    st.info("Descarga en formato Excel las columnas visibles en 'Tabla Detallada'.")
    excel_data = download_excel(table_data_detallada)
    st.download_button(
        label="Descargar Tabla en Excel",
        data=excel_data,
        file_name="Proyecciones_y_Ventas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == "__main__":
    main()
