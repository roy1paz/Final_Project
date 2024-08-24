import os
import pandas as pd


def get_ids_str():
    if not os.path.exists('karmalego_ids_str'):
        os.makedirs('karmalego_ids_str')
        print("created karmalego_ids_str dir")
    
    filter_or_not = ["karmalego_five_tuple_results", "filter_karmalego_five_tuple_results"]
    labels = ["cancer", "cardiac", "neither"]
    columns = ['CODE_ATC', 'level_1', 'level_2', 'level_3', 'level_4']
    for is_filter in filter_or_not:
        if is_filter == "karmalego_five_tuple_results":
            dir_name = "non_filter"
        else:
            dir_name = "filter_by_meds"
        if not os.path.exists(f'karmalego_ids_str/{dir_name}'):
            os.makedirs(f'karmalego_ids_str/{dir_name}')
            print(f"created {dir_name} dir")
            
        for label in labels:
            if not os.path.exists(f'karmalego_ids_str/{dir_name}/{label}'):
                os.makedirs(f'karmalego_ids_str/{dir_name}/{label}')
                print(f"created karmalego_ids_str/{dir_name}/{label} dir")
            for col in columns:
                path = f'{is_filter}/{label}/{label}_{col}_home_hospital_meds_vertical.csv'
                df = pd.read_csv(path)
                df = df[df["Value"].astype(str).str.strip() == "1"]
                ids = df["PatientID"].astype(str).to_list()
                ids_str = ','.join(ids)
                with open(f"karmalego_ids_str/{dir_name}/{label}/{label}_{col}_ids_str.txt", 'w') as f:
                    f.write(ids_str)
                    

if __name__ == "__main__":
    get_ids_str()
    