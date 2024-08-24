import os
import ast
import pandas as pd


def retain_key_zero(range_str):
    ranges_dict = ast.literal_eval(range_str)
    key_zero_dict = {0: ranges_dict.get(0)}
    return key_zero_dict

def sort_and_reassign(range_str):
    # Check if the input is already a dictionary
    if isinstance(range_str, dict):
        ranges_dict = range_str
    else:
        try:
            # Convert string to dictionary if it's not already
            ranges_dict = ast.literal_eval(range_str)
        except ValueError:
            print(f"Error parsing string: {range_str}")
            return range_str  # Return the original string in case of an error

    # Sort the dictionary by the 'MIN' value and reassign keys
    sorted_items = sorted(ranges_dict.items(), key=lambda item: item[1]['MIN'])
    reassigned_dict = {i: item[1] for i, item in enumerate(sorted_items)}
    return str(reassigned_dict)
    
def process_clustering_results(processed_data, results_df, errors_df):
    # first, fix error df
    # remove duplicates clusters
    errors_df['RANGES'] = errors_df['RANGES'].apply(retain_key_zero)
    # Set all values in 'K' column to 1
    errors_df['K'] = 1

    # merge both dataframes results_df, errors_df
    cluster_results_df = pd.concat([results_df, errors_df], ignore_index=True)

    # drop unused meds 
    processed_data = processed_data.rename(columns={'M_GIVEN_WAY_DESC': 'GIVEN_WAY'})
    for index, row in cluster_results_df.iterrows():
        med = row['CODE_ATC']
        way = row['GIVEN_WAY']
        if processed_data[(processed_data['CODE_ATC']==med) & (processed_data['GIVEN_WAY'] == way)].shape[0] == 0:
            cluster_results_df.drop(index, inplace=True)
    
    # Sort the dictionary by the 'MIN' value and reassign keys
    cluster_results_df['RANGES'] = cluster_results_df['RANGES'].apply(sort_and_reassign)

    # add units to the cluster_results_df
    unit_mapping = processed_data.set_index(['CODE_ATC', 'GIVEN_WAY'])['UNIT_OF_MEASURE'].to_dict()
    cluster_results_df['UNIT'] = cluster_results_df.set_index(['CODE_ATC', 'GIVEN_WAY']).index.map(unit_mapping)

    # get from the first cluster the max value
    # cluster_results_df['first_cluster_max_value'] = cluster_results_df['RANGES'].apply(lambda x: ast.literal_eval(x)[0]['MAX'])
    # get from the last cluster the min value
    # cluster_results_df['last_cluster_min_value'] = cluster_results_df['RANGES'].apply(lambda x: ast.literal_eval(x)[-1]['MIN'])

    cluster_results_df.to_csv("cluster_results.csv", index=False)


if __name__ == "__main__":
    processed_data_top_meds_path = os.path.join('..', 'raw_data', 'processed_top_meds_data.csv')
    results_path = 'results.csv'
    errors_path = 'error.csv'
    
    processed_data_df = pd.read_csv(processed_data_top_meds_path, low_memory=False)
    results_df = pd.read_csv(results_path, low_memory=False)
    errors_df = pd.read_csv(errors_path, low_memory=False)

    process_clustering_results(processed_data_df, results_df, errors_df)
