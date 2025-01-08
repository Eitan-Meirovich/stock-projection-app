import pandas as pd

class DataLoader:
    def __init__(self, raw_data_path):
        self.raw_data_path = raw_data_path

    def load_data(self, filename):
        """
        Cargar el archivo desde la ruta especificada y limpiar las fechas.
        """
        file_path ='data/input/data.xlsx' # Ajusta según la ruta de tu archivo
        data = pd.read_excel(file_path)  # Ajusta según el formato del archivo

        # Renombrar columnas para asegurar consistencia
        column_mapping = {
            'Fecha': 'Date',
            'Codigo Producto': 'Product_Code',
            'Venta': 'Sales'
        }
        data.rename(columns=column_mapping, inplace=True)

        # Validar y limpiar fechas
        if 'Date' not in data.columns:
            raise ValueError("La columna 'Date' no se encuentra en el archivo de entrada.")

        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')  # Convertir fechas inválidas a NaT
        data = data.dropna(subset=['Date'])  # Eliminar filas con fechas nulas
        data = data[data['Date'].dt.year >= 2020]  # Filtrar fechas menores a 2020
        data['Date'] = data['Date'].dt.date  # Eliminar la hora y dejar solo la fecha
        print("Datos cargados y fechas validadas exitosamente.")
        return data