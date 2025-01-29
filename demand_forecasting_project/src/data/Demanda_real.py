import pyodbc
import pandas as pd

# Configuración de conexión a SQL Server
SERVER = '186.10.95.240'  # Reemplaza con el nombre de tu servidor
DATABASE = 'tasa_entel_srv'  # Reemplaza con el nombre de tu base de datos
USERNAME = 'tasa_entel_usr'  # Reemplaza con tu usuario
PASSWORD = 't4s43nt3l'  # Reemplaza con tu contraseña

# Consulta SQL para obtener el stock actual
QUERY = """
SELECT DATEFROMPARTS(YEAR(dbo.MAEDDO.FEEMLI), MONTH(dbo.MAEDDO.FEEMLI), 1) AS 'Fecha', SUM(dbo.MAEDDO.CAPRCO1) AS Demanda, dbo.MAEDDO.UD01PR AS unidad, dbo.MAEPR.KOPR AS codigoProducto, 
                  dbo.MAEPR.NOKOPR AS producto, dbo.MAEPR.KOGE AS codigoGenerico, dbo.MAEPR.RUPR AS RUBRO
FROM     dbo.MAEDDO INNER JOIN
                  dbo.MAEPR ON dbo.MAEDDO.KOPRCT = dbo.MAEPR.KOPR
WHERE  (dbo.MAEDDO.FEEMLI BETWEEN '2022-01-01' AND '2025-12-31') AND (dbo.MAEDDO.TIDO = 'FCV') AND (dbo.MAEDDO.TIPR = 'FPN')
GROUP BY DATEFROMPARTS(YEAR(dbo.MAEDDO.FEEMLI), MONTH(dbo.MAEDDO.FEEMLI), 1), dbo.MAEDDO.UD01PR, dbo.MAEDDO.TIDO, dbo.MAEPR.KOPR, dbo.MAEPR.NOKOPR, dbo.MAEPR.KOGE, dbo.MAEPR.UD01PR, dbo.MAEPR.RUPR
"""

def get_demand_data():
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
        demand_data = pd.read_sql_query(QUERY, connection)
        connection.close()
        print("Consulta ejecutada y conexión cerrada.")
        
        # Mostrar las primeras filas como verificación
        print(demand_data.head())
        
        return demand_data
    except Exception as e:
        print(f"Error al conectarse a SQL Server o ejecutar la consulta: {e}")
        return None

if __name__ == "__main__":
    demand_data = get_demand_data()
    if demand_data is not None:
        # Guardar los datos en un CSV (opcional)
        for column in demand_data.select_dtypes(include=["object"]).columns:
            demand_data[column] = demand_data[column].str.strip()

        demand_data.to_csv("demand_forecasting_project/data/input/demand_data.csv", index=False)
        print("Datos de demand guardados en 'demand_data.csv'.")
