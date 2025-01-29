import os
import pandas as pd
import numpy as np

class DataLoader:
    def __init__(self, raw_data_path):
        """
        Inicializa el DataLoader con la ruta a los datos crudos.
        
        Args:
            raw_data_path (str): Ruta al directorio que contiene los archivos de datos
        """
        self.raw_data_path = os.path.abspath(raw_data_path)
        print(f"DataLoader inicializado con ruta: {self.raw_data_path}")
        
        # Define mapeos de columnas posibles para manejar diferentes formatos de entrada
        self.column_mappings = [
            {'Fecha': 'Date', 'Codigo Producto': 'Product_Code', 'Venta': 'Sales'},
            {'Date': 'Date', 'Product_Code': 'Product_Code', 'Sales': 'Sales'},
            {'Fecha': 'Date', 'codigoProducto': 'Product_Code', 'Demanda': 'Sales'}
        ]

    def load_data(self, filename):
        """
        Carga y procesa los datos del archivo especificado.
        
        Args:
            filename (str): Nombre del archivo a cargar
            
        Returns:
            pd.DataFrame: DataFrame con los datos procesados
        """
        # Construir la ruta completa al archivo
        file_path = os.path.join(self.raw_data_path, filename)
        print(f"Intentando cargar archivo: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No se encontró el archivo: {file_path}")
            
        # Determinar el tipo de archivo y leer
        file_extension = os.path.splitext(filename)[1].lower()
        try:
            if file_extension == '.xlsx':
                data = pd.read_excel(file_path)
            elif file_extension == '.csv':
                data = pd.read_csv(file_path)
            else:
                raise ValueError(f"Tipo de archivo no soportado: {file_extension}")
        except Exception as e:
            raise Exception(f"Error al leer el archivo {filename}: {str(e)}")

        # Intentar diferentes mapeos de columnas
        data_mapped = None
        for mapping in self.column_mappings:
            try:
                data_temp = data.rename(columns=mapping)
                if all(col in data_temp.columns for col in ['Date', 'Product_Code', 'Sales']):
                    data_mapped = data_temp
                    break
            except:
                continue
        
        if data_mapped is None:
            raise ValueError("No se pudo mapear las columnas del archivo a los nombres requeridos")

        # Procesar fechas
        data_mapped['Date'] = pd.to_datetime(data_mapped['Date'], errors='coerce')
        data_mapped = data_mapped.dropna(subset=['Date'])
        data_mapped = data_mapped[data_mapped['Date'].dt.year >= 2020]

        print(f"Datos cargados exitosamente de {filename}")
        print(f"Dimensiones del DataFrame: {data_mapped.shape}")
        return data_mapped