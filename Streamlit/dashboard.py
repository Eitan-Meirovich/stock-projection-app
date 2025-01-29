import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import matplotlib.pyplot as plt
import os
import subprocess
import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
FORECAST_DIR = os.path.join(BASE_DIR, "demand_forecasting_project")
base_dir = FORECAST_DIR

# ------------------------------------------------
#   Corrida de Modelo
# ------------------------------------------------
def update_demand_data():
    """
    Actualiza los datos de demanda desde SQL Server.
    """
    try:
        # Ejecutar el script de demanda
        script_path = os.path.join(base_dir, "src/data/Demanda_real.py")
        print(f"Ejecutando: {script_path}")
        result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {e.cmd}: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return False

def run_model_pipeline(input_type='demand'):
    try:
        """
        Ejecuta el pipeline completo del modelo.
        """
        base_scripts = [
            "src/data/hierarchy_map.py",
            "src/data/Data_groups.py",
            "src/models/Proyecciones.py",
            "src/models/Invierno/Top_Down.py",
            "src/models/Hilos_Verano/Top_Down_Verano_25.py",
            "src/models/Bebé/Top_Down_25.py",
            "Consolidado_resultados.py",
            "merged_data.py",
            "src/flow_details.py"
        ]

        # Elegir el procesador según el tipo de input
        if input_type == 'demand':
            print("Usando datos de demanda (data.xlsx)")
            data_processor = "run_processor2.py"
        else:
            print("Usando datos de venta (data_venta.xlsx)")
            data_processor = "run_processor.py"

        scripts = [data_processor] + base_scripts

        # Ejecutar cada script
        for script in scripts:
            script_path = os.path.join(base_dir, script)  # Ruta absoluta
            print(f"Ejecutando: {script_path}")
            result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
            print(result.stdout)

        print("Ejecución de scripts completada.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {e.cmd}: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return False

def model_control_interface():
    """
    Interface de Streamlit para controlar la ejecución del modelo
    """
    st.title("Control de Modelo de Proyección")

    st.write("""
    Esta interfaz permite ejecutar el modelo de proyección eligiendo entre usar datos
    de demanda o venta como input. El proceso actualiza automáticamente los dashboards
    una vez completado.
    """)

    # Selección del tipo de input
    input_type = st.radio(
        "Seleccione el tipo de datos de entrada:",
        ('Demanda', 'Venta'),
        horizontal=True,
        help="Elija si desea usar datos de demanda o de venta para generar las proyecciones."
    )

    # Estado de la última ejecución
    if os.path.exists('processed_data.csv'):
        last_modified = os.path.getmtime('processed_data.csv')
        last_modified_date = datetime.datetime.fromtimestamp(last_modified)
        st.info(f"Última actualización: {last_modified_date.strftime('%Y-%m-%d %H:%M:%S')}")

    # Botón para ejecutar el modelo
    if st.button("Ejecutar Modelo", type="primary"):
        with st.spinner('Ejecutando modelo...'):
            success = run_model_pipeline(input_type.lower())

            if success:
                st.success(
                    "¡Modelo ejecutado exitosamente! "
                    "Los dashboards de proyección y flujo de stock han sido actualizados."
                )
                st.experimental_rerun()
            else:
                st.error("Hubo un error en la ejecución del modelo. Por favor revisa los logs.")

def update_data_interface():
    """
    Interface de Streamlit para actualizar los datos de demanda.
    """
    st.title("Actualización de Datos de Demanda")

    st.write("""
    Esta interfaz permite actualizar los datos de demanda desde SQL Server. 
    Una vez completada la actualización, se ejecutará el modelo de proyección.
    """)

    # Estado de la última actualización
    if os.path.exists('demand_data.csv'):
        last_modified = os.path.getmtime('demand_data.csv')
        last_modified_date = datetime.datetime.fromtimestamp(last_modified)
        st.info(f"Última actualización: {last_modified_date.strftime('%Y-%m-%d %H:%M:%S')}")

    # Botón para actualizar los datos
    if st.button("Actualizar Datos de Demanda", type="primary"):
        with st.spinner('Actualizando datos...'):
            success = update_demand_data()

            if success:
                st.success("Datos de demanda actualizados exitosamente.")
                st.experimental_rerun()
            else:
                st.error("Hubo un error al actualizar los datos. Por favor revisa los logs.")

def main():

    # -----------------------------------------------------------------------
    # 1. Estilos CSS: se han agregado comentarios y ligeras mejoras visuales
    # -----------------------------------------------------------------------
    st.markdown("""
    <style>
        :root {
            --primary: #1E40AF;     /* Azul oscuro */
            --secondary: #3B82F6;   /* Azul intermedio */
            --accent: #60A5FA;      /* Azul claro */
            --background: #F8FAFC;
        }
        h1, h2, h3 {
            color: var(--primary) !important;
            font-family: 'Arial', sans-serif;
        }
        h1 {
            font-size: 2.3rem !important;
            text-align: center;
            margin-bottom: 1.5rem !important;
        }
        h2 {
            font-size: 1.8rem !important;
            margin-bottom: 1.5rem !important;
        }
        .main {
            padding: 1rem 2rem;
        }
        .block-container {
            padding: 1rem 2rem 3rem;
            max-width: 95rem;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 1rem;
            width: 20rem !important;
        }
        .main .block-container {
            padding: 1rem 2rem;
            max-width: none;
        }
        .stInfo {
            background-color: #EFF6FF !important;
            color: #1E40AF !important;
            border: 1px solid #BFDBFE !important;
            padding: 1rem !important;
            border-radius: 8px !important;
        }
        /* Botones */
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
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        div.metric-container > div {
            background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        div.metric-container > div:hover {
            transform: translateY(-2px);
        }
        .metric-container h2 {
            font-size: 1.1rem;
            color: var(--primary);
            margin-bottom: 0.3rem;
        }
        .metric-container p {
            font-size: 2rem;
            font-weight: bold;
            color: var(--secondary);
            margin: 0;
        }
        .growth-positive { color: #059669 !important; }
        .growth-negative { color: #DC2626 !important; }
        /* Tablas */
        .dataframe {
            font-size: 20px !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
            margin: 1rem 0 !important;
        }
        .dataframe thead th {
            background-color: var(--primary) !important;
            color: White!important;
            font-size: 20px !important;
            font-weight: 800 !important;
            text-align: center !important;
        }
        .dataframe tbody td {
            font-size: 20px !important;
            border-bottom: 1px solid #E2E8F0 !important;
            text-align: center !important;
        }
        .dataframe tr:nth-child(even) {
            background-color: #F8FAFC !important;
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
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #F1F5F9;
            padding: 1rem 0.5rem;
        }
        section[data-testid="stSidebar"] .block-container {
            border-radius: 12px;
            background: white;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    # ------------------------------------------------
    #   CARGA DE DATOS DESDE CSV
    # ------------------------------------------------
    file_path = './demand_forecasting_project/data/output/merged2.csv'

    @st.cache_data
    def load_data():
        data = pd.read_csv(file_path)
        
        # Convertir las columnas numéricas eliminando el formato de miles
        numeric_cols = ['Venta 2025', 'Venta 2024', 'Venta 2023', 'Venta 2022', 'Projection 2025', 'Projection 2026']
        for col in numeric_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col].replace({',': ''}, regex=True), errors='coerce')
        
        return data

    data = load_data()
    
    # ------------------------------------------------
    #   TÍTULO PRINCIPAL
    # ------------------------------------------------
    st.title("🧶 Dashboard de Proyección y Ventas")
    st.write(
        "Este dashboard te permite visualizar las proyecciones de ventas del año en curso (por ejemplo, 2025) "
        "y compararlas con años anteriores, además de mostrar un cálculo acumulado (YTD) para analizar el avance "
        "hasta la fecha."
    )

    # ------------------------------------------------
    #   FILTROS LATERALES
    # ------------------------------------------------
    with st.sidebar:
        st.header("Filtros")
        # Puedes usar expanders para no saturar la vista inicial de filtros:
        with st.expander("Seleccionar Nivel de Agregación", expanded=True):
            grouping_level = st.radio(
                "Nivel de agrupación:",
                ("Super Familia", "Familia", "Codigo Producto"),
                index=0
            )

        with st.expander("Seleccionar Vista", expanded=True):
            view_type = st.radio(
                "Vista de la tabla:",
                ("Trimestres", "Meses"),
                index=0
            )

    # ------------------------------------------------
    #   FILTRADO DE DATOS
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

        filtered_data = data[data["SuperFamily"].isin(superfamily_filter)].copy()

        if view_type == "Trimestres":
            filtered_data["Trimestre"] = ((filtered_data["Mes"] - 1) // 3) + 1
            table_data = filtered_data.groupby(["SuperFamily","Trimestre"], as_index=False).agg({
                "Projection 2025": "sum",
                "Projection 2026": "sum",
                "Venta 2025": "sum",
                "Venta 2024": "sum",
                "Venta 2023": "sum",
                "Venta 2022": "sum"
            })
        else:  # Meses
            table_data = filtered_data.groupby(["SuperFamily","Mes"], as_index=False).agg({
                "Projection 2025": "sum",
                "Projection 2026": "sum",
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
        ].copy()

        if view_type == "Trimestres":
            filtered_data["Trimestre"] = ((filtered_data["Mes"] - 1) // 3) + 1
            table_data = filtered_data.groupby(["Familia","Trimestre"], as_index=False).agg({
                "Projection 2025": "sum",
                "Projection 2026": "sum",
                "Venta 2025": "sum",
                "Venta 2024": "sum",
                "Venta 2023": "sum",
                "Venta 2022": "sum"
            })
        else:  # Meses
            table_data = filtered_data.groupby(["Familia","Mes"], as_index=False).agg({
                "Projection 2025": "sum",
                "Projection 2026": "sum",
                "Venta 2025": "sum",
                "Venta 2024": "sum",
                "Venta 2023": "sum",
                "Venta 2022": "sum"
            })

    else:  # Codigo Producto
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
        ].copy()

        if view_type == "Trimestres":
            filtered_data["Trimestre"] = ((filtered_data["Mes"] - 1) // 3) + 1
            table_data = filtered_data.groupby(["Codigo Producto","Trimestre"], as_index=False).agg({
                "Projection 2025": "sum",
                "Projection 2026": "sum",
                "Venta 2025": "sum",
                "Venta 2024": "sum",
                "Venta 2023": "sum",
                "Venta 2022": "sum"
            })
        else:  # Meses
            table_data = filtered_data.groupby(["Codigo Producto","Mes"], as_index=False).agg({
                "Projection 2025": "sum",
                "Projection 2026": "sum",
                "Venta 2025": "sum",
                "Venta 2024": "sum",
                "Venta 2023": "sum",
                "Venta 2022": "sum"
            })

    # ------------------------------------------------
    #   FORMATEO MILES (.,) PARA LA TABLA
    # ------------------------------------------------
    numeric_cols = ["Projection 2025", "Projection 2026","Venta 2025","Venta 2024","Venta 2023","Venta 2022"]
    for col in numeric_cols:
        if col in table_data.columns:
            table_data[col] = table_data[col].apply(
                lambda x: f"{int(x):,}".replace(",", "X").replace(".", ",").replace("X", ".") 
                if pd.notnull(x) else x
            )

    # ------------------------------------------------
    #            INDICADORES CLAVE (KPIs)
    # ------------------------------------------------
    st.header("Indicadores Clave")
    st.info("Los siguientes KPIs muestran la proyección total vs. las ventas reales de 2025/2024 y un crecimiento estimado.")

    # Convertir columnas a float nuevamente para poder hacer sum
    def str_to_float(val):
        # Helper para convertir "00.000" => float
        return float(
            str(val).replace(".","").replace(",",".") 
            if pd.notnull(val) and val != "" else 0
        )
    
    current_month = datetime.datetime.now().month

    # Filtrar datos hasta el mes actual
    filtered_month_data = filtered_data[filtered_data["Mes"] <= current_month]


    total_projection_2025 = filtered_month_data["Projection 2025"].apply(str_to_float).sum()
    total_projection_2026 = filtered_month_data["Projection 2026"].apply(str_to_float).sum()
    total_sales_2025 = filtered_month_data["Venta 2025"].apply(str_to_float).sum()
    total_sales_2024 = filtered_month_data["Venta 2024"].apply(str_to_float).sum()

    # Crecimiento vs. 2024

    growth_percentage = ((total_projection_2025 - total_sales_2024) / total_sales_2024) * 100 if total_sales_2024 else 0
    growth_percentage_float = growth_percentage

    formatted_growth_percentage = f"{growth_percentage_float:,.2f}" 
    formatted_total_projection = f"{total_projection_2025:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    formatted_total_sales_2025 = f"{total_sales_2025:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    formatted_total_sales_2024 = f"{total_sales_2024:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    formatted_growth_percentage = formatted_growth_percentage.replace(",", "X").replace(".", ",").replace("X", ".")


    # ------------------------------------------------
    # YTD según Mes / Trimestre actual
    # ------------------------------------------------
  
    if view_type == "Meses":
        time_column = "Mes"
        current_period = datetime.datetime.now().month
    else:
        time_column = "Trimestre"
        current_period = (datetime.datetime.now().month - 1) // 3 + 1

    # Copia para cálculos YTD
    table_data_ytd = table_data.copy()
    # Convertir la columna de período a int
    if time_column in table_data_ytd.columns:
        table_data_ytd[time_column] = table_data_ytd[time_column].astype(int)
        table_data_ytd = table_data_ytd[table_data_ytd[time_column] <= current_period]

        # Quitar formateo en Projection, Venta 2025, Venta 2024
        for col in ["Projection 2025", "Venta 2025", "Venta 2024"]:
            if col in table_data_ytd.columns:
                table_data_ytd[col] = table_data_ytd[col].apply(str_to_float)

        # Sumas
        projection_ytd = table_data_ytd["Projection 2025"].sum()
        venta_2025_ytd = table_data_ytd["Venta 2025"].sum()
        venta_2024_ytd = table_data_ytd["Venta 2024"].sum()

        # Comparaciones
        growth_percentage_projection = ((venta_2025_ytd - projection_ytd ) / projection_ytd) * 100 if venta_2025_ytd else 0
        growth_percentage_sales = ((venta_2025_ytd - venta_2024_ytd) / venta_2024_ytd) * 100 if venta_2024_ytd else 0

        formatted_projection_ytd = f"{projection_ytd:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_venta_2025_ytd = f"{venta_2025_ytd:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_venta_2024_ytd = f"{venta_2024_ytd:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_growth_projection = f"{growth_percentage_projection:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        formatted_growth_sales = f"{growth_percentage_sales:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        # Si no encuentra la columna de tiempo
        projection_ytd, venta_2025_ytd, venta_2024_ytd = 0,0,0
        formatted_growth_projection, formatted_growth_sales = "0","0"

    # ------------------------------------------------
    # Tarjetas KPI con estilo
    # ------------------------------------------------
    st.markdown(
        f"""
        <div class="metric-container">
            <div>
                <h2>Proyección</h2>
                <p>{formatted_projection_ytd} Kg</p>
            </div>
            <div>
                <h2>Venta 2025</h2>
                <p>{formatted_venta_2025_ytd} Kg</p>
            </div>
            <div>
                <h2>Venta 2024</h2>
                <p>{formatted_venta_2024_ytd} Kg</p>
            </div>
            <div>
                <h2>% Cump_Proy</h2>
                <p class="{'growth-positive' if growth_percentage_projection >= 0 else 'growth-negative'}">
                    {formatted_growth_projection}%
                </p>
            </div>
            <div>
                <h2>% 25 vs 24 YTD</h2>
                <p class="{'growth-positive' if growth_percentage_sales >= 0 else 'growth-negative'}">
                    {formatted_growth_sales}%
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------
    #  PESTAÑAS DE VISUALIZACIÓN
    # ------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈Tabla Resumida", 
        "📈Tabla Detallada",
        "📊Gráfica", 
        "📊Acumulados (YTD)",
        "⚙️ Control de Modelo",
        "📊 Comportamiento de Producto"

    ])

    # =========================================================
    #   1) TABLA RESUMIDA
    # =========================================================
    with tab1:
        st.markdown("<h3 style='text-align: center'>Tabla Resumida</h3>", unsafe_allow_html=True)
        st.info("Vista sencilla con las columnas más importantes (Proyección, Venta 2025, Venta 2024).")

        # Selección de columnas
        resumen_cols = []
        if "Familia" in table_data.columns:
            resumen_cols.append("Familia")
        elif "SuperFamily" in table_data.columns:
            resumen_cols.append("SuperFamily")
        elif "Codigo Producto" in table_data.columns:
            resumen_cols.append("Codigo Producto")

        # Trimestre o Mes
        if view_type == "Trimestres" and "Trimestre" in table_data.columns:
            resumen_cols.append("Trimestre")
        elif "Mes" in table_data.columns:
            resumen_cols.append("Mes")

        for c in ["Projection 2026","Projection 2025", "Venta 2025", "Venta 2024"]:
            if c in table_data.columns:
                resumen_cols.append(c)

        table_data_resumida = table_data[resumen_cols].copy()

        rename_map_resum = {
            "Familia": "Familia",
            "SuperFamily": "Super Familia",
            "Codigo Producto": "Código Producto",
            "Trimestre": "Trimestre",
            "Mes": "Mes",
            "Projection 2026": "Proyección 2026 (Kg)",
            "Projection 2025": "Proyección 2025 (Kg)",
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
        desired_order = []

        # Orden lógico de las columnas
        for col in ["SuperFamily","Familia","Codigo Producto","Trimestre","Mes", "Projection 2026","Projection 2025","Venta 2025","Venta 2024","Venta 2023","Venta 2022"]:
            if col in table_data_detallada.columns:
                desired_order.append(col)

        table_data_detallada = table_data_detallada[desired_order]

        rename_map_detail = {
            "SuperFamily": "Super Familia",
            "Familia": "Familia",
            "Codigo Producto": "Código Producto",
            "Trimestre": "Trimestre",
            "Mes": "Mes",
            "Projection 2026": "Proyección 2026 (Kg)",
            "Projection 2025": "Proyección 2025 (Kg)",
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

        # Para graficar, revertimos formateo
        table_plot = table_data.copy()
        for col in numeric_cols:
            if col in table_plot.columns:
                table_plot[col] = table_plot[col].apply(str_to_float)

        # Determinar eje X
        x_col = "Trimestre" if ("Trimestre" in table_plot.columns and view_type=="Trimestres") else "Mes"

        chart_type = st.radio(
            "Tipo de gráfico:",
            ["Líneas", "Barras"],
            index=0
        )

        # Generar la figura
        if chart_type == "Líneas":
            fig = px.line(
                table_plot, 
                x=x_col, 
                y=["Projection 2025", "Projection 2026", "Venta 2025", "Venta 2024", "Venta 2023", "Venta 2022"],
                labels={"value": "Kg", "variable": "Categoría", x_col:"Período"},
                title="Proyección vs. Ventas",
                markers=True
            )
            # Línea punteada para Projection
            fig.update_traces(
                mode="lines+markers",
                selector=dict(name="Projection"),
                line=dict(width=3, dash="dash")
            )
        else:
            df_melt = table_plot.melt(
                id_vars=[x_col],
                value_vars=["Projection 2025", "Projection 2026", "Venta 2025", "Venta 2024", "Venta 2023", "Venta 2022"],
                var_name="Categoría", 
                value_name="Kg"
            )
            fig = px.bar(
                df_melt,
                x=x_col,
                y="Kg",
                color="Categoría",
                barmode="group",
                text_auto=True,
                labels={"Kg": "Kg", x_col:"Período"},
                title="Proyección vs. Ventas"
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

        # Copia de la tabla para el cumsum
        table_data_ytd = table_data.copy()
        x_col = "Trimestre" if ("Trimestre" in table_data_ytd.columns and view_type=="Trimestres") else "Mes"
        if x_col not in table_data_ytd.columns:
            st.warning("No se puede calcular YTD: falta columna Mes o Trimestre.")
        else:
            table_data_ytd[x_col] = table_data_ytd[x_col].astype(int)
            table_data_ytd = table_data_ytd.sort_values(by=x_col)

            # Convertir a float
            for c in ["Projection 2025", "Projection 2026","Venta 2025","Venta 2024"]:
                if c in table_data_ytd.columns:
                    table_data_ytd[c] = table_data_ytd[c].apply(str_to_float)

            # Calcular cumsum
            for c in ["Projection 2025", "Projection 2026","Venta 2025","Venta 2024"]:
                ytd_col = c + "_YTD"
                if c in table_data_ytd.columns:
                    table_data_ytd[ytd_col] = table_data_ytd[c].cumsum()

            # % de cumplimiento
            if "Venta 2025_YTD" in table_data_ytd.columns and "Projection_YTD" in table_data_ytd.columns:
                table_data_ytd["%_Cumplimiento_2025"] = (
                    table_data_ytd["Venta 2025_YTD"] / table_data_ytd["Projection 2025_YTD"] * 100
                ).fillna(0)

            # % Crecimiento vs. 2024
            if "Venta 2024_YTD" in table_data_ytd.columns and "Venta 2025_YTD" in table_data_ytd.columns:
                table_data_ytd["%_Crecimiento_2025_vs_2024"] = (
                    (table_data_ytd["Venta 2025_YTD"] - table_data_ytd["Venta 2024_YTD"])
                     / table_data_ytd["Venta 2024_YTD"] * 100
                ).fillna(0)

            # Tabla con valores acumulados (YTD)
            needed_cols = []
            if "SuperFamily" in table_data_ytd.columns:
                needed_cols.append("SuperFamily")
            if "Familia" in table_data_ytd.columns:
                needed_cols.append("Familia")
            needed_cols.append(x_col)
            for c in ["Projection 2025_YTD","Venta 2025_YTD","Venta 2024_YTD","%_Cumplimiento_2025","%_Crecimiento_2025_vs_2024"]:
                if c in table_data_ytd.columns:
                    needed_cols.append(c)

            table_acumulada = table_data_ytd[needed_cols].copy()

            rename_acumulada = {
                "Projection 2025_YTD": "Proyección (YTD)",
                "Venta 2025_YTD": "Venta 2025 (YTD)",
                "Venta 2024_YTD": "Venta 2024 (YTD)",
                "%_Cumplimiento_2025": "% Cumplimiento vs. Proy",
                "%_Crecimiento_2025_vs_2024": "% Crecimiento vs. 2024",
                "Trimestre": "Trimestre",
                "Mes": "Mes"
            }
            table_acumulada.rename(columns=rename_acumulada, inplace=True)

            st.write("### Tabla con valores acumulados (YTD)")
            st.write("Esta tabla muestra la suma acumulada de Proyección y Ventas (cumsum) desde el primer período hasta el actual.")
            st.dataframe(table_acumulada, use_container_width=True)

            # Gráfico de Acumulados
            fig_ytd = px.line(
                table_acumulada,
                x=("Trimestre" if view_type == "Trimestres" else "Mes"),
                y=["Proyección (YTD)","Venta 2025 (YTD)"],
                labels={"value": "Kg", "variable": "Categoría", ("Trimestre" if view_type == "Trimestres" else "Mes"):"Período"},
                title="Acumulado (YTD): Proyección vs. Venta 2025",
                markers=True
            )
            fig_ytd.update_traces(
                mode="lines+markers",
                selector=dict(name="Proyección (YTD)"),
                line=dict(width=3, dash="dash")
            )
            st.write("### Acumulado (YTD): Proyección vs. Venta 2025")
            st.plotly_chart(fig_ytd, use_container_width=True)

            st.write(
                "Nota: La venta 2025 puede ser baja si el año está iniciando. "
                "Esta gráfica muestra la evolución acumulada para comparar con la proyección."
            )

    # =========================================================
    #   5) CONTROL DE MODELO
    # =========================================================
    with tab5:
        model_control_interface()
        update_data_interface()

    # ------------------------------------------------
    #   BOTÓN DE DESCARGA (EXCEL) - TABLA DETALLADA
    # ------------------------------------------------
    def download_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            dataframe.to_excel(writer, index=False, sheet_name="Proyecciones_y_Ventas")
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

    with tab6:
        st.header("📊 Comportamiento de Productos dentro de una Familia")
        
        # Filtro de familia
        family_filter = st.multiselect(
            "Selecciona una Familia:", 
            options=sorted(data["Familia"].unique()),
            default=[]
        )

        if not family_filter:
            st.warning("Por favor selecciona al menos una familia para visualizar los datos.")
            return

        # Filtro de vista
        view_type = st.radio("Seleccionar vista:", ["Meses", "Trimestres"], horizontal=True)

        # Filtrar datos por familia
        filtered_data = data[data["Familia"].isin(family_filter)].copy()

        if view_type == "Trimestres":
            filtered_data["Trimestre"] = ((filtered_data["Mes"] - 1) // 3) + 1
            time_col = "Trimestre"
        else:
            time_col = "Mes"
        
        # Tabla de datos
        table_data = filtered_data.groupby(["Codigo Producto", time_col], as_index=False).agg({
            "Venta 2023": "sum", "Venta 2024": "sum", "Venta 2025": "sum", "Projection 2025": "sum"
        })
        
        pivot_table = table_data.pivot(index="Codigo Producto", columns=time_col, values=["Venta 2023", "Venta 2024", "Venta 2025", "Projection 2025"])
        pivot_table.columns = [f"{col[0]} - {col[1]}" for col in pivot_table.columns]
        pivot_table.reset_index(inplace=True)
        
        st.dataframe(pivot_table, use_container_width=True)

        # KPIs
        total_ventas_2025 = filtered_data["Venta 2025"].sum()
        total_proyeccion_2025 = filtered_data["Projection 2025"].sum()
        growth_vs_2024 = ((total_ventas_2025 - filtered_data["Venta 2024"].sum()) / filtered_data["Venta 2024"].sum()) * 100 if filtered_data["Venta 2024"].sum() else 0
        
        st.metric(label="Total Venta 2025", value=f"{total_ventas_2025:,.0f} Kg")
        st.metric(label="Proyección 2025", value=f"{total_proyeccion_2025:,.0f} Kg")
        st.metric(label="Crecimiento vs 2024", value=f"{growth_vs_2024:.2f}%")

        # Gráfico de comportamiento
        st.subheader("Evolución de Ventas y Proyección")
        df_melted = filtered_data.melt(
            id_vars=["Codigo Producto", time_col],
            value_vars=["Venta 2023", "Venta 2024", "Venta 2025", "Projection 2025"],
            var_name="Ratio",
            value_name="Valor"
        )
        
        fig = px.line(
            df_melted,
            x=time_col,
            y="Valor",
            color="Codigo Producto",
            line_group="Codigo Producto",
            title="Tendencia de Ventas y Proyecciones",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
