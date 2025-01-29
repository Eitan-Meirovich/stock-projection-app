import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
 
# Generar algunos datos aleatorios
datos = np.random.normal(0, 3, size=200)
 
# Crear un histograma con color y título personalizados
plt.hist(datos, bins=20, color='skyblue', edgecolor='black')
plt.title('Mi Histograma Personalizado')
 
# Mostrar el histograma en Streamlit
st.pyplot()

import plotly.express as px
 
# Crear una gráfica de dispersión en 3D
fig = px.scatter_3d(x=[1, 2, 3, 4], y=[4, 3, 2, 1], z=[1, 4, 2, 3])
st.plotly_chart(fig)

 
# Datos para graficar
etiquetas = 'Python', 'Java', 'C++', 'JavaScript'
tamaños = [215, 130, 245, 210]
 
# Crear una gráfica circular (tarta)
plt.pie(tamaños, labels=etiquetas, autopct='%1.1f%%')
 
# Mostrar la gráfica en Streamlit
st.pyplot()