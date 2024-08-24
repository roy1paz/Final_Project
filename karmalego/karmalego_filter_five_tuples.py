import os
import pandas as pd


def filter_five_tuples(ids_to_filter):
    if not os.path.exists('filter_karmalego_five_tuple_results'):
        os.makedirs('filter_karmalego_five_tuple_results')
    
    labels = ["cancer", "cardiac"]
    columns = ['CODE_ATC', 'level_1', 'level_2', 'level_3', 'level_4']
    for label in labels:
        if not os.path.exists(f'filter_karmalego_five_tuple_results/{label}'):
            os.makedirs(f'filter_karmalego_five_tuple_results/{label}')
        for col in columns:
            path = f'karmalego_five_tuple_results/{label}/{label}_{col}_home_hospital_meds_vertical.csv'
            df = pd.read_csv(path)
            filtered_df = df[df['PatientID'].isin(ids_to_filter)]
            filtered_df.to_csv(f'filter_karmalego_five_tuple_results/{label}/{label}_{col}_home_hospital_meds_vertical.csv', index=False)
            print(f'Finished to filter file: {label}_{col}_home_hospital_meds_vertical.csv')
    
    
if __name__ == "__main__":
    lst_ids = pd.read_csv('gout_patients_ids.csv')['Patient ID'].to_list()
    filter_five_tuples(lst_ids)

