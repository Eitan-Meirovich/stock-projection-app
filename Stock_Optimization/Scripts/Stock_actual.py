import pyodbc
import pandas as pd

# Configuración de conexión a SQL Server
SERVER = '186.10.95.240'  # Reemplaza con el nombre de tu servidor
DATABASE = 'tasa_entel_srv'  # Reemplaza con el nombre de tu base de datos
USERNAME = 'tasa_entel_usr'  # Reemplaza con tu usuario
PASSWORD = 't4s43nt3l'  # Reemplaza con tu contraseña

# Consulta SQL para obtener el stock actual
QUERY = """
SELECT KOPR as 'Product_Code', STFI1 AS 'Stock'
FROM MAEPR
WHERE RUPR IN ('R10', 'R20') AND TIPR = 'FPN'
"""

def get_stock_data():
    """
    Conecta a SQL Server, ejecuta la consulta y retorna los datos en un DataFrame.
    """
    try:
        # Establecer la conexión
        connection = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
        )
        print("Conexión a SQL Server exitosa.")

        # Ejecutar la consulta y cargar los datos en un DataFrame
        stock_data = pd.read_sql_query(QUERY, connection)
        connection.close()
        print("Consulta ejecutada y conexión cerrada.")
        
        # Mostrar las primeras filas como verificación
        print(stock_data.head())
        
        return stock_data
    except Exception as e:
        print(f"Error al conectarse a SQL Server o ejecutar la consulta: {e}")
        return None

if __name__ == "__main__":
    stock_data = get_stock_data()
    if stock_data is not None:
        # Guardar los datos en un CSV (opcional)
        stock_data.to_csv("Stock_Optimization/Data/stock_data.csv", index=False)
        print("Datos de stock guardados en 'stock_data.csv'.")
