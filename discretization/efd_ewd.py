import os
import re
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore')


def replace_invalid_chars(name):
    invalid_chars_regex = r'[<>:"/\\|?*\x00-\x1F]'
    valid_name = re.sub(invalid_chars_regex, '_', name)
    return valid_name

def EFD(df, num_bins):
    df = df.dropna(subset=['Value'])  # Drop NaN values

    df.sort_values(by='Value', inplace=True)
    
    increment = 1e-10
    df['Value'] = df['Value'].groupby(df['Value']).transform(lambda x: x + np.arange(len(x)) * increment)
    
    # unique_values_count = df['Value'].nunique()
    # if unique_values_count < num_bins:
    #     logging.info(f"EFD Error: Not enough unique values ({unique_values_count}) to create {num_bins} bins.")
    #     return None, None

    # Adjust the 'duplicates' parameter to drop any duplicate bin edges
    bin_ranges, edges = pd.qcut(df['Value'], q=num_bins, retbins=True)

    df['EFD'] = pd.cut(df['Value'], bins=edges, labels=False) + 1

    intervals = bin_ranges.cat.categories
    labels = [f'({round(intervals[i].left, 10)} - {round(intervals[i].right, 10)}]' for i in range(len(intervals))]

    return df, labels


def EWD(df, num_bins):
    df = df.dropna(subset=['Value'])  # Drop NaN values

    # unique_values_count = df['Value'].nunique()
    # if unique_values_count < num_bins:
    #     logging.info(f"EWD Error: Not enough unique values ({unique_values_count}) to create {num_bins} bins.")
    #     return None, None

    # Categorize values into intervals
    bin_ranges, edges = pd.cut(df['Value'], bins=num_bins, retbins=True)

    df['EWD'] = pd.cut(df['Value'], bins=edges, labels=False) + 1
    
    # Generate labels based on bin edges
    labels = [f'({round(edges[i], 10)} - {round(edges[i+1], 10)}]' for i in range(len(edges)-1)]
    
    return df, labels


def plot_EWD(df, bin_ranges, path):
    plt.figure(figsize=(10, 6))
    ax = df['EWD'].value_counts(sort=False).plot(kind='bar')
    med = df['Concept Name'].tolist()[0]
    num_bins = len(bin_ranges)
    plt.suptitle("Equal Width Discretization (EWD)",fontsize=14, fontweight='bold')
    plt.title(f"{num_bins} Bins - Medicine {med}")
    plt.xlabel('Bins')
    plt.ylabel('Frequency')
        
    ax.set_xticks(range(num_bins))
    ax.set_xticklabels(bin_ranges, rotation=0, ha='right')
    
    for i, count in enumerate(df['EWD'].value_counts(sort=False)):
        plt.text(i, count, str(count), ha='center', va='bottom')
        
    plt.savefig(path + f'/EWD_{num_bins}.png')
    plt.close()
    # plt.show()


def plot_EFD(df, intervals, path):
    plt.figure(figsize=(10, 6))
    ax = df['EFD'].value_counts(sort=False).plot(kind='bar')
    med = df['Concept Name'].tolist()[0]
    num_bins = len(intervals)
    plt.suptitle("Equal Frequency Discretization (EFD)",fontsize=14, fontweight='bold')
    plt.title(f"{num_bins} Bins - Medicine {med}")
    plt.xlabel('Bins')
    plt.ylabel('Frequency')

    ax.set_xticks(range(num_bins))
    ax.set_xticklabels(intervals, rotation=0, ha='right')

    for i, count in enumerate(df['EFD'].value_counts(sort=False)):
        plt.text(i, count, str(count), ha='center', va='bottom')
    
    plt.savefig(path + f'/EFD_{num_bins}.png')
    plt.close()
    # plt.show()


def process_csv(csv_name):
    columns_to_read = ['Patient ID', 'Start Time','End Time', 'Concept Name', 'Value']

    if not os.path.exists(f'results/{csv_name[:-4]}'):
        os.makedirs(f'results/{csv_name[:-4]}')

    # get five tuples files
    five_tuples_path = os.path.join('..', 'five_tuples_csv_files', f'five_tuple_results\\{csv_name}')
    
    df = pd.read_csv(five_tuples_path, usecols=columns_to_read)
    
    # filter all the rows that contains 'DOSAGE'
    df = df[df['Concept Name'].str.contains('DOSAGE', na=False)]
    df['Concept Name'] = df['Concept Name'].str.slice(stop=-7)

    # extract meds from df
    meds_names = set(df['Concept Name'].tolist())

    # fix data
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    # extract only int and float from units
    df['Value'] = df['Value'].str.extract(r'(\d+\.\d+|\d+)').astype(float)
    return df, meds_names


if __name__ == "__main__":
    logging.basicConfig(filename='logfile.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if not os.path.exists('results'):
        os.makedirs('results')
    csv_names = ['CODE_ATC_home_hospital_meds_vertical.csv',
                 'level1_home_hospital_meds_vertical.csv',
                 'level2_home_hospital_meds_vertical.csv',
                 'level3_home_hospital_meds_vertical.csv',
                 'level4_home_hospital_meds_vertical.csv']

    for csv_name in csv_names:
        logging.info(f"Starting {csv_name[:-4]}")
        # open and process csv file
        df, meds_names = process_csv(csv_name)
       
        bins_lst = [2,3]
        for med in meds_names:
            med_fixed = replace_invalid_chars(med)
            current_path = f'results/{csv_name[:-4]}/{med_fixed}'
            if not os.path.exists(current_path):
                os.makedirs(current_path)

            df_med = df[df['Concept Name'] == med]

            for num_bins in bins_lst:
                # EFD
                try:
                    df_efd, efd_ranges = EFD(df_med, num_bins)
                    if df_efd is not None:
                        plot_EFD(df_efd, efd_ranges, current_path)
                        file_path_efd = f"{current_path}/EFD_bins_{num_bins}.csv"
                        df_efd.to_csv(file_path_efd, index=False)
                except Exception as e:
                    logging.info(f"EFD Error for {med}: {e}")

                # EWD
                try:
                    df_ewd, ewd_ranges = EWD(df_med, num_bins)
                    if df_ewd is not None:
                        plot_EWD(df_ewd, ewd_ranges, current_path)
                        file_path_ewd = f"{current_path}/EWD_bins_{num_bins}.csv"
                        df_ewd.to_csv(file_path_ewd, index=False)
                except Exception as e:
                    logging.info(f"EWD Error for {med}: {e}")
        logging.info(f"Finished {csv_name[:-4]}")
