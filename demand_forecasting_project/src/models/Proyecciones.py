import pandas as pd
import numpy as np
from datetime import datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os
import warnings
warnings.filterwarnings('ignore')

def save_historical_forecast(forecast_df, category_name, forecast_date):
    """
    Guarda el pronóstico en un archivo histórico con la fecha en que se realizó,
    reemplazando sólo los meses que correspondan a la nueva proyección.
    """
    history_dir = f'C:\\Users\\Ukryl\\stock-projection-app\\demand_forecasting_project\\data\\forecast_history\\{category_name}'
    os.makedirs(history_dir, exist_ok=True)
    
    # Convertir a datetime para asegurar formatos
    forecast_df = forecast_df.copy()
    forecast_df['Date'] = pd.to_datetime(forecast_df['Date'])
    
    # Añadir columnas informativas
    forecast_df['Forecast_Date'] = forecast_date.strftime('%Y-%m-%d')  # fecha en que se corre el modelo
    forecast_df['Creation_Time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    history_file = os.path.join(history_dir, f'forecast_history_{category_name}.csv')
    
    if os.path.exists(history_file):
        history_df = pd.read_csv(history_file)
        history_df['Date'] = pd.to_datetime(history_df['Date'], errors='coerce')
        
        # 1) Eliminar del histórico cualquier registro cuyas fechas de pronóstico
        #    estén en el mismo rango que estamos recalculando.
        min_new_date = forecast_df['Date'].min()
        max_new_date = forecast_df['Date'].max()
        
        mask = (history_df['Date'] >= min_new_date) & (history_df['Date'] <= max_new_date)
        history_df = history_df[~mask]  # nos quedamos con lo fuera de ese rango
        
        # 2) Agregar el nuevo pronóstico
        history_df = pd.concat([history_df, forecast_df], ignore_index=True)
    else:
        history_df = forecast_df
    
    # Guardar histórico actualizado
    history_df.to_csv(history_file, index=False)
    print(f"Histórico de proyecciones actualizado en: {history_file}")


def load_historical_forecast(category_name, target_date=None):
    """
    Carga las proyecciones históricas para una fecha específica.
    Si no se especifica fecha, devuelve todo el histórico.
    """
    history_file = f'C:\\Users\\Ukryl\\stock-projection-app\\demand_forecasting_project\\data\\forecast_history\\{category_name}\\forecast_history_{category_name}.csv'
    
    if not os.path.exists(history_file):
        return None
    
    try:
        history_df = pd.read_csv(history_file)
        
        # Convertir las fechas asegurando el formato correcto
        history_df['Date'] = pd.to_datetime(history_df['Date']).dt.strftime('%Y-%m-%d')
        history_df['Forecast_Date'] = pd.to_datetime(history_df['Forecast_Date'])
        
        if target_date:
            target_date = pd.to_datetime(target_date)
            return history_df[history_df['Forecast_Date'] == target_date]
        
        return history_df
    
    except Exception as e:
        print(f"Error al cargar el histórico: {str(e)}")
        return None
    
def setup_forecast_periods():
    """Configura los períodos de entrenamiento y pronóstico."""
    current_date = datetime.now()
    
    if current_date.day > 28:
        if current_date.month == 12:
            forecast_start = pd.Timestamp(current_date.year + 1, 1, 1)
        else:
            forecast_start = pd.Timestamp(current_date.year, current_date.month + 1, 1)
    else:
         forecast_start = pd.Timestamp(current_date.year, current_date.month, 1)

    forecast_periods = 15  # Pronóstico de 15 meses

    train_end = forecast_start - pd.DateOffset(days=1)
    train_start = pd.Timestamp('2022-01-01')  # Datos desde 2022

    # Debug info
    print(f"Fecha actual: {current_date}")
    print(f"Inicio de pronóstico: {forecast_start}")
    print(f"Períodos a pronosticar: {forecast_periods}")
    
    return current_date, train_start, train_end, forecast_start, forecast_periods

def load_and_prepare_data(file_path, train_start, train_end):
    """Carga y prepara los datos para el pronóstico."""
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'])
    
    # Filtrar datos entre train_start y train_end inclusive
    mask = (data['Date'] >= train_start) & (data['Date'] <= train_end)
    train_data = data[mask]
    
    monthly_sales = (train_data.groupby(train_data['Date'].dt.to_period('M'))['Sales']
                              .sum()
                              .reset_index())
    monthly_sales['Date'] = monthly_sales['Date'].dt.to_timestamp()
    monthly_sales.set_index('Date', inplace=True)
    
    return data, monthly_sales

def generate_forecast(monthly_sales, forecast_periods, use_seasonal=True):
    """Genera pronósticos usando el modelo apropiado según los datos disponibles."""
    n_observations = len(monthly_sales)
    
    if n_observations >= 24 and use_seasonal:
        # Si tenemos suficientes datos, usamos modelos estacionales
        print("Usando modelos estacionales...")
        
        # Holt-Winters
        hw_model = ExponentialSmoothing(
            monthly_sales['Sales'],
            seasonal='add',
            seasonal_periods=12,
            trend='add'
        ).fit()
        hw_forecast = hw_model.forecast(steps=forecast_periods)
        
        # SARIMA
        sarima_model = SARIMAX(
            monthly_sales['Sales'],
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 12)
        ).fit(disp=False)
        sarima_forecast = sarima_model.get_forecast(steps=forecast_periods)
        
        # Combinar pronósticos
        forecast = 0.5 * hw_forecast + 0.5 * sarima_forecast.predicted_mean
        
    else:
        # Si tenemos pocos datos, usamos un modelo más simple
        print("Usando modelo simple debido a datos limitados...")
        
        model = ExponentialSmoothing(
            monthly_sales['Sales'],
            trend='add',
            seasonal=None
        ).fit()
        
        forecast = model.forecast(steps=forecast_periods)
    
    return forecast

