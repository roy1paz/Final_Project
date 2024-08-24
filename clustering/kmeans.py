import pandas as pd
from sklearn.cluster import KMeans

from scores import *


def kmeans_model(df):
    X = df[['M_DOSAGE']].to_numpy()
    
    size = len(set(df['M_DOSAGE'].to_list()))
    results = {"k": [], 'labels': [], 'silhouette': [], "calinski_harabaszre": [], "davies_bouldin": []}
    k_range = range(2, min(6, size))
    for k in k_range:
        try:
            kmeans = KMeans(n_clusters=k)
            kmeans.fit(X)
        
            calinski_harabaszre, silhouette, davies_bouldin = clustering_score(X, kmeans.labels_)
            
            results["k"].append(k)
            results["labels"].append(kmeans.labels_)
            results["silhouette"].append(silhouette)
            results["calinski_harabaszre"].append(calinski_harabaszre)
            results["davies_bouldin"].append(davies_bouldin)
        except Exception as e:
            continue

    results_df = pd.DataFrame(results)
    return results_df