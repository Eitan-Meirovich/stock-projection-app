import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar
import os
import numpy as np

# 1. Configuración de página en modo WIDE
st.set_page_config(
    page_title="Dashboard de Gestión de Stock",
    layout="wide"  # <-- Ajusta para usar todo el ancho disponible
)
WINDING_RATE = 500  # Kg por día que se pueden ovillar
MONTH_NAMES_ES = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]

def main():
    st.markdown("""
       <style>
           /* Estilos personalizados */
           :root{
               --primary-color: #1E40AF;
               --secondary-color: #3B82F6;
               --acent: #60A5FA;
               --text-color: #F8FAFC;
           }
           .block-container > {
               padding: 2rem 3rem;
               max-width: 400rem;
               max-height: 500rem;
               margin: 0 auto;
                
            } 
           h1,h2,h3{
               color: var(--primary-color) !important;
               font-family: 'Arial';
               text-align: center !important;
           }
           h1{
               font-size: 3rem !important;
               margin-bottom: 2rem !important;
           }
           h2{
               font-size: 2rem !important;
               margin-bottom: 2rem !important;
           }
           h3{
               font-size: 2rem !important;
               margin-bottom: 2rem !important;
           }
           div.row-widget.stRadio > div {
               display: flex;
               align-items: center;
               text-align: center;
               justify-content: center;
               gap: 2rem;
           }
           div.metric-container {
               display: flex;
               flex-wrap: wrap;
               text-align: center;
               justify-content: center; 
               gap: 2rem;
               margin: 2rem 0;
           }
           div.metric-container > div {
               background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
               border-radius: 12px;
               padding: 1rem;
               box-shadow: 0 1px 3px rgba(0,0,0,0.1);
               transition: transform 0.2s;
               display: flex;
               text-align: center;
               flex-direction: column;
               justify-content: center;
               align-items: center;
           }
           div.metric-container > div:hover {
               transform: translateY(-2px);
           }
           .metric-container h2 {
               font-size: 1.2rem;
               margin-bottom: 0.5rem;
               text-align: center !important;
           }
           .metric-container p {
               font-size: 1.8rem;
               text-align: center !important;
               font-weight: bold;
               margin: 0;
           }
                
           .dataframe {
               font-size: 14px !important;
               border-radius: 8px !important;
               overflow: hidden !important;
               box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
               margin: 1rem auto !important; /* centrar la tabla en la página */
           }
           .dataframe thead th {
               background-color: var(--primary-color) !important;
               color: white!important;
               font-size: 20px !important;
               font-weight: 700 !important;
               padding: 12px !important;
               text-align: center !important;
           }
           .dataframe tbody td {
               padding: 10px !important;
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
           .stTabs [data-baseweb="tab-list"] {
               justify-content: center !important;
               border-bottom: 2px solid #E2E8F0;
           }
           .stTabs [data-baseweb="tab"] {
               padding: 1rem 2rem !important;
               font-weight: 600 !important;
               color: var(--primary-color) !important;
               border: none !important;
               background-color: transparent !important;
               justify-content: center !important;
           }
           .stTabs [data-baseweb="tab-highlight"] {
               background-color: var(--primary-color) !important;
           }
           .stTabs [aria-selected="true"] {
               color: var(--primary-color) !important;
               border-bottom: 2px solid var(--primary-color) !important;
           }
           section[data-testid="stSidebar"] {
               background-color: #F1F5F9;
           }
           section[data-testid="stSidebar"] .block-container {
               border-radius: 12px;
               background: white;
               padding: 1.5rem;
               box-shadow: 0 1px 3px rgba(0,0,0,0.1);
           }
           section[data-testid="stSidebar"] h2 {
               font-size: 1.5rem !important;
               margin-bottom: 1.5rem !important;
               text-align: center !important;
           }
           .stRadio > label {
               padding: 1rem;
               background-color: #F8FAFC;
               border-radius: 6px;
               margin-bottom: 0.5rem;
               transition: all 0.2s;
               text-align: center !important;
               display: block;
           }
           .stRadio > label:hover {
               background-color: #EFF6FF;
           }
       </style>
    """, unsafe_allow_html=True)

    # ----------------------------------------
    # 1. FUNCIONES DE CARGA Y PREPROCESADO
    # ----------------------------------------
    def load_data():
        """Carga los datos de stock y proyecciones."""
        try:
            stock_df = pd.read_csv('./Stock_Optimization/Results/Stock_Cono_Ovillo.csv')
            st.sidebar.markdown("### Stock Data Loaded")
            st.sidebar.markdown(f"Total productos: {len(stock_df)}")

            projection_df = pd.read_csv('./demand_forecasting_project/data/output/Consolidated_forecast.csv')
            projection_df['Date'] = pd.to_datetime(projection_df['Date'])

            # Extraer mes y año
            projection_df['Month'] = projection_df['Date'].dt.month
            projection_df['Year'] = projection_df['Date'].dt.year

            # Agrupar proyecciones
            projection_grouped = projection_df.groupby(
                ['Codigo Producto', 'Familia', 'Super Familia', 'Month']
            ).agg({
                'Projection': 'sum'
            }).reset_index()
            # Crear un diccionario con las proyecciones mensuales
            projection_dict = {}
            for _, row in projection_grouped.iterrows():
                key = row['Codigo Producto']
                if key not in projection_dict:
                    projection_dict[key] = {
                        'Familia': row['Familia'],
                        'SuperFamily': row['Super Familia'],
                        'monthly_projection': {i: 0 for i in range(1, 13)}  # Inicializar todos los meses
                    }
                projection_dict[key]['monthly_projection'][row['Month']] = row['Projection']
        
            # Combinar con datos de stock
            combined_data = []
            for _, stock_row in stock_df.iterrows():
                product_code = stock_row['Ovillo_Code']
                proj_data = projection_dict.get(product_code, {
                    'Familia': 'Sin Familia',
                    'SuperFamily': 'Sin Super Familia',
                    'monthly_projection': {i: 0 for i in range(1, 13)}
                })
            
                combined_row = {
                    'Product_Code': product_code,
                    'Stock_Cones': stock_row['Cono_Stock'],
                    'Stock_Ovillo': stock_row['Ovillo_Stock'],
                    'Stock_Total': stock_row['Stock_total'],
                    'Familia': proj_data['Familia'],
                    'SuperFamily': proj_data['SuperFamily'],
                    'monthly_projection': proj_data['monthly_projection']
                }
                combined_data.append(combined_row)
        
            combined_df = pd.DataFrame(combined_data)

            st.sidebar.markdown("### Diagnóstico Final")
            st.sidebar.markdown(f"Productos totales: {len(combined_df)}")
            st.sidebar.markdown(
                "Productos con proyección: "
                f"{len(combined_df[combined_df['monthly_projection'].apply(lambda x: sum(x.values()) > 0)])}"
            )
        
            return combined_df
        
        except Exception as e:
            st.error(f"Error al cargar los datos: {str(e)}")
            st.error(f"Tipo de error: {e.__class__.__name__}")
            return None

    def get_forecast_months():
        """Obtiene la lista de meses para los próximos 15 meses desde el mes actual."""
        current_date = datetime.now()
        months = []
        for i in range(15):
            future_date = current_date + pd.DateOffset(months=i+1)
            month_name = MONTH_NAMES_ES[future_date.month - 1]
            month_year = f"{month_name} {future_date.year}"
            months.append(month_year)
        return months
        
    def calculate_monthly_flow(item, safety_stock=0):
        """
        Calcula el flujo mensual de stock considerando proyecciones mensuales.
        monthly_flow[mes] = stock remanente en ese mes.
        """
        monthly_flow = {}
        current_stock = item['Stock_Total'] + safety_stock
        monthly_projections = item['monthly_projection']

        current_date = datetime.now()
        for i in range(15):
            future_date = current_date + pd.DateOffset(months=i+1)
            month_key = f"{MONTH_NAMES_ES[future_date.month - 1]} {future_date.year}"
        
            monthly_demand = monthly_projections.get(future_date.month, 0)
            remaining_stock = current_stock - monthly_demand
            monthly_flow[month_key] = remaining_stock
            current_stock = remaining_stock
    
        return monthly_flow
    
    def process_stock_flow(data, safety_stock, grouping_option):
        """Procesa los datos de stock y flujo para cada agrupación (Super Familia, Familia, etc.)."""
        forecast_months = get_forecast_months()
    
        # Definir trimestres
        quarters = {}
        for i, month in enumerate(forecast_months):
            quarter_num = (i // 3) + 1
            if quarter_num not in quarters:
                quarters[quarter_num] = []
            quarters[quarter_num].append(month)

        data['has_associated_cone'] = data['Stock_Cones'] > 0
        data['Stock_Total'] = data['Stock_Total'] + safety_stock
    
        processed_items = []
        for _, item in data.iterrows():
            monthly_flow = calculate_monthly_flow(item, safety_stock)
            item_dict = item.to_dict()
            item_dict['monthly_flow'] = monthly_flow
            processed_items.append(item_dict)

        grouped = pd.DataFrame(processed_items).groupby(grouping_option)
        processed_results = []
        for group, items in grouped:
            monthly_flows = {}
            for month in forecast_months:
                monthly_flows[month] = sum(
                    it['monthly_flow'][month]
                    for it in processed_items if it[grouping_option] == group
                )

            quarterly_data = {}
            for quarter_num, months in quarters.items():
                # El valor del trimestre se tomará como el stock al final del último mes de ese trimestre
                quarterly_data[f'{quarter_num}° Trimestre'] = monthly_flows[months[-1]]

            processed_results.append({
                'group': group,
                'stockCones': items['Stock_Cones'].sum(),
                'stockOvillo': items['Stock_Ovillo'].sum(),
                'stockInitial': items['Stock_Total'].sum(),
                'monthly': monthly_flows,
                'quarterly': quarterly_data,
                'hasStockout': any(val <= 0 for val in monthly_flows.values())
            })

        return processed_results
    
    # ------------------------
    # Funciones para Tablas
    # ------------------------
    def create_detailed_table(data):
        detailed_data = []
        for row in data:
            detailed_row = {
                'Super Familia': row['group'],
                'Stock Conos (Kg)': row['stockCones'],
                'Stock Ovillos (Kg)': row['stockOvillo'],
                'Stock Inicial (Kg)': row['stockInitial'],
                **{f"{month} (Kg)": value for month, value in row['monthly'].items()},
                **{f"{quarter} (Kg)": value for quarter, value in row['quarterly'].items()}
            }
            detailed_data.append(detailed_row)
        return pd.DataFrame(detailed_data)
    
    def create_priority_table(recommendations):
        if not recommendations:
            return None
        df = pd.DataFrame(recommendations)

        def style_priority_table(df):
            def priority_color(val):
                if val == 'Alta':
                    color = 'red'
                elif val == 'Media':
                    color = 'orange'
                else:
                    color = 'green'
                return f'color: {color}'

            return df.style.applymap(priority_color, subset=['Prioridad']).format({
                'Cantidad Necesaria': '{:,.0f}',
                'Conos Disponibles': '{:,.0f}',
                'Días Necesarios': '{:,.0f}'
            }).set_properties(**{'text-align': 'center'})
        return style_priority_table(df)

    # ------------------------
    # Funciones de KPI extras
    # ------------------------
    def calculate_winding_recommendations(data):
        """
        Calcula recomendaciones de ovillado basándose en un umbral
        de demanda vs. stock de conos y ovillos.
        """
        recommendations = []
        for row in data:
            monthly_data = list(row['monthly'].items())
            current_ovillo_stock = row['stockOvillo']
            current_cono_stock = row['stockCones']
            # Proyección anual / 12 => estimación de demanda mensual "teórica"
            monthly_projection = row.get('Projection', 0) / 12 if 'Projection' in row else 0
        
            for idx, (month, projected_stock) in enumerate(monthly_data):
                # months_until_need
                if monthly_projection > 0:
                    months_until_need = idx
                    # Si el stock proyectado < monthly_projection => podría faltar
                    if projected_stock < monthly_projection and current_cono_stock > 0:
                        stock_needed = monthly_projection - projected_stock
                        days_needed = round(min(stock_needed, current_cono_stock) / WINDING_RATE)
                        months_needed = round(days_needed / 29, 1)
                
                        if months_until_need <= 1:
                            priority = 'Alta'
                        elif months_until_need <= 4:
                            priority = 'Media'
                        else:
                            priority = 'Baja'
                
                        recommendations.append({
                            'Mes': month,
                            'Cantidad Necesaria': round(stock_needed),
                            'Conos Disponibles': round(current_cono_stock),
                            'Stock Ovillos': round(current_ovillo_stock),
                            'Días Necesarios': days_needed,
                            'Meses Necesarios': months_needed,
                            'Prioridad': priority,
                            'Grupo': row['group'],
                            'Stock Proyectado': round(projected_stock),
                            'Demanda Mensual': round(monthly_projection)
                        })
                        # Reducir conos disponibles
                        current_cono_stock = max(0, current_cono_stock - stock_needed)
        # Ordenar
        priority_order = {'Alta': 0, 'Media': 1, 'Baja': 2}
        recommendations.sort(key=lambda x: (priority_order[x['Prioridad']], x['Mes']))
        return recommendations

    def calculate_advanced_kpis(processed_data, original_data):
        """
        Calcula KPIs más profundos:
          - Tasa de Agotamiento (porcentaje de meses con stock negativo)
          - Fill Rate (simplificado)
          - Días de Inventario (total stock vs. demanda diaria promedio)
        Nota: El Fill Rate exacto requiere simular demanda satisfecha/insatisfecha.
        Aquí se hace un approach muy sencillo.
        """
        if not processed_data:
            return {"stockout_rate": 0, "fill_rate": 0, "days_of_inventory": 0}
        
        # --- 1) Tasa de Agotamiento ---
        negative_count = 0
        total_months = 0
        
        # Recorremos cada agrupación (ej. cada familia, super familia, etc.)
        for row in processed_data:
            leftover_vals = row['monthly'].values()  # stock resultante mes a mes
            total_months += len(leftover_vals)
            negative_count += sum(1 for val in leftover_vals if val < 0)
        
        stockout_rate = (negative_count / total_months * 100) if total_months else 0

        # --- 2) Fill Rate (simplificado) ---
        # Suponemos que cada vez que stock es negativo un mes, se deja de atender esa parte.
        # Fill Rate = (1 - (Agotamiento)) x 100? 
        # No es exacto, pero sirve de aproximación rápida:
        fill_rate = 100 - stockout_rate if stockout_rate < 100 else 0
        
        # --- 3) Días de Inventario ---
        # Tomamos el stock total de todos los grupos (stockInitial sumado) 
        total_stock = sum(row['stockInitial'] for row in processed_data)
        
        # Sumamos la demanda 12 meses (de la DataFrame original) para tener la "demanda anual"
        # "original_data" = subset de data con 'monthly_projection'
        if original_data is not None and 'monthly_projection' in original_data.columns:
            monthly_demand_12 = 0
            for i in range(1, 13):
                # sumamos la demanda del mes i de todos los productos
                monthly_demand_12 += original_data['monthly_projection'].apply(lambda x: x.get(i, 0)).sum()
        else:
            monthly_demand_12 = 0
        
        # Demanda diaria promedio
        daily_demand = (monthly_demand_12 / (12*30)) if monthly_demand_12 else 0
        
        days_of_inventory = total_stock / daily_demand if daily_demand > 0 else 0

        return {
            "stockout_rate": stockout_rate,     # Porcentaje
            "fill_rate": fill_rate,            # Porcentaje
            "days_of_inventory": days_of_inventory
        }

    # ------------------------
    # Funciones de gráficos
    # ------------------------
    def create_stock_flow_chart(data, view_type='monthly'):
        if view_type == 'monthly':
            monthly_data = []
            for row in data:
                for month, value in row['monthly'].items():
                    monthly_data.append({
                        'Grupo': row['group'],
                        'Período': month,
                        'Stock': value
                    })
            df_plot = pd.DataFrame(monthly_data)
        else:
            quarterly_data = []
            for row in data:
                for quarter, value in row['quarterly'].items():
                    quarterly_data.append({
                        'Grupo': row['group'],
                        'Período': quarter,
                        'Stock': value
                    })
            df_plot = pd.DataFrame(quarterly_data)
        
        fig = go.Figure()
        for grupo in df_plot['Grupo'].unique():
            df_grupo = df_plot[df_plot['Grupo'] == grupo]
            fig.add_trace(go.Scatter(
                x=df_grupo['Período'],
                y=df_grupo['Stock'],
                name=grupo,
                mode='lines+markers',
                line=dict(width=3),
                marker=dict(size=8),
                hovertemplate="<b>%{x}</b><br>Stock: %{y:,.0f} Kg<br><extra></extra>"
            ))

        fig.update_layout(
            title={
                'text': 'Proyección de Stock por Período',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Período",
            yaxis_title="Stock (Kg)",
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            height=500
        )
        fig.update_xaxes(tickangle=45)
        fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Nivel Crítico")
        return fig

    def create_stock_comparison_chart(data):
        stock_comparison = pd.DataFrame([{
            'Grupo': row['group'],
            'Stock Ovillos': row['stockOvillo'],
            'Stock Conos': row['stockCones']
        } for row in data])
    
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Stock Ovillos',
            x=stock_comparison['Grupo'],
            y=stock_comparison['Stock Ovillos'],
            marker_color='#2ecc71'
        ))
        fig.add_trace(go.Bar(
            name='Stock Conos',
            x=stock_comparison['Grupo'],
            y=stock_comparison['Stock Conos'],
            marker_color='#3498db'
        ))
    
        fig.update_layout(
            title={
                'text': 'Distribución de Stock: Ovillos vs Conos',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Grupo de Productos",
            yaxis_title="Stock (Kg)",
            barmode='group',
            height=400,
            plot_bgcolor='white',
            bargap=0.15,
            bargroupgap=0.1
        )
        return fig

    # ------------------------
    # Funciones de Formato
    # ------------------------
    def format_number(value):
        return f"{value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def style_dataframe(df):
        def cell_style(val, is_numeric=True):
            try:
                val = float(val) if is_numeric else val
                if is_numeric:
                    color = 'blue' if val > 0 else 'red'
                    return f'color: {color}; font-weight: bold; text-align: center'
                return 'text-align: left'
            except:
                return 'text-align: left'

        styled = df.style
        for col in df.columns:
            is_numeric = (col != 'Grupo')
            styled = styled.applymap(lambda x: cell_style(x, is_numeric), subset=[col])

        return (styled.format({col: format_number for col in df.columns if col != 'Grupo'})
                    .set_properties(**{'text-align': 'center', 'width': '120px'})
                    .set_table_styles([
                        {'selector': 'th', 'props': [('text-align', 'center')]},
                        {'selector': 'td', 'props': [('text-align', 'center')]}
                    ]))

    def create_summary_table(data, view_type="Mensual", table_type="Resumida"):
        if table_type == "Detallada":
            cols = ['Grupo', 'Stock Conos (Kg)', 'Stock Ovillos (Kg)', 'Stock Inicial (Kg)']
        else:
            cols = ['Grupo', 'Stock Inicial (Kg)']
    
        if view_type == "Mensual":
            monthly_cols = [f"{month} (Kg)" for month in data[0]['monthly'].keys()]
            cols.extend(monthly_cols)
        else:
            quarterly_cols = [f"{quarter} (Kg)" for quarter in data[0]['quarterly'].keys()]
            cols.extend(quarterly_cols)
        
        table_data = []
        for row in data:
            table_row = {
                'Grupo': row['group'],
                'Stock Inicial (Kg)': row['stockInitial']
            }
            if table_type == "Detallada":
                table_row.update({
                    'Stock Conos (Kg)': row['stockCones'],
                    'Stock Ovillo (Kg)': row['stockOvillo'] if 'stockOvillo' in row else row['stockOvillo']
                })
            
            if view_type == "Mensual":
                table_row.update({
                    f"{month} (Kg)": value
                    for month, value in row['monthly'].items()
                })
            else:
                table_row.update({
                    f"{quarter} (Kg)": value
                    for quarter, value in row['quarterly'].items()
                })
            table_data.append(table_row)
    
        df = pd.DataFrame(table_data)
        # Reordenar columnas en el orden deseado
        df = df[[c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]]
        return df

    # --------------------------
    #           FLUJO
    # --------------------------
    data = load_data()

    if data is not None:
        with st.sidebar:
            st.header("Configuración")
            st.markdown("---")

            safety_stock = st.number_input(
                "Stock de Seguridad (Kg)",
                min_value=0,
                value=0,
                step=100,
                help="Cantidad adicional de stock para mantener como seguridad"
            )

            grouping_option = st.radio(
                "Nivel de agrupación",
                ('Super Familia', 'Familia', 'Codigo Producto'),
                index=0
            )

            column_mapping = {
                'Super Familia': 'SuperFamily',
                'Familia': 'Familia',
                'Codigo Producto': 'Product_Code'
            }

            # Filtro por Familia si grouping = "Codigo Producto"
            if grouping_option == 'Codigo Producto':
                if "Familia" in data.columns:
                    all_families = sorted(data["Familia"].dropna().unique())
                    selected_family = st.selectbox(
                        "Selecciona una Familia (opcional):",
                        options=["(Ver todas)"] + list(all_families)
                    )
                    if selected_family != "(Ver todas)":
                        data = data[data['Familia'] == selected_family]

            # Multiselect de grupos
            all_group_values = sorted(data[column_mapping[grouping_option]].dropna().unique())
            grouping_filter = st.multiselect(
                f"Selecciona {grouping_option}(s):",
                options=all_group_values,
                default=all_group_values
            )
        
            if not grouping_filter:
                grouping_filter = all_group_values
        
            data_filtered = data[data[column_mapping[grouping_option]].isin(grouping_filter)]
            processed_data = process_stock_flow(data_filtered, safety_stock, column_mapping[grouping_option])

        # KPIs principales ---------------------------------------
 
        current_month = datetime.now().month
        next_3_months = [(current_month + i - 1) % 12 + 1 for i in range(1, 4)]

        total_demanda_3m = 0
        for _, row in data_filtered.iterrows():
            demanda_sku = 0
            for mes in next_3_months:
                demanda_sku += row['monthly_projection'][mes]
            total_demanda_3m += demanda_sku

        total_stock = sum(row['stockInitial'] for row in processed_data)
        productos_riesgo = sum(1 for row in processed_data if row['hasStockout'])

        # Demanda 3 meses aprox (ver tu lógica original)
        if total_demanda_3m > 0:
            cobertura = (total_stock / (total_demanda_3m / 3))
        else:
            cobertura = "N/A"

        # Eficiencia => ratio Ovillos/Total
        total_ovillos = sum(row['stockOvillo'] for row in processed_data)
        eficiencia = (total_ovillos / total_stock * 100) if total_stock else 0

        # Formateamos
        formatted_Total_stock = format_number(total_stock)
        formatted_producto_riesgo = format_number(productos_riesgo)
        formatted_cobertura = (
            f"{cobertura:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if isinstance(cobertura, (int, float)) else "N/A"
        )
        formatted_eficiencia = f"{eficiencia:.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        st.title("🧶 Dashboard de Gestión de Stock")

        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
        
        kpi_labels = [
            ("Stock Total", formatted_Total_stock, "Total stock available in Kg"),
            ("N°Productos en Riesgo", formatted_producto_riesgo, "Number of products at risk of stockout"),
            ("Meses de cobertura", formatted_cobertura, "Months of coverage based on current stock and demand"),
            ("% Eficiencia", formatted_eficiencia, "Efficiency percentage of stock usage")
        ]
    
        for col, (title, value, tooltip) in zip(cols, kpi_labels):
            col.metric(label=title, value=value, help=tooltip)

            # Tabs principales ---------------------------------------
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Análisis de Stock",
            "⚠️ Alertas y Prioridades",
            "📈 Proyecciones",
            "📐 KPIs Avanzados"
        ])

        # ------------------ TAB 1: Análisis de Stock
        with tab1:
            col1, col2 = st.columns([1, 2])
            with col1:
                view_type = st.selectbox("Visualización", ["Mensual", "Trimestral"], key="view_type")
            with col2:
                table_type = st.selectbox("Desglose", ["Resumida", "Detallada"], key="table_type")
            
            st.markdown("<h3 style='text-align: center'>Resumen de Stock</h3>", unsafe_allow_html=True)

            if processed_data:
                df = create_summary_table(processed_data, view_type, table_type)
                st.dataframe(style_dataframe(df), use_container_width=True, height=400)
            else:
                st.info("No hay datos para mostrar en la tabla.")

        # ------------------ TAB 2: Alertas y Prioridades
        with tab2:
            st.markdown("<h3 style='text-align: center'>Alertas de Stock</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 3])
            with col1:
                priority_filter = st.selectbox("Filtrar por prioridad", ["Todas", "Alta", "Media", "Baja"])
    
            recommendations = calculate_winding_recommendations(processed_data)
    
            if recommendations:
                if priority_filter != "Todas":
                    recommendations = [r for r in recommendations if r['Prioridad'] == priority_filter]
                if recommendations:
                    priority_table = create_priority_table(recommendations)
                    st.dataframe(
                        priority_table,
                        use_container_width=True,
                        height=400
                    )
                else:
                    st.info(f"No hay alertas con prioridad {priority_filter}")
            else:
                st.info("No hay alertas de stock que mostrar")

        # ------------------ TAB 3: Proyecciones
        with tab3:
            st.plotly_chart(
                create_stock_flow_chart(
                    processed_data,
                    'monthly' if view_type == "Mensual" else 'quarterly'
                ),
                use_container_width=True
            )

        # ------------------ TAB 4: KPIs Avanzados
        with tab4:
            st.markdown("<h3 style='text-align: center'>KPIs Avanzados</h3>", unsafe_allow_html=True)
            if not processed_data:
                st.info("No hay datos para calcular KPIs Avanzados.")
            else:
                adv_kpis = calculate_advanced_kpis(processed_data, data_filtered)

                # Mostramos en 3 métricas
                colA, colB, colC = st.columns(3)
                # Tasa de Agotamiento
                tasa_agot = f"{adv_kpis['stockout_rate']:.2f}%"
                colA.metric(
                    label="Tasa de Agotamiento",
                    value=tasa_agot,
                    help="Porcentaje de meses (en el horizonte) con stock < 0"
                )
                # Fill Rate
                fill_rate_val = f"{adv_kpis['fill_rate']:.2f}%"
                colB.metric(
                    label="Nivel de Servicio (Fill Rate)",
                    value=fill_rate_val,
                    help="Porcentaje de demanda teóricamente atendida (aprox)."
                )
                # Días de Inventario
                days_inventory = f"{adv_kpis['days_of_inventory']:.1f}"
                colC.metric(
                    label="Días de Inventario",
                    value=days_inventory,
                    help="Cuántos días de cobertura habría según demanda anualizada."
                )

                st.write("Estos KPIs se basan en una **aproximación**: si necesitas un cálculo más preciso (sobre todo para Fill Rate), deberías simular la demanda satisfecha mes a mes con la demanda real/proyectada.")

if __name__ == "__main__":
    main()
