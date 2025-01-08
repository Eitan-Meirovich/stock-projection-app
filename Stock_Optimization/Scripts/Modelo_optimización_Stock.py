import pandas as pd
import matplotlib.pyplot as plt
import os

# Rutas de los archivos de entrada
stock_path = 'Data/stock_data.csv'  # Cambia a la ruta correcta de tu archivo
forecast_path = 'Data/consolidated_forecast.csv'  # Cambia a la ruta correcta de tu archivo
relation_path = 'Data/relation_cone_skein.xlsx'  # Archivo con la relación entre conos y ovillos

# Cargar los datos
stock_data = pd.read_csv(stock_path)
forecast_data = pd.read_csv(forecast_path)
relation_data = pd.read_excel(relation_path)

# Combinar los datasets usando la columna 'Product_Code'
combined_data = pd.merge(stock_data, forecast_data, on='Product_Code', how='inner')

# Añadir stock de conos basado en la relación
relation_data = relation_data.rename(columns={"Ovillo_Code": "Product_Code", "Cono_Code": "Cone_Code"})
stock_data = stock_data.rename(columns={"Product_Code": "Cone_Code", "Stock": "Stock_Cones"})
relation_with_stock = pd.merge(relation_data, stock_data, on='Cone_Code', how='left')
relation_with_stock = relation_with_stock.groupby('Product_Code')['Stock_Cones'].sum().reset_index()

# Combinar con el dataset principal
combined_data = pd.merge(combined_data, relation_with_stock, on='Product_Code', how='left')
combined_data['Stock_Cones'] = combined_data['Stock_Cones'].fillna(0)

# Calcular el stock total
combined_data['Stock_Total'] = combined_data['Stock'] + combined_data['Stock_Cones']

# Calcular la proyección acumulada directamente desde 'Forecast_Product'
combined_data['Total_Projection'] = combined_data['Forecast_Product']

# Calcular el flujo acumulado de stock basado en el stock total
def calculate_stock_flow(data):
    stock_flow = []
    available_stock = data['Stock_Total'].iloc[0]

    for projection in data['Total_Projection']:
        available_stock -= projection
        stock_flow.append(available_stock)

    return stock_flow

# Aplicar cálculo de flujo de stock por producto
results_path = 'Results'
os.makedirs(results_path, exist_ok=True)

for super_familia in combined_data['SuperFamily'].unique():
    super_familia_path = os.path.join(results_path, super_familia)
    os.makedirs(super_familia_path, exist_ok=True)

    super_familia_data = combined_data[combined_data['SuperFamily'] == super_familia]

    for familia in super_familia_data['Familia'].unique():
        familia_path = os.path.join(super_familia_path, familia)
        os.makedirs(familia_path, exist_ok=True)

        familia_data = super_familia_data[super_familia_data['Familia'] == familia]

        for product_code in familia_data['Product_Code'].unique():
            product_data = familia_data[familia_data['Product_Code'] == product_code]
            product_monthly = product_data.groupby('Month').agg({
                'Total_Projection': 'sum',
                'Stock_Total': 'sum'
            }).reset_index()

            product_monthly['Stock_Flow'] = calculate_stock_flow(product_monthly)

            # Guardar resultados
            product_file = os.path.join(familia_path, f'{product_code}_details.csv')
            product_monthly.to_csv(product_file, index=False)

            # Generar gráfico
            plt.figure(figsize=(12, 6))
            plt.bar(product_monthly['Month'], product_monthly['Total_Projection'], color='blue', label='Proyección de Demanda')
            plt.plot(product_monthly['Month'], product_monthly['Stock_Flow'], color='orange', marker='o', label='Flujo de Stock Total')
            plt.xlabel('Mes')
            plt.ylabel('Cantidad')
            plt.title(f'Proyecciones de Demanda y Flujo de Stock para {product_code}')
            plt.legend()
            plt.xticks(product_monthly['Month'])
            plt.tight_layout()
            plt.savefig(os.path.join(familia_path, f'{product_code}_stock_projection.png'))
            plt.close()

print("Resultados generados y organizados por super familia, familia y producto en la carpeta 'Results'.")
