from pathlib import Path
import os
import pandas as pd
import re
from tqdm import tqdm

def read_one_hotel_csv_wrapper(file_path, hotel_name):
    """
    Wrapper function for reading a single hotel's CSV file.

    Args:
        file_path (Path): Path to the CSV file.
        hotel_name (str): Name of the hotel.

    Returns:
        pd.DataFrame or int: Filtered DataFrame if successful, -1 otherwise.
    """
    
    return read_one_hotel_csv(file_path, hotel_name)

def read_one_hotel_csv(file_path, file_name):
    
    """
    Read a single hotel's CSV file and filter its content.

    Args:
        file_path (Path): Path to the CSV file.
        file_name (str): File name of the CSV.

    Returns:
        pd.DataFrame or int: Filtered DataFrame if successful, -1 otherwise.
    """
    
    try:
        # Read the CSV file into a DataFrame.
        df1_city_hotel = pd.read_csv(file_path, sep=',', encoding='utf-8-sig', engine='python')
    except:
        return -1
    if len(df1_city_hotel) == 0:
        return -1
    
    # Filter rows where either "The reviewer liked" or "The reviewer did not liked" is not null.
    df1_city_hotel_comments_filter = df1_city_hotel[
        df1_city_hotel[['The reviewer liked', 'The reviewer did not liked']].notnull().any(axis=1)]

    # Extract hotel system key and city from the file name.
    file_name_list = re.split('\\\\|\.|___', file_name)
    hotel_sys_key = file_name_list[-2]
    
    # Assign city and hotel_sys_key as new columns in the DataFrame.
    df1_city_hotel_comments_filter = df1_city_hotel_comments_filter.assign(city=file_name_list[0])
    df1_city_hotel_comments_filter = df1_city_hotel_comments_filter.assign(hotel_sys_key=hotel_sys_key)

    return df1_city_hotel_comments_filter

# Function to merge results from all hotels in a city.
def merge_results(results_dir, merge_results_dir):
    """
        Merge all hotel review files within each city and save the merged results.
        
        Args:
            results_dir (Path): Path to read the CSV file.
            merge_results_dir (Path): Path to output the mereged CSV file.
    """
    for _city in city_list:
        # Get the list of all hotels for the current city.
        cur_city_hotel_list = os.listdir(results_dir / _city)
        cur_city_df_list = []

        # Process each hotel's CSV file.
        for each_hotel in tqdm(cur_city_hotel_list):
            cur_df = read_one_hotel_csv(results_dir / _city / each_hotel, each_hotel)
            if type(cur_df) != int:
                cur_city_df_list.append(cur_df)

        # Merge all DataFrames for the current city.
        cur_merged_df = pd.concat(cur_city_df_list)
        cur_merged_df.to_csv(merge_results_dir / "{city}_results_merged.csv".format(city=_city), sep=',', index=False, encoding='utf-8-sig')

if __name__ == '__main__':
    # Define the directory paths.
    results_dir = Path('Path/to/output/city_result')
    output_dir = results_dir.parent
    merge_results_dir = output_dir / 'merge_result'

    # List all cities in the results directory.
    city_list = os.listdir(results_dir)

    # Check and create the merged results directory if necessary.
    if os.path.exists(merge_results_dir) :
        print("Merged Results directory exists")
    elif len(os.listdir(merge_results_dir)) == 0:
        print("Merged Results directory exists but is empty!")
        merge_results(results_dir, merge_results_dir)
    else:
        print("Creating Merged Results directory and merging results")
        os.mkdir(merge_results_dir)
        merge_results(results_dir, merge_results_dir)

    # Create a master merge file containing data from all cities.
    master_merge_file_name = "all_cities_merged.csv"
    if os.path.exists(output_dir / master_merge_file_name):
        print("Master merge file exists!")
    else:
        list_of_all_df = []
        for each_merged_files in tqdm(os.listdir(merge_results_dir)):
            cur_city_df = pd.read_csv(merge_results_dir / each_merged_files, sep=',', encoding='utf-8-sig')
            list_of_all_df.append(cur_city_df)
        master_merged_df = pd.concat(list_of_all_df)
        master_merged_df.to_csv(output_dir / master_merge_file_name, sep=',', index=False, encoding='utf-8-sig')
