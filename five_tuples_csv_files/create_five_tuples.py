import os
import pandas as pd
from tqdm import tqdm


def create_concept_rows(row, col):
    """ Helper function to create multiple rows per one row based on the specific column """
    med = row[col]
    return pd.DataFrame({
        'Patient ID': row['ID_BAZNAT_CURRENT'],
        'Concept Name': [med, f'{med}_DOSAGE', f'{med}_UNIT', f'{med}_GIVEN_WAY'],
        'Start Time': row['REG_DATE'],
        'End Time': row['REG_DATE'],
        'Value': [True, row['M_DOSAGE'], row['UNIT_OF_MEASURE'], row['M_GIVEN_WAY_DESC']]
    })


def get_5_tuple_file(df, column):
    """ Function to process each column and generate the necessary files """
    tuples = pd.concat([create_concept_rows(row, column) for index, row in tqdm(df.iterrows())], ignore_index=True)
    tuples.to_csv(f"five_tuple_results/{column}_home_hospital_meds_vertical.csv", index=False)


if __name__ == "__main__":
    path = os.path.join('..', 'raw_data', 'processed_top_meds_data.csv')

    if not os.path.exists('five_tuple_results'):
        os.makedirs('five_tuple_results')

    df = pd.read_csv(path) # forget about the warnings, just keep going :)

    for col in ['level_1', 'level_2', 'level_3', 'level_4', 'CODE_ATC']:
        try:
            print(f"\nStart {col} file\n")
            get_5_tuple_file(df, col)
            print(f"\nFinished and saved {col} file\n")
        except:
            print(f"\nFailed to process {col} file\n")

