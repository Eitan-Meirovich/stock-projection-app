import pandas as pd
import streamlit as st
import numpy as np


# Cargar los datos consolidados
file_path = r"C:\Users\Ukryl\stock-projection-app\Stock_Optimization\Results\consolidado_datos.csv"   # Cambia esto a la ruta donde tengas el archivo

def load_data():
    try:
        data = pd.read_csv(file_path)
        # Convertir la columna Fecha en formato datetime
        data['Fecha'] = pd.to_datetime(data['Fecha'], errors='coerce')

        # Extraer mes de la columna Fecha
        data['Mes'] = data['Fecha'].dt.month

        # Crear columnas de proyección por mes
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        data['Mes Nombre'] = data['Mes'].map({i + 1: mes for i, mes in enumerate(meses)})

        # Agrupar por producto y mes
        grouped = data.groupby(['Super Familia', 'Familia', 'Codigo Producto', 'Stock Total', 'Mes Nombre']).agg({
            'Projection': 'sum'
        }).reset_index()

        # Pivotear para convertir meses en columnas
        pivoted = grouped.pivot(index=['Super Familia', 'Familia', 'Codigo Producto', 'Stock Total'], columns='Mes Nombre', values='Projection').fillna(0).reset_index()

        # Asegurar que todos los meses están presentes como columnas
        for mes in meses:
            if mes not in pivoted.columns:
                pivoted[mes] = 0

        return pivoted
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Calcular los valores por mes y trimestre
def process_data(df):
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    for i, mes in enumerate(meses):
        if i == 0:
            df[mes] = df['Stock Total'] - df[mes]
        else:
            prev_month = meses[i - 1]
            df[mes] = df[prev_month] - df[mes]

    # Calcular trimestres
    df['Primer Trimestre'] = df[['Enero', 'Febrero', 'Marzo']].apply(lambda x: x.sum(), axis=1)
    df['Segundo Trimestre'] = df[['Abril', 'Mayo', 'Junio']].apply(lambda x: x.sum(), axis=1)
    df['Tercer Trimestre'] = df[['Julio', 'Agosto', 'Septiembre']].apply(lambda x: x.sum(), axis=1)
    df['Cuarto Trimestre'] = df[['Octubre', 'Noviembre', 'Diciembre']].apply(lambda x: x.sum(), axis=1)

    return df

# Formatear datos para visualización
def format_data(df):
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_columns:
        df[col] = df[col].apply(lambda x: f"{int(x):,}".replace(",", "."))
    return df

# Aplicar estilos condicionales
def style_data(df):
    def apply_styles(val):
        try:
            val = float(val.replace(".", "").replace(",", "."))  # Convertir a número para la validación
            if val < 0:
                return f'color: red; font-weight: bold;'
            elif val > 0:
                return f'color: blue; font-weight: bold;'
        except:
            return ''

    styled_df = df.style.applymap(apply_styles, subset=df.columns[1:])  # Estilizar columnas desde la segunda en adelante
    return styled_df

# Descargar datos como Excel
def download_excel(df):
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()
    return output.getvalue()

# Simulación con Stock de Seguridad
def simulate_stock_with_safety(df, safety_stock):
    simulated_df = df.copy()
    simulated_df['Stock Total Ajustado'] = simulated_df['Stock Total'] - safety_stock
    cols = list(simulated_df.columns)
    # Mover la columna 'Stock Total Ajustado' al lado de 'Stock Total'
    cols.insert(cols.index('Stock Total') + 1, cols.pop(cols.index('Stock Total Ajustado')))
    simulated_df = simulated_df[cols]
    return simulated_df