def run_forecast(category_name, file_path):
    """Ejecuta el pronóstico para una categoría específica."""
    print(f"\n=== Pronóstico para categoría: {category_name} ===")
    
    # 1) Configurar periodos
    current_date, train_start, train_end, forecast_start, forecast_periods = setup_forecast_periods()
    
    # 2) Cargar y preparar datos de entrenamiento
    data, monthly_sales = load_and_prepare_data(file_path, train_start, train_end)
    
    # 3) Generar pronóstico de 15 meses
    forecast_values = generate_forecast(monthly_sales, forecast_periods, use_seasonal=True)
    
    # Crear DF con las fechas de pronóstico mensuales
    forecast_dates = pd.date_range(start=forecast_start, periods=forecast_periods, freq='M')
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Forecast_Sales': forecast_values
    })
    
    # 4) Guardar la proyección actual en carpeta específica (si quieres archivo "sueltos")
    output_dir = f'C:\\Users\\Ukryl\\stock-projection-app\\demand_forecasting_project\\data\\processed\\{category_name}'
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'Proyección_15MM_{category_name}.csv'
    
    forecast_df.to_csv(os.path.join(output_dir, output_file), index=False)
    print(f"Proyecciones guardadas en '{os.path.join(output_dir, output_file)}'")
    
    # 5) Guardar/actualizar el histórico (solo sobreescribiendo los 15 meses nuevos)
    save_historical_forecast(forecast_df.copy(), category_name, current_date)
    
    # 6) (Opcional) comparar con pronóstico anterior
    #    Ejemplo: pronóstico del mes pasado:
    try:
        last_month = current_date - pd.DateOffset(months=1)
        last_forecast = load_historical_forecast(category_name, last_month)
        if last_forecast is not None and not last_forecast.empty:
            print("\nComparación con proyección anterior:")
            comparison_df = pd.merge(
                forecast_df,
                last_forecast[['Date', 'Forecast_Sales']],
                on='Date',
                how='left',
                suffixes=('_Current', '_Previous')
            )
            comparison_df['Difference'] = comparison_df['Forecast_Sales_Current'] - comparison_df['Forecast_Sales_Previous']
            print(comparison_df.to_string(index=False))
    except Exception as e:
        print(f"No se pudo cargar la comparación con el mes anterior: {str(e)}")


def main():
    categories = {
        'Invierno': 'processed_data_invierno.csv',
        'Verano': 'processed_data_hilos verano.csv',
        'Bebé': 'processed_data_bebé.csv'
    }
    
    base_path = r'C:\Users\Ukryl\stock-projection-app\demand_forecasting_project\data\processed'
    
    for category, filename in categories.items():
        file_path = os.path.join(base_path, filename)
        run_forecast(category, file_path)

if __name__ == "__main__":
    main()
