import os
import warnings
from sklearn.exceptions import ConvergenceWarning

import pandas as pd
from collections import Counter
from tqdm import tqdm

from kmeans import kmeans_model
from dbscan import dbscan_model
from agglomerative import agglomerative_model

warnings.simplefilter("ignore", category=ConvergenceWarning)


def check_range_intersections(ranges_dict):
    # Extract all ranges from the dictionary
    if len(ranges_dict) > 2:
        return False
    
    all_ranges = [(key, ranges_dict[key]['MIN'], ranges_dict[key]['MAX']) for key in ranges_dict]

    # Compare each pair of ranges for intersection
    num_ranges = len(all_ranges)
    for i in range(num_ranges):
        for j in range(i + 1, num_ranges):
            # Get the min and max for the first range
            min_i, max_i = all_ranges[i][1], all_ranges[i][2]
            # Get the min and max for the second range
            min_j, max_j = all_ranges[j][1], all_ranges[j][2]
            # Check for intersection
            if (min_i <= max_j) and (max_i >= min_j):
                return True  # Return True if any intersection is found
    return False  # Return False if no intersections are found


def get_cluster_borders(df, k):
     # Determine cluster borders
    clusters_borders = {}
    for i in range(k):
        cluster_data = df[df['cluster'] == i]['M_DOSAGE']
        clusters_borders[i] = {"MIN": cluster_data.min(), "MAX": cluster_data.max()}
    return clusters_borders


def most_frequent_number(lst):
    # Count the frequency of each element in the list
    counter = Counter(lst)
    # Find the element with the highest frequency
    most_common = counter.most_common(1)  # Returns the list of the most common element and its count
    return most_common[0][0]  # Return the element


def majority_k(df):
    # Find the k values corresponding to the highest rank for each metric
    if not df['calinski_harabaszre'].isna().all():
        calinski_k = df.loc[df['calinski_harabaszre'].idxmax(), 'k']
    else:
        calinski_k = 1
    if not df['silhouette'].isna().all():
        silhouette_k = df.loc[df['silhouette'].idxmax(), 'k']
    else:
        silhouette_k = 1
    if not df['davies_bouldin'].isna().all():
        davies_bouldin_k = df.loc[df['davies_bouldin'].idxmin(), 'k']
    else:
        davies_bouldin_k = 1

    # Count the most frequent k value, first score in the list is the defoult value
    k_options = [silhouette_k, calinski_k, davies_bouldin_k]
    if set(k_options) == 3:
        # No majority! so choose by silhouette score, K = k_options[0]
        return k_options[0]
    else:
        best_k = most_frequent_number(k_options)
        return best_k


def dbscan_majority_k(df):
    # Find the best parameter settings for each metric
    try:
        best_silhouette_sett = df.loc[df['silhouette'].idxmax(), ['eps', 'min_samples']]
        best_calinski_sett = df.loc[df['calinski_harabaszre'].idxmax(), ['eps', 'min_samples']]
        best_davies_sett = df.loc[df['davies_bouldin'].idxmin(), ['eps', 'min_samples']]

        # Collect all best settings in a list
        settings_options = [tuple(best_silhouette_sett), tuple(best_calinski_sett), tuple(best_davies_sett)]
        most_frequent_setting = most_frequent_number(settings_options)

        settings_index = df[(df['eps'] == most_frequent_setting[0]) & (df['min_samples'] == most_frequent_setting[1])].index[0]
        best_result = df.loc[settings_index]

        best_k = len(set(best_result["labels"])) - (1 if -1 in best_result["labels"] else 0) 
        return best_k, most_frequent_setting
    except Exception as e:
        return 1, None


if __name__ == "__main__":

    if not os.path.exists('cluster_results'):
            os.makedirs('cluster_results')
            
    level = ['level_4', 'level_3','level_2', 'level_1', 'CODE_ATC']
    for med_level in level:
        path = os.path.join('..', 'raw_data', f'results/processed_data_{med_level}.csv')
        columns = [med_level, 'GIVEN_WAY', 'K', 'RANGES']
        results_df = pd.DataFrame(columns=columns)
        error_df = pd.DataFrame(columns=columns)
        results_csv_path = f'cluster_results/{med_level}_results.csv'
        error_csv_path = f'cluster_results/{med_level}_error.csv'

        df = pd.read_csv(path, low_memory=False)

        medications = df[med_level].unique()

        # iterate over each medications and given way, and get the cluster label for the dosages 
        for med in tqdm(medications):
            given_way = df[df[med_level] == med]['M_GIVEN_WAY_DESC'].unique()
            for way in given_way:
                df_filtered = df[(df[med_level] == med) & (df['M_GIVEN_WAY_DESC'] == way)].copy()
                
                if df_filtered.empty:
                    continue

                dosage = df_filtered[['M_DOSAGE']].to_numpy()
                
                # kmeans
                kmeans_df = kmeans_model(df_filtered)
                kmeans_k = majority_k(kmeans_df)

                # dbscan
                dbscan_df = dbscan_model(df_filtered)
                dbscan_k, dbscan_settings = dbscan_majority_k(dbscan_df)

                # agglomerative
                # if both models are not agree on the same k, check with agglomerative
                if kmeans_k != dbscan_k:
                    # No majority! choose agglomerative
                    agglomerative_df = agglomerative_model(df_filtered)
                    best_k = majority_k(agglomerative_df)
                    if best_k == 1:
                        # only one cluster so all labels are the same
                        labels = [0] * df_filtered.shape[0]
                    else:
                        labels = agglomerative_df[agglomerative_df['k'] == best_k]["labels"].iloc[0]
                else:
                    # we have a majority, kmeans and dbscan agree on the K value
                    best_k = dbscan_k
                    # we can take also kmeans labels
                    if dbscan_settings == None:
                        # only one cluster so all labels are the same
                        labels = [0] * df_filtered.shape[0]
                    else:    
                        labels = dbscan_df[(dbscan_df['eps'] == dbscan_settings[0]) & (dbscan_df['min_samples'] == dbscan_settings[1])]["labels"].iloc[0]
                
                # insert cluster labels
                df_filtered["cluster"] = labels

                # cluster ranges {0: {min: , max: },}
                clusters_borders = get_cluster_borders(df_filtered, best_k)

                # check for intersections
                if check_range_intersections(clusters_borders):
                    # insert to intersection errors dataframe
                    error_row = pd.DataFrame([{
                        med_level: med,
                        'GIVEN_WAY': way,
                        'K': best_k,
                        'RANGES': clusters_borders
                    }])
                    error_row.to_csv(error_csv_path, mode='a', header=not os.path.exists(error_csv_path), index=False)
                else:
                    # insert to result dataframe
                    result_row = pd.DataFrame([{
                        med_level: med,
                        'GIVEN_WAY': way,
                        'K': best_k,
                        'RANGES': clusters_borders
                    }])
                    result_row.to_csv(results_csv_path, mode='a', header=not os.path.exists(results_csv_path), index=False)
        
