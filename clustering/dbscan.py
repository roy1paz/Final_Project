import math
import pandas as pd
from sklearn.cluster import DBSCAN

from scores import *

def dbscan_model(df):
    df_size = df.shape[0]

    X = df[['M_DOSAGE']].to_numpy()

    results = {'eps': [], 'min_samples': [], 'labels': [], 'silhouette': [], "calinski_harabaszre": [], "davies_bouldin": []}
    eps_values = [0.01, 0.5, 1.0, 1.5, 2.0]
    min_samples_values = [math.ceil(df_size * 0.01), math.ceil(df_size * 0.05), math.ceil(df_size * 0.1), math.ceil(df_size * 0.15)]

    for eps in eps_values:
        for min_samples in min_samples_values:
            try:
                dbscan = DBSCAN(eps=eps, min_samples=min_samples)
                dbscan.fit(X)
                labels = dbscan.labels_

                # DBSCAN can result in some points being labeled as noise (-1),
                # these should not be considered in the evaluation metrics
                if len(set(labels)) > 1:  # Ensure there's at least one cluster plus noise
                    calinski_harabaszre, silhouette, davies_bouldin = clustering_score(X, labels)
                    results['eps'].append(eps)
                    results['min_samples'].append(min_samples)
                    results['labels'].append(labels)
                    results['silhouette'].append(silhouette)
                    results['calinski_harabaszre'].append(calinski_harabaszre)
                    results['davies_bouldin'].append(davies_bouldin)
                else:
                    continue
            except Exception as e:
                continue

    results_df = pd.DataFrame(results)
    return results_df
