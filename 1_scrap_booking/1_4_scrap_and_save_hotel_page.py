import random
import string
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path

from tqdm import tqdm
import pandas as pd
import time
import requests

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

#Beautiful soup
from bs4 import BeautifulSoup, element
import urllib
from random import randint, choice
import re
import os
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import ssl
from retry import retry
import concurrent.futures
tqdm.pandas()

properties = {
    # Sleep time between request to booking.com
    "minimum_sleep_time": 2,
    "maximum_sleep_time": 3,
    # Versions and headers
    "minimum_major_version": 1,
    "maximum_major_version": 56,
    "minimum_minor_version": 1,
    "maximum_minor_version": 10,
}



def create_random_header():
    """
    Generate a random HTTP header for requests.

    Returns:
        dict: A dictionary containing 'User-Agent' and 'Cookie'.
    """
    browsers = ["Mozilla/5.0", "Mozilla/4.0", "Mozilla/6.0", "Chrome/92.0.4515.107", "Chrome/93.0.4577.63", "Chrome/94.0.4606.61"]
    os_list = ["Windows NT 10.0; Win64; x64", "Windows NT 6.3; Win64; x64", "Windows NT 6.1; Win64; x64", "X11; Linux x86_64", "Macintosh; Intel Mac OS X 10_15_7"]

    chosen_browser = random.choice(browsers)
    chosen_os = random.choice(os_list)

    major_version = random.randint(1, 56)
    minor_version = random.randint(1, 10)

    user_agent = f"{chosen_browser}/{major_version}.{minor_version} ({chosen_os})"

    # Generate a random cookie value
    cookies = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    header = {'User-Agent': user_agent, 'Cookie': cookies}

    return header

class MyAdapter(HTTPAdapter):
    """
    A custom HTTPAdapter class for managing HTTPS connections with specific settings.

    Methods:
        init_poolmanager(connections, maxsize, block=False):
            Initializes a connection pool with specified parameters.
    """
    def init_poolmanager(self, connections, maxsize, block=False):
        """
        Initialize a connection pool with custom parameters.

        Args:
            connections (int): Number of connection pools.
            maxsize (int): Maximum size of the connection pool.
            block (bool): Whether to block when no connections are available.
        """
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)

@retry(exceptions=Exception, tries=8, delay=2, backoff=1.5, max_delay=30)
def get_page(url):
    """
    Perform a GET request to the given URL and return results.
    Add a wait logic that, combined with random header, will help avoiding
    """
    header =create_random_header()
    request = urllib.request.Request(url, headers=header)
    s = requests.Session()
    s.mount('https://', MyAdapter())
    with urllib.request.urlopen(request) as rep:
        result = rep.read()
    result=result.decode("utf-8")
    time.sleep(randint(properties['minimum_sleep_time'], properties['maximum_sleep_time']))
    return result,header


def get_hotel_name(country_code,hotel_sys_key):
    """
    Fetch the hotel name from its Booking.com page.

    Args:
        country_code (str): The country code of the hotel.
        hotel_sys_key (str): The unique system key for the hotel.

    Returns:
        str or None: The name of the hotel if successfully scraped; None otherwise.
    """
    # URL template for the hotel page
    url = 'https://www.booking.com/hotel/{country_code}/{hotel_sys_key}.html?checkin=2024-09-02&checkout=2024-09-03&group_adults=2&group_children=1&no_rooms=1'
    cur_url = url.format(country_code=country_code,hotel_sys_key=hotel_sys_key)
    try:
        # Fetch the hotel page content
        response,_ = get_page(cur_url)
        soup = BeautifulSoup(response, "html.parser")
        
        # Extract the title of the page and parse the hotel name
        title_tag = soup.title
        title_text = title_tag.string.strip().split(',')[0] if title_tag else None
        
        # Save the raw HTML for reference
        with open(output_path / f"{country_code}_{hotel_sys_key}.html", "w", encoding='utf-8') as file:
            file.write(soup.prettify())
        return title_text
    
    except Exception as e:
        # Handle errors by logging the failed URL
        print(f"Failed to fetch hotel name. URL: {cur_url}")
        print(f"Error: {e}")
        return None

def scrape_hotel_name(row_tuple):
    """
    Wrapper function to scrape hotel names for parallel processing.

    Args:
        row_tuple (tuple): A tuple containing the index and a row of the DataFrame.

    Returns:
        tuple: Index of the row and the scraped hotel name.
    """
    index, row = row_tuple
    country_code, hotel_sys_key = row['country_code'], row['hotel_sys_key']
    
    # Get the hotel name using the country code and hotel system key
    hotel_name = get_hotel_name(country_code, hotel_sys_key)
    return index, hotel_name

if __name__ == "__main__":
    folder_path = Path(__file__).parent.resolve().parent.resolve()

    # Define folder paths
    data_path = folder_path / 'booking.com_data'
    output_path = folder_path / 'booking.com_data' / 'hotel_page'
    
    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Load the DataFrame containing country codes and hotel system keys
    df = pd.read_csv(data_path / 'country_city_hotel.csv')

    # Use a ThreadPoolExecutor to scrape hotel names concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        # Use tqdm for a progress bar while scraping hotel names
        results = list(tqdm(executor.map(scrape_hotel_name, df.iterrows()), total=len(df)))

    # Sort results by the index (to align with the DataFrame)
    results.sort(key=lambda x: x[0])

    # Extract hotel names from the results
    hotel_names = [result[1] for result in results]

    # Add the scraped hotel names as a new column in the DataFrame
    df['hotel_name'] = hotel_names

    # Save the updated DataFrame to a CSV file
    df.to_csv(output_path / 'country_city_hotel_name.csv', index=False)