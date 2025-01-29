import streamlit as st
from dashboard import main as proyeccion_dashboard
from Stock_Flow_Dashboard import main as stock_dashboard


# Barra lateral para seleccionar la página
page = st.sidebar.selectbox(
    "Seleccione una página",
    ["Proyección de Ventas", "Optimización de Stock"]
)

# Llamar a la función correspondiente según la selección
if page == "Proyección de Ventas":
    proyeccion_dashboard()
elif page == "Optimización de Stock":
    stock_dashboard()