# Cargar y procesar los datos
data = load_data()
if data is not None:
    # Procesar los datos
    processed_data = process_data(data)

    # Configuración de Streamlit
    st.set_page_config(layout="wide")
    st.title("Dashboard de Stock")

    st.subheader("Tabla de datos consolidada")

    # Opciones de agrupación
    grouping_option = st.radio(
        "Selecciona el nivel de agrupación:",
        ('Super Familia', 'Familia', 'Codigo Producto')
    )

    # Filtro adicional para Familia cuando se selecciona Código Producto
    family_filter = None
    if grouping_option == 'Codigo Producto':
        family_values = processed_data['Familia'].unique()
        family_filter = st.selectbox("Selecciona una Familia:", options=family_values)
        processed_data = processed_data[processed_data['Familia'] == family_filter]

    # Opciones de filtro dinámico
    grouping_values = processed_data[grouping_option].unique()
    grouping_filter = st.multiselect(f"Selecciona {grouping_option}(s):", options=grouping_values, default=grouping_values)

    # Filtrar datos
    filtered_data = processed_data[processed_data[grouping_option].isin(grouping_filter)]

    # Agrupar por el nivel seleccionado
    if grouping_option == 'Super Familia':
        aggregated_data = filtered_data.groupby('Super Familia').agg(
            {
                'Stock Total': 'sum',
                'Enero': 'sum', 'Febrero': 'sum', 'Marzo': 'sum',
                'Abril': 'sum', 'Mayo': 'sum', 'Junio': 'sum',
                'Julio': 'sum', 'Agosto': 'sum', 'Septiembre': 'sum',
                'Octubre': 'sum', 'Noviembre': 'sum', 'Diciembre': 'sum',
                'Primer Trimestre': 'sum', 'Segundo Trimestre': 'sum',
                'Tercer Trimestre': 'sum', 'Cuarto Trimestre': 'sum'
            }
        ).reset_index()
        columns_to_display = ['Super Familia', 'Stock Total', 'Primer Trimestre', 'Segundo Trimestre', 'Tercer Trimestre', 'Cuarto Trimestre']
    elif grouping_option == 'Familia':
        aggregated_data = filtered_data.groupby(['Super Familia', 'Familia']).agg(
            {
                'Stock Total': 'sum',
                'Enero': 'sum', 'Febrero': 'sum', 'Marzo': 'sum',
                'Abril': 'sum', 'Mayo': 'sum', 'Junio': 'sum',
                'Julio': 'sum', 'Agosto': 'sum', 'Septiembre': 'sum',
                'Octubre': 'sum', 'Noviembre': 'sum', 'Diciembre': 'sum',
                'Primer Trimestre': 'sum', 'Segundo Trimestre': 'sum',
                'Tercer Trimestre': 'sum', 'Cuarto Trimestre': 'sum'
            }
        ).reset_index()
        columns_to_display = ['Super Familia', 'Familia', 'Stock Total', 'Primer Trimestre', 'Segundo Trimestre', 'Tercer Trimestre', 'Cuarto Trimestre']
    else:  # Codigo Producto
        aggregated_data = filtered_data.groupby(['Super Familia', 'Familia', 'Codigo Producto']).agg(
            {
                'Stock Total': 'sum',
                'Enero': 'sum', 'Febrero': 'sum', 'Marzo': 'sum',
                'Abril': 'sum', 'Mayo': 'sum', 'Junio': 'sum',
                'Julio': 'sum', 'Agosto': 'sum', 'Septiembre': 'sum',
                'Octubre': 'sum', 'Noviembre': 'sum', 'Diciembre': 'sum',
                'Primer Trimestre': 'sum', 'Segundo Trimestre': 'sum',
                'Tercer Trimestre': 'sum', 'Cuarto Trimestre': 'sum'
            }
        ).reset_index()
        columns_to_display = ['Super Familia', 'Familia', 'Codigo Producto', 'Stock Total', 'Primer Trimestre', 'Segundo Trimestre', 'Tercer Trimestre', 'Cuarto Trimestre']

    # Opción para mostrar por trimestres o meses
    view_option = st.radio("Selecciona la vista de la tabla:", ("Trimestres", "Meses y Trimestres"))

    # Ajustar datos según la vista seleccionada
    if view_option == "Trimestres":
        aggregated_data = aggregated_data[columns_to_display]

    # Simulación con Stock de Seguridad
    st.subheader("Simulación con Stock de Seguridad")
    safety_stock = st.number_input("Ingresa el Stock de Seguridad:", min_value=0, value=0)
    simulated_data = simulate_stock_with_safety(aggregated_data, safety_stock)

    # Formatear y estilizar datos
    formatted_data = format_data(simulated_data)
    styled_data = style_data(formatted_data)

    # Mostrar tabla estilizada en Streamlit
    st.write(styled_data, unsafe_allow_html=True)

    # Botón para descargar Excel
    st.download_button(
        label="Descargar tabla en Excel",
        data=download_excel(simulated_data),
        file_name="tabla_stock_simulada.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
