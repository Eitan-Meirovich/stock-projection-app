import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Ajustamos la ruta para tener en cuenta la estructura del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

# Añadimos la ruta raíz del proyecto al path de Python
if project_root not in sys.path:
    sys.path.append(project_root)

# Ahora podemos importar el DataLoader desde la ruta correcta
from demand_forecasting_project.src.data.data_loader import DataLoader

class DataProcessor:
    def __init__(self, raw_data_path, processed_data_path, hierarchy_path):
        """
        Initialize the DataProcessor with necessary paths.
        
        Args:
            raw_data_path (str): Ruta a los datos crudos
            processed_data_path (str): Ruta donde se guardarán los datos procesados
            hierarchy_path (str): Ruta al archivo de jerarquía
        """
        self.raw_data_path = os.path.abspath(raw_data_path)
        self.processed_data_path = os.path.abspath(processed_data_path)
        self.hierarchy_path = os.path.abspath(hierarchy_path)
        
        # Aseguramos que existan los directorios necesarios
        os.makedirs(self.processed_data_path, exist_ok=True)
        
        print(f"DataProcessor inicializado con:")
        print(f"- Raw data path: {self.raw_data_path}")
        print(f"- Processed data path: {self.processed_data_path}")
        print(f"- Hierarchy path: {self.hierarchy_path}")
        
    def validate_input(self, data):
        """
        Validate input data structure and contents.
        """
        required_columns = ['Date', 'Product_Code', 'Sales']
        missing_cols = [col for col in required_columns if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Validate data types
        if not pd.api.types.is_datetime64_any_dtype(data['Date']):
            raise ValueError("Date column must be datetime type")
            
        return True
    
    def clean_data(self, data):
        """
        Clean and prepare data for analysis.
        """
        df = data.copy()
        if df.index.name is not None or isinstance(df.index, pd.MultiIndex):
            df = df.reset_index()
            
        # Convert sales to numeric, coercing errors to NaN
        df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
        
        # Remove obvious errors
        df = df[df['Sales'] >= 0]  # Remove negative sales
        
        # Handle missing values using forward fill then backward fill
        df['Sales'] = df.groupby('Product_Code')['Sales'].transform(
            lambda x: x.fillna(method='ffill').fillna(method='bfill')
        )
        
        return df
    
    def remove_outliers(self, data):
        """
        Remove statistical outliers by product and month using IQR method.
        """
        def remove_group_outliers(group):
            if len(group) < 4:  # Skip small groups
                return group
                
            Q1 = group['Sales'].quantile(0.25)
            Q3 = group['Sales'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 2.5 * IQR
            upper_bound = Q3 + 2.5 * IQR
            
            # Replace outliers with boundary values instead of removing
            group.loc[group['Sales'] < lower_bound, 'Sales'] = lower_bound
            group.loc[group['Sales'] > upper_bound, 'Sales'] = upper_bound
            return group
        
        return data.groupby(['Product_Code', data['Date'].dt.month]).apply(remove_group_outliers)
    
    def add_features(self, data):
        """
        Add relevant features for analysis while carefully handling the DataFrame structure.
    
        This function adds time-based features and statistical calculations while ensuring
        we don't create duplicate columns or index conflicts.
    
        Args:
            data (pd.DataFrame): Input DataFrame to add features to
        
        Returns:
            pd.DataFrame: DataFrame with additional features
        """
        # Create a copy to avoid modifying the original data
        df = data.copy()
    
        # Carefully handle the index reset
        if 'Product_Code' in df.index.names:
            # Get the index names that we want to keep as columns
            index_names = [name for name in df.index.names if name not in df.columns]
            # Reset only those indices that won't create duplicates
            if index_names:
                df = df.reset_index(level=index_names)
    
        # Ensure Date is datetime type
        df['Date'] = pd.to_datetime(df['Date'])
    
        # Add time-based features
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Quarter'] = df['Date'].dt.quarter
        df['DayOfWeek'] = df['Date'].dt.dayofweek
        df['WeekOfYear'] = df['Date'].dt.isocalendar().week
    
        # Calculate rolling statistics for different windows
        # Make sure Product_Code is available for grouping
        group_col = 'Product_Code'
        if group_col not in df.columns and group_col in df.index.names:
            df = df.reset_index(level=group_col)
    
        for window in [7, 30, 90]:
            col_name = f'Sales_MA_{window}d'
            df[col_name] = df.groupby(group_col)['Sales'].transform(
                lambda x: x.rolling(window, min_periods=1).mean()
            )
        
            std_col_name = f'Sales_Std_{window}d'
            df[std_col_name] = df.groupby(group_col)['Sales'].transform(
            lambda x: x.rolling(window, min_periods=1).std()
            ).fillna(0)
    
        # Calculate month-over-month growth
        df['Sales_MoM_Growth'] = df.groupby(group_col)['Sales'].transform(
            lambda x: x.pct_change()
        ).fillna(0)
    
        # Add seasonality indicators
        df['IsHighSeason'] = df['Month'].isin([3, 4, 5, 6])
        df['Season'] = pd.cut(df['Month'], 
                         bins=[0, 3, 6, 9, 12], 
                         labels=['Winter', 'Spring', 'Summer', 'Fall'],
                         include_lowest=True)
    
        # Sort the data chronologically within each product
        df = df.sort_values([group_col, 'Date'])
    
        # Print diagnostic information
        print("\nFeature Generation Summary:")
        print(f"Original columns: {list(data.columns)}")
        print(f"New columns added: {[col for col in df.columns if col not in data.columns]}")
        print(f"Total features now: {len(df.columns)}")
    
        return df
    def process(self, filename):
        """
        Main processing pipeline that handles data loading, cleaning, and feature generation.
    
        This method coordinates the entire data processing workflow while providing
        detailed feedback about each step.
    
        Args:
            filename (str): Name of the file to process
        
        Returns:
            pd.DataFrame: Processed DataFrame with all features
        """
        try:
            # Load data
            print(f"\nStarting processing of {filename}")
            loader = DataLoader(self.raw_data_path)
            data = loader.load_data(filename)
        
            # Validate
            print("\nValidating data structure...")
            self.validate_input(data)
            print(f"Initial data shape: {data.shape}")
        
            # Clean data
            print("\nCleaning data...")
            data = self.clean_data(data)
            print(f"Shape after cleaning: {data.shape}")
        
            # Generate features
            print("\nGenerating features...")
            data = self.add_features(data)
            print(f"Final data shape: {data.shape}")
        
            # Sort and deduplicate
            data = data.sort_values(['Product_Code', 'Date'])
            initial_rows = len(data)
            data = data.drop_duplicates()
            if len(data) < initial_rows:
                print(f"Removed {initial_rows - len(data)} duplicate rows")
        
            # Save processed data
            output_file = os.path.join(
                self.processed_data_path, 
                f"processed_{os.path.splitext(filename)[0]}.csv"
            )
            data.to_csv(output_file, index=False)
            print(f"\nProcessing completed successfully. Output saved to: {output_file}")
        
            return data
        
        except Exception as e:
            print(f"\nError processing data: {str(e)}")
            print("Stack trace:")
            import traceback
            traceback.print_exc()
            raise