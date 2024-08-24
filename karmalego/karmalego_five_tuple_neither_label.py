import os
import pandas as pd
from tqdm import tqdm


def create_concept_rows(row, labels_patients_ids):
    """ Helper function to create multiple rows per one row based on the specific column """
    if row['ID_BAZNAT_CURRENT'] in labels_patients_ids[0] or row['ID_BAZNAT_CURRENT'] in labels_patients_ids[1]:
        val = "0"
    else:
        val = "1"
    return pd.DataFrame({
        'PatientID': row['ID_BAZNAT_CURRENT'],
        'ConceptName': [f'neither_target'],
        'StartTime': row['Latest_REG_DATE'],
        'EndTime': row['Latest_REG_DATE'],
        'Value': val
    })


def get_5_tuple_file(df, column, labels_patients_ids):
    """ Function to process each column and generate the necessary files """
    tuples = pd.concat([create_concept_rows(row, labels_patients_ids) for index, row in tqdm(df.iterrows())], ignore_index=True)
    tuples.to_csv(f"karmalego_five_tuple_results/neither/neither_{column}_home_hospital_meds_vertical.csv", index=False)


def add_last_date_col(df):
    # Calculate the latest REG_DATE for each ID_BAZNAT_CURRENT
    latest_dates = df.groupby('ID_BAZNAT_CURRENT')['REG_DATE'].max().reset_index()
    latest_dates.columns = ['ID_BAZNAT_CURRENT', 'Latest_REG_DATE']

    # Merge the latest dates back into the original DataFrame
    df = df.merge(latest_dates, on='ID_BAZNAT_CURRENT', how='left').drop_duplicates(subset=['ID_BAZNAT_CURRENT'])
    return df


if __name__ == "__main__":

    if not os.path.exists('karmalego_five_tuple_results'):
        os.makedirs('karmalego_five_tuple_results')
    
    labels = [("cancer", "labels_ids/cancer_patients_ids.csv"),
              ("cardiac", "labels_ids/Cardiac_disease_patients_ids.csv")]
    
    if not os.path.exists(f'karmalego_five_tuple_results/neither'):
        os.makedirs(f'karmalego_five_tuple_results/neither')
        
    for col in ['level_1', 'level_2', 'level_3', 'level_4', 'CODE_ATC']:
        try:
            path = os.path.join('..', 'raw_data', f'results/processed_data_{col}.csv')
            cancer_patients_ids = pd.read_csv(labels[0][1])["Patient ID"].to_list()
            cardiac_patients_ids = pd.read_csv(labels[1][1])["Patient ID"].to_list()
            df = pd.read_csv(path) # forget about the warnings, just keep going :)
            df = add_last_date_col(df) # add last date column to the df
            
            print(f"\nStart neither_{col} file\n")
            get_5_tuple_file(df, col, (cancer_patients_ids, cardiac_patients_ids))
            print(f"\nFinished and saved neither_{col} file\n")
        except:
            print(f"\nFailed to process neither_{col} file\n")

