import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from data.data_loader import DataLoader

class DataProcessor:
    def __init__(self, raw_data_path, processed_data_path, hierarchy_path):
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        self.hierarchy_path = hierarchy_path
        
    def validate_input(self, data):
        """Validate input data structure and contents"""
        required_columns = ['Date', 'Product_Code', 'Sales']
        missing_cols = [col for col in required_columns if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return True
    
    def clean_data(self, data):
        """Clean and prepare data"""
        df = data.copy()
        
        # Convert data types
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])  # Drop invalid dates
        df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
        
        # Remove obvious errors
        df = df[df['Sales'] >= 0]  # Remove negative sales
        
        # Handle missing values
        df['Sales'] = df['Sales'].fillna(df.groupby(['Product_Code', 
                                                    df['Date'].dt.month])['Sales'].transform('median'))
        return df
    
    def remove_outliers(self, data):
        """Remove statistical outliers by product and month"""
        def remove_group_outliers(group):
            Q1 = group['Sales'].quantile(0.25)
            Q3 = group['Sales'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return group[(group['Sales'] >= lower_bound) & (group['Sales'] <= upper_bound)]
        
        return data.groupby(['Product_Code', data['Date'].dt.month]).apply(remove_group_outliers).reset_index(drop=True)
    
    def add_features(self, data):
        """Add relevant features for analysis"""
        df = data.copy()
        
        # Ensure Product_Code is not in index
        if 'Product_Code' in df.index.names:
            df = df.reset_index()
        
        # Time-based features
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Quarter'] = df['Date'].dt.quarter
        df['DayOfWeek'] = df['Date'].dt.dayofweek
        
        # Lag features
        df['Sales_LastMonth'] = df.groupby('Product_Code')['Sales'].shift(1)
        df['Sales_LastYear'] = df.groupby('Product_Code')['Sales'].shift(12)
        
        return df
    
    def process(self, filename):
        """Main processing pipeline"""
        try:
            # Load data
            loader = DataLoader(self.raw_data_path)
            data = loader.load_data(filename)
            
            # Validate
            self.validate_input(data)
            
            # Process
            data = self.clean_data(data)
            data = self.remove_outliers(data)
            data = self.add_features(data)
            
            # Sort and deduplicate
            data = data.sort_values(by='Date')
            data = data.drop_duplicates()
            
            # Save processed data
            output_file = os.path.join(self.processed_data_path, f"processed_{filename.split('.')[0]}.csv")
            data.to_csv(output_file, index=False)
            
            print(f"Data processing completed successfully. Output saved to: {output_file}")
            return data
            
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            raise
