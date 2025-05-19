import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import os
from tqdm import tqdm


# Define the paths
input_path = Path('Path/to/input/csv')
output_path = Path('Path/to/output/csv')

# Specify the folder type (e.g., 'per_review' or 'per_sentence')
folder_type = 'per_review'



# Get a list of all CSV files in the data directory
list_of_csvs = os.listdir(input_path)

# Columns of interest from the CSV files
useful_columns = ['city','hotel_sys_key']

# Read the main CSV file containing review data
df = pd.read_csv(input_path/'per_review.csv',low_memory=False)

# Keep only the useful columns and group by 'hotel_sys_key' to get the first 'city'
df = df[useful_columns]
df = df.groupby('hotel_sys_key')['city'].first().reset_index()

city_country_codes = {
    "Xi'an": "cn",
    "Shenyang": "cn",
    "Lima": "pe",
    "Beijing": "cn",
    "Seoul": "kr",
    "London": "uk",
    "Los_Angeles": "us",
    "Tehran": "ir",
    "Toronto": "ca",
    "Karachi": "pk",
    "Nanjing": "cn",
    "Barcelona": "es",
    "Guangzhou": "cn",
    "New_York": "us",
    "Tianjin": "cn",
    "Hong_Kong": "hk",
    "Manila": "ph",
    "Singapore": "sg",
    "Dhaka": "bd",
    "Dallas": "us",
    "Chengdu": "cn",
    "Johannesburg": "za",
    "Chicago": "us",
    "Paris": "fr",
    "Mumbai": "in",
    "Nairobi": "ke",
    "Osaka": "jp",
    "Sao_Paulo": "br",
    "Philadelphia": "us",
    "Wuhan": "cn",
    "Houston": "us",
    "Buenos_Aires": "ar",
    "Hyderabad": "in",
    "Riyadh": "sa",
    "Santiago": "cl",
    "Zhengzhou": "cn",
    "Tokyo": "jp",
    "Nagoya": "jp",
    "Bangkok": "th",
    "Cairo": "eg",
    "Bangalore": "in",
    "Boston": "us",
    "Milan": "it",
    "Chennai": "in",
    "Delhi": "in",
    "Washington": "us",
    "San_Francisco": "us",
    "Atlanta": "us",
    "Mexico_City": "mx",
    "Madrid": "es",
    "Miami": "us",
    "Kuala_Lumpur": "my",
    "Dusseldorf": "de",
    "Rio_de_Janeiro": "br",
    "Kolkata": "in",
    "Hangzhou": "cn",
    "Shanghai": "cn",
    "Istanbul": "tr"
}

# Add a new column for the country code by mapping the city to its country code
df['country_code'] = df['city'].apply(lambda x: city_country_codes[x])

# Save the DataFrame to a new CSV file in the output directory
df.to_csv(output_path / 'country_city_hotel.csv',index=False)
