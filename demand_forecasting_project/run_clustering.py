import sys
# Asegurarte de que Python encuentre los módulos en `src`
sys.path.append('C:/Users/Ukryl/demand_forecasting_project/src')

from features.engineering import ClusterAnalysis

clustering = ClusterAnalysis(
    processed_data_path='data/processed',
    output_path='data/processed'
)
clustering.run()
