import os
import math
import pandas as pd

# Ajusta estas rutas según tu proyecto:
RELATION_CONE_PATH = "Stock_Optimization/Data/relation_cone_skein.xlsx"
STOCK_DATA_PATH    = "Stock_Optimization/Data/stock_data.csv"         # Tiene Product_Code (conos + ovillos) y Stock
FORECAST_DATA_PATH = "Stock_Optimization/Data/consolidated_forecast.csv"  # Donde tengas proyección (ovillos)
RESULTS_DIR        = "Stock_Optimization/Results"
OUTPUT_FILE        = os.path.join(RESULTS_DIR, "stock_flow_details.csv")

stock_data = pd.read_csv(STOCK_DATA_PATH)
relation_cone_skein = pd.read_excel(RELATION_CONE_PATH)
# Mergear las tablas utilizando la relación entre Cono_Code y Ovillo_Code
merged_data = relation_cone_skein.merge(
    stock_data, left_on='Cono_Code', right_on='Product_Code', how='left'
).rename(columns={'Stock': 'Cono_Stock'})

merged_data = merged_data.merge(
    stock_data, left_on='Ovillo_Code', right_on='Product_Code', how='left'
).rename(columns={'Stock': 'Ovillo_Stock'})

# Calcular el Stock_total
merged_data['Stock_total'] = merged_data['Cono_Stock'].fillna(0) + merged_data['Ovillo_Stock'].fillna(0)

# Seleccionar las columnas relevantes para el resultado final
final_data = merged_data[['Ovillo_Code', 'Cono_Stock', 'Ovillo_Stock', 'Stock_total']]

final_data.to_csv('Stock_Optimization/Results/Stock_Cono_Ovillo.csv', index=False)

# Mostrar el resultado para verificar
print(final_data.head())