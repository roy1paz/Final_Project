import math
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.metrics import calinski_harabasz_score
from sklearn.metrics import davies_bouldin_score


def clustering_score(X, labels):
    unique_labels = np.unique(labels)
    if len(unique_labels) > 1:
        calinski_harabaszre = calinski_harabasz_score(X, labels)
        silhouette = silhouette_score(X, labels)
        davies_bouldin = davies_bouldin_score(X, labels)
    else:
        calinski_harabaszre = 0
        silhouette = -1
        davies_bouldin = math.inf
    
    return calinski_harabaszre, silhouette, davies_bouldin

