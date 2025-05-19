import os
import re
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
from tqdm import tqdm
from pathlib import Path 

# Specify the folder path containing HTML files
folder_path = Path('Path/to/HTML/folder')


def extract_room_info(html_content):
    """
    Extract room information (name and price) from the HTML content of a hotel booking page.

    Args:
        html_content (str): The raw HTML content of the hotel booking page.

    Returns:
        list: A list of tuples containing room names and their corresponding prices.
              Each tuple is in the format (room_name, price) where price is in USD.
              If the price is unavailable, it is set to None.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    room_info = []

    # Find all room types
    room_types = soup.find_all('span', class_='hprt-roomtype-icon-link')

    # Find all price selects
    price_selects = soup.find_all('select', class_='hprt-nos-select')

    # Pair room types with prices
    for room_type, price_select in zip(room_types, price_selects):
        room_name = room_type.text.strip()

        # Find option 1 in the select element
        option_1 = price_select.find('option', value='1')
        if option_1:
            # Extract and parse the price from the option text
            price_text = option_1.text.strip()
            price_match = re.search(r'US\$(\d+)', price_text)
            if price_match:
                price = int(price_match.group(1)) # Convert price to integer
            else:
                price = None
        else:
            price = None
            
        # Append the room name and price as a tuple to the result list
        room_info.append((room_name, price))

    return room_info

def process_html_file(file_path):
    """
    Process an HTML file to extract room information and associated metadata.

    Args:
        file_path (str): Path to the HTML file containing hotel booking information.

    Returns:
        list[dict]: A list of dictionaries, each containing:
            - 'countrycode': The country code of the hotel.
            - 'hotel_sys_key': The system key of the hotel.
            - 'roomtype': The type of the room.
            - 'price': The price of the room in USD or None if not available.
    """
    
    # Extract filename and derive metadata
    filename = os.path.basename(file_path)
    filename_tmp = filename.split('.html')[0]
    country_code = filename_tmp.split('_')[0]
    hotel_sys_key = filename_tmp.split('_')[1]

    # Read the HTML content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Extract room information from the HTML content
    room_info = extract_room_info(html_content)

    # Structure the extracted data into a list of dictionaries
    return [
        {
            'countrycode': country_code,
            'hotel_sys_key': hotel_sys_key,
            'roomtype': room_type,
            'price': price
        }
        for room_type, price in room_info
    ]

def process_html_files(folder_path):
    """
    Process all HTML files in a folder to extract room information and compile it into a DataFrame.

    Args:
        folder_path (str): Path to the folder containing HTML files.

    Returns:
        pd.DataFrame: A DataFrame containing extracted data with the following columns:
            - 'countrycode': The country code of the hotel.
            - 'hotel_sys_key': The system key of the hotel.
            - 'roomtype': The type of the room.
            - 'price': The price of the room in USD or None if not available.
    """
    
    # List all HTML files in the given folder
    html_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.html')]

    # Use ThreadPoolExecutor to process files concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        results = list(tqdm(executor.map(process_html_file, html_files), total=len(html_files)))

    # Flatten the list of results
    data = [item for sublist in results for item in sublist]

    # Create DataFrame
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    # Process HTML files and create DataFrame
    result_df = process_html_files(folder_path)

    # Optionally, save the DataFrame to a CSV file
    result_df.to_csv('hotel_room_prices_multi.csv', index=False)
