import numpy as np
import random
import hdbscan
import matplotlib.pyplot as plt
from typing import List
from sklearn.manifold import TSNE
import src.algo.cma_es as ce

def plot_data(data: np.ndarray, cluster_labels: np.array = None):
    plt.figure(figsize=(10, 8))
    if cluster_labels is None:
        cluster_labels = np.zeros(data.shape[0])
    scatter = plt.scatter(data[:, 0], data[:, 1], c=cluster_labels, cmap='viridis', s=1)
    plt.title('Data Points Distribution')
    plt.xlabel('Component 1')
    plt.ylabel('Component 2')
    plt.colorbar(scatter, label='Cluster ID')
    plt.show()

class ClusterSeeds:
    def __init__(self, nums: int, bounds: (int, int), objective_function: callable):
        """
        :param nums: dimensions
        now only support dimensions which are exactly the same
        """
        self.dim = nums
        self._train_data = None
        self._lower_bound = bounds[0]
        self._upper_bound = bounds[1]
        self._obj_func = objective_function

    """
    Using cluster algorithm and generate population for genetic algorithm (CUDA version)
    By UMAP and hdbscan algorithm
    """
    def gen_population_gpu(self, hdbscan_min_cluster_size: int = 10):
        from cuml.manifold import UMAP
        self._train_data = np.unique(self._train_data, axis=0)
        umap_model = UMAP(n_neighbors=15, min_dist=0.3)
        reduced_data = umap_model.fit_transform(self._train_data)
        # cluster with hdbscan
        hdb_cluster = hdbscan.HDBSCAN(min_samples=hdbscan_min_cluster_size)
        cluster_labels = hdb_cluster.fit_predict(reduced_data)
        plot_data(reduced_data, cluster_labels)

        unique_clusters = np.unique(cluster_labels)
        noise_size = 0
        population = []
        for cluster in unique_clusters:
            if cluster == -1:
                noise_size = np.sum(cluster_labels == -1)
                continue  # skip the noise points
            # generate population for generic algorithm
            cluster_points = self._train_data[cluster_labels == cluster]
            cluster_size = cluster_points.shape[0]
            num_samples = int(np.sqrt(cluster_size))
            random_indices = np.random.choice(cluster_size, num_samples, replace=False)
            random_points = cluster_points[random_indices]
            population.extend(random_points)
        print(f"noise: {noise_size}")
        plot_data(umap_model.fit_transform(np.array(population)))
        return population

    """
    Using cluster algorithm and generate population for genetic algorithm (CPU version)
    By t-sne and hdbscan algorithm
    """
    def gen_population_cpu(self, hdbscan_min_cluster_size: int = 10):
        self._train_data = np.unique(self._train_data, axis=0)
        tsne = TSNE(n_components=2, perplexity=30, random_state=42)
        reduced_data = tsne.fit_transform(self._train_data)
        # cluster using hdbscan
        hdb_cluster = hdbscan.HDBSCAN(min_samples=hdbscan_min_cluster_size)
        cluster_labels = hdb_cluster.fit_predict(reduced_data)
        plot_data(reduced_data, cluster_labels)
        unique_clusters = np.unique(cluster_labels)
        noise_size = 0
        population = []
        for cluster in unique_clusters:
            if cluster == -1:
                noise_size = np.sum(cluster_labels == -1)
                continue
            cluster_points = self._train_data[cluster_labels == cluster]
            cluster_size = cluster_points.shape[0]
            num_samples = int(np.sqrt(cluster_size))
            random_indices = np.random.choice(cluster_size, num_samples, replace=False)
            random_points = cluster_points[random_indices]
            population.extend(random_points)
        print(f"noise: {noise_size}")
        plot_data(tsne.fit_transform(np.array(population)))
        return population

    def run_cluster_cma_es(self, train_data: np.ndarray = None, using_gpu: bool = False):
        # if no train data, generate by random, not very useful
        if train_data is None:
            train_data = np.random.randint(self._lower_bound, self._upper_bound, size=(50000, self.dim))
        self._train_data = train_data
        if using_gpu:
            population = self.gen_population_gpu()
        else:
            population = self.gen_population_cpu()

        cma_es_runner = ce.CMA_ES(self.dim, population, self._obj_func, (self._lower_bound, self._upper_bound))
        cma_es_runner.run(num_iterations=50)

    def convert_buffers_int_ndarray(self, buffers: List[bytes]) -> np.ndarray:
        """
        try to parse buffers to ndarray
        and each line must contain dim int
        """
        candidates = []
        for s in buffers:
            try:
                s_decoded = s.decode('utf-8').strip()
                if not s_decoded:
                    continue
                numbers = [int(token) for token in s_decoded.strip().split()]
                if len(numbers) == self.dim:
                    candidates.append(numbers)
            except Exception as e:
                print(f"parse seed error: {e}")
        return np.array(candidates, dtype=np.int32)

    def convert_buffers_unicode_ndarray(self, buffers: List[bytes]) -> np.ndarray:
        """
        try to parse buffers to ndarray
        and each line must contain dim int
        """
        candidates = []
        for s in buffers:
            if not s:
                continue
            temp = []
            for ch in s.strip().split():
                try:
                    i = ord(ch)
                except Exception as e:
                    i = 65533
                temp.append(i)
            candidate = np.array(temp)
            if len(candidate) == self.dim:
                candidates.append(candidate)
        return np.array(candidates, dtype=np.int32)
