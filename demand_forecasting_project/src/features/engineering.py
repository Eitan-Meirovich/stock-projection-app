import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class ClusterAnalysis:
    def __init__(self, processed_data_path, output_path):
        self.processed_data_path = processed_data_path
        self.output_path = output_path

    def load_processed_data(self):
        """
        Load the processed data for clustering.
        """
        file_path = f"{self.processed_data_path}/processed_data.csv"
        data = pd.read_csv(file_path)

        # Verificar columnas esenciales
        required_columns = ['Sales', 'Year', 'Month']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Missing required column: {col} in the dataset.")

        return data

    def preprocess_data(self, data):
        """
        Preprocess the data for clustering.
        Normalize numeric variables and select relevant features.
        """
        # Seleccionar columnas relevantes
        features = data[['Sales', 'Year', 'Month', 'Familia', 'Super Familia']]

        # Normalizar las variables numéricas
        scaler = StandardScaler()
        normalized_features = scaler.fit_transform(features)

        return normalized_features

    def determine_optimal_clusters(self, data):
        """
        Determine the optimal number of clusters using the elbow method.
        """
        distortions = []
        K = range(1, 10)
        for k in K:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(data)
            distortions.append(kmeans.inertia_)

        # Plot the elbow curve
        plt.figure(figsize=(8, 5))
        plt.plot(K, distortions, 'bo-')
        plt.title("Elbow Method to Determine Optimal Clusters")
        plt.xlabel("Number of Clusters")
        plt.ylabel("Distortion")
        plt.show()

    def perform_clustering(self, data, n_clusters):
        """
        Perform K-Means clustering and assign clusters to the data.
        """
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(data)
        return clusters

    def save_clustered_data(self, original_data, clusters):
        """
        Save the data with cluster assignments.
        """
        original_data['Cluster'] = clusters
        output_file = f"{self.output_path}/clustered_data.csv"
        original_data.to_csv(output_file, index=False)
        print(f"Clustered data saved to {output_file}")

    def run(self):
        """
        Full clustering pipeline.
        """
        data = self.load_processed_data()
        normalized_data = self.preprocess_data(data)

        # Determine the optimal number of clusters
        self.determine_optimal_clusters(normalized_data)

        # Perform clustering (adjust n_clusters based on the elbow method)
        clusters = self.perform_clustering(normalized_data, n_clusters=3)

        # Save the results
        self.save_clustered_data(data, clusters)

