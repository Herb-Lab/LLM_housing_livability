# -*- coding: utf8 -*-
import logging
from logging import handlers
from pathlib import Path
import random
import string
import socket

import time
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

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
import threading

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

class Logger(object):
    """
    A custom logger class for managing logging configurations.

    Attributes:
        level_relations (dict): Mapping of log levels to their numeric values.
    Methods:
        __init__(filename, level='info', when='D', backCount=3, fmt):
            Initializes the logger with specific settings.
    """
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    #fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    def __init__(self, filename, level='info', when='D', backCount=3, fmt='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s'
                 ):
        """
        Initialize the logger with file and console handlers.

        Args:
            filename (str): Log file name.
            level (str): Logging level.
            when (str): Frequency for rotating the log file.
            backCount (int): Number of backup files to keep.
            fmt (str): Format string for log messages.
        """
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level))
        sh = logging.StreamHandler()
        sh.setFormatter(format_str)
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')
        th.setFormatter(format_str)
        self.logger.addHandler(sh)
        self.logger.addHandler(th)

log = Logger('booking_scrapper.log', level='debug')


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

socket.setdefaulttimeout(500)

@retry(exceptions=Exception, tries=8, delay=2, backoff=1.5, max_delay=30, logger=log.logger)
def get_page(url):
    """
    Perform a GET request to the given URL and return the page content and header.

    Args:
        url (str): URL to fetch.

    Returns:
        tuple: Page content (str) and header (dict).
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

def deal_comment_pages(page, max_comment_page_number, base_hotel_comments_url, country_code ,hotel_sys_key, list_title, list_grade,
                       list_namereviewer, list_countryreviewer, list_commentadded, list_nightmonth, list_nightnb, list_bedroomtype,
                       list_reviewcommentliked, list_reviewcommentdisliked):
    
    """
    Process comments from a specific page of a hotel review.

    Args:
        page (int): Current page number.
        max_comment_page_number (int): Total number of pages.
        base_hotel_comments_url (str): Base URL for fetching comments.
        country_code (str): Country code for the hotel.
        hotel_sys_key (str): System key for the hotel.
        list_title (list): List to store review titles.
        list_grade (list): List to store review grades.
        list_namereviewer (list): List to store reviewer names.
        list_countryreviewer (list): List to store reviewer countries.
        list_commentadded (list): List to store review dates.
        list_nightmonth (list): List to store months of trips.
        list_nightnb (list): List to store number of nights.
        list_bedroomtype (list): List to store bedroom types.
        list_reviewcommentliked (list): List to store positive comments.
        list_reviewcommentdisliked (list): List to store negative comments.
    """
    
    log.logger.info(
        '---------- Reviewing Comments page number : {current_page_num}/{total_page_num} current_time is {current_time}---------'
        .format(current_page_num=page, total_page_num=max_comment_page_number,
                current_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    hotel_comments_url = base_hotel_comments_url.format(country_code=country_code,hotel_sys_key=hotel_sys_key, offset=page * 25)
    start_time = time.time()
    current_hotel_comments_page = get_page(hotel_comments_url)[0]
    finish_time = time.time()
    log.logger.info('----------- We try to connect to : \n Page : {}'.format(hotel_comments_url))
    log.logger.info(
        '----------- This connect spent time: {spent_time}s '.format(spent_time=round(finish_time - start_time, 3)))

    soup = BeautifulSoup(current_hotel_comments_page, 'lxml')
    for review in soup.findAll("div", {"class": "bui-grid__column-9"}):

        # TITLE
        tofind = review.find("h3", {"class": "c-review-block__title"})
        list_title.append(tofind.get_text(strip=True)) if tofind != None else list_title.append("")

        # GRADE
        tofind = review.find("div", {"class": "bui-review-score__badge"})
        list_grade.append(tofind.get_text(strip=True)) if tofind != None else list_grade.append("")

        # NAME REVIEWER
        tofind = review.parent.find("span", {"class": "bui-avatar-block__title"})
        list_namereviewer.append(tofind.get_text(strip=True)) if tofind != None else list_namereviewer.append("")

        # COUNTRY REVIEWER
        tofind = review.parent.find("span", {"class": "bui-avatar-block__subtitle"})
        list_countryreviewer.append(tofind.get_text(strip=True)) if tofind != None else list_countryreviewer.append(
            "")

        if len(review.parent.findAll("span", {"class": "c-review-block__date"})) == 2:
            # DATE OF COMMENT
            list_commentadded.append(
                review.parent.findAll("span", {"class": "c-review-block__date"})[1].get_text(strip=True).split(
                    ': ')[1])
            # MONTH OF TRIP
            list_nightmonth.append(
                review.parent.findAll("span", {"class": "c-review-block__date"})[0].get_text(strip=True))
            # NUMBER OF NIGHT
            list_nightnb.append(review.parent.findAll("span", {"class": "c-review-block__date"})[0]
                                .parent.get_text(strip=True).split('night')[0].strip())
        else:
            list_commentadded.append("")
            list_nightmonth.append("")
            list_nightnb.append("")

        # BEDROOM TYPE
        tofind = review.parent.find("a", {"class": "c-review-block__room-link"})
        list_bedroomtype.append(tofind.get_text(strip=True)) if tofind != None else list_bedroomtype.append("")

        # POSITIVE COMMENT
        revpos = review.find(text="Liked")
        if revpos != None:
            revposfr = revpos.findNext('span').findNext('span').get_text(strip=True)
            if revposfr != '':
                list_reviewcommentliked.append(revposfr)
            else:
                list_reviewcommentliked.append(revpos.findNext('span').get_text(strip=True))
        else:
            list_reviewcommentliked.append("")

        # NEGATIVE COMMENT
        revneg = review.find(text="Disliked")
        if revneg != None:
            revnegfr = revneg.findNext('span').findNext('span').get_text(strip=True)
            if revnegfr != '':
                list_reviewcommentdisliked.append(revnegfr)
            else:
                list_reviewcommentdisliked.append(revneg.findNext('span').get_text(strip=True))
        else:
            list_reviewcommentdisliked.append("")

    log.logger.info(
        'Comments Page {page_num} of {hotel_sys_name} done\n'.format(page_num=page, hotel_sys_name=hotel_sys_key))
    return


def one_hotel_reviews(one_hotel_file_name, hotel_sys_key, country_code):

    """
    Collect all reviews of a specific hotel and save them to a file.

    Args:
        one_hotel_file_name (str): File name for saving hotel reviews.
        hotel_sys_key (str): System key for the hotel.
        country_code (str): Country code of the hotel.
    """
    
    # Base URL template for fetching hotel reviews
    base_hotel_comments_url = "https://www.booking.com/reviewlist.html?cc1={country_code}&lang=en-us;pagename={hotel_sys_key};type=total;rows=25;offset={offset}"

    # Initialize lists to store review details
    list_title = []
    list_grade = []
    list_namereviewer = []
    list_countryreviewer = []
    list_bedroomtype = []
    list_commentadded = []
    list_nightmonth = []
    list_nightnb = []
    list_reviewcommentliked = []
    list_reviewcommentdisliked = []

    # Fetch the first page to determine the number of review pages
    origin_hotel_comments_url = base_hotel_comments_url.format(country_code=country_code, hotel_sys_key=hotel_sys_key, offset=0)
    origin_hotel_comments_page = get_page(origin_hotel_comments_url)[0]
    
    log.logger.info('-------We connect to origin page of {hotel}: \n Page : {hotel_query_url} ---'
          .format(hotel=hotel_sys_key, hotel_query_url=origin_hotel_comments_url))
    
    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(origin_hotel_comments_page, 'lxml')

    # Determine the number of comment pages
    try:
        max_comment_page_number = int(soup.find_all("a", {"class": "bui-pagination__link"})[-1].get_text(strip=True).split(" ")[-1])
    except:
        log.logger.info("-------This hotel only have 1 page of comments")
        max_comment_page_number= 1
    log.logger.info("-------There are total {} comment pages for this hotel".format(max_comment_page_number))

    # Use ThreadPoolExecutor for concurrent processing of review pages
    executor_one_hotel = ThreadPoolExecutor(max_workers=200)
    one_hotel_tasks = []
    for page in range(0,max_comment_page_number):
        one_hotel_tasks.append(executor_one_hotel.submit(deal_comment_pages,page, max_comment_page_number, base_hotel_comments_url, country_code, hotel_sys_key, list_title
                                             ,list_grade,list_namereviewer, list_countryreviewer, list_commentadded,
                                             list_nightmonth, list_nightnb,list_bedroomtype,list_reviewcommentliked, list_reviewcommentdisliked))
    
    # Wait for all threads to complete
    wait(one_hotel_tasks, return_when=ALL_COMPLETED)

    # Organize the collected data into a DataFrame
    columns = {
        'Review Title': list_title,
        'Grade': list_grade,
        'Reviewer name': list_namereviewer,
        'Date review': list_commentadded,
        'Month of trip': list_nightmonth,
        'Number of nights': list_nightnb,
        'Country reviewer': list_countryreviewer,
        'Bedroom Type': list_bedroomtype,
        'The reviewer liked': list_reviewcommentliked,
        'The reviewer did not liked': list_reviewcommentdisliked,
    }
    data_download = pd.DataFrame(columns)
    
    log.logger.info("-------The comments of hotel: {hotel} is collected, the result will be saved in {file_name} "
          .format(hotel=hotel_sys_key, file_name=one_hotel_file_name))
    data_download.to_csv(one_hotel_file_name, sep=',', index=False, encoding='utf-8-sig')

def one_hotel_of_one_page(hotel_num, page_number, hotel_cards, city, recorded_hotels):
    
    """
    Process a single hotel from a city page.

    Args:
        hotel_num (int): Hotel index on the page.
        page_number (int): Page number in the city results.
        hotel_cards (list): List of hotel cards on the page.
        city (str): Name of the city being processed.
        recorded_hotels (set): Set of already processed hotel files.
    """
    
    log.logger.info("-------We will query No.{hotel_num} hotel in Page {page_number}"
                    .format(hotel_num=hotel_num, page_number=page_number))
    
    # Extract the hotel URL from the card
    hotel_href = hotel_cards[hotel_num].get("href")
    
    log.logger.info("-------the hotel url is {url}".format(url=hotel_href))
    
    # Parse the system key and country code from the URL
    hotel_key_query_list = re.findall("/(.*?)\.html", hotel_href)[0].split(".")[-1].split("/")
    hotel_sys_key = hotel_key_query_list[-1]
    hotel_country_code = hotel_key_query_list[-2]
    
    # Extract the true hotel name from the card
    hotel_true_name = hotel_cards[hotel_num].find_next("div").get_text(strip=True)
    
    log.logger.info("-------The true name of hotel is {true_name}, and sys key is {sys_key}"
                    .format(true_name=hotel_true_name, sys_key=hotel_sys_key))
    
    # Generate a filename for the hotel reviews
    one_hotel_file_name = city.replace(" ", "_") + "___" + hotel_sys_key + ".csv"

    # Check if the hotel has already been processed
    if one_hotel_file_name in recorded_hotels:
        log.logger.info("-------The result of hotel {true_name} has been collected in {file_name}, pass\n"
                        .format(true_name=hotel_true_name, file_name=one_hotel_file_name))
        return
    
    # Collect reviews for the hotel and save them
    one_hotel_reviews(one_hotel_file_name, hotel_sys_key, hotel_country_code)
    return

def one_page_of_one_city(page_number, max_city_page_number, city):
    
    """
    Process a single page of a city's hotel listings.

    Args:
        page_number (int): Current page number being processed.
        max_city_page_number (int): Total number of pages in the city.
        city (str): Name of the city being processed.
    """
    
    log.logger.info("-----We will deal with NO.{page_num}/{total_page_num} page of {city} properties ----- "
                    .format(page_num=page_number, total_page_num=max_city_page_number, city=city))
    
    # Construct the query URL for the current page
    current_city_query_url = "https://www.booking.com/searchresults.html?ss={city}&lang=en-us&rows=25&offset={offset}" \
        .format(city=city, offset=page_number * 25)
    log.logger.info("-----The query url is {}".format(current_city_query_url))
    
    # Fetch the HTML content of the page
    current_city_page = get_page(current_city_query_url)[0]
    
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(current_city_page, 'lxml')
    hotel_cards = soup.find_all("a", {"class": "e13098a59f"})
    recorded_hotels = set(os.listdir())
    
    # List to hold tasks for concurrent processing and Thread pool for processing hotels concurrently
    one_city_page_tasks = []
    executor_one_city_page = ThreadPoolExecutor(max_workers=14)

    # Submit tasks to process each hotel on the current pag
    for hotel_num in range(len(hotel_cards)):
        one_city_page_tasks.append(
            executor_one_city_page.submit(one_hotel_of_one_page, hotel_num, page_number, hotel_cards, city, recorded_hotels))
    wait(one_city_page_tasks, return_when=ALL_COMPLETED)


def one_city_info(city_origin):
    
    """
    Process all hotel listings and reviews for a given city.

    Args:
        city_origin (str): Original name of the city.
    """
    
    # Replace spaces with underscores to create a valid folder name
    city = city_origin.replace(" ", "_")
    
    # Ensure a directory exists for the city
    if not os.path.exists(city):
        os.makedirs(city)
    os.chdir(city)
    
    # Base URL template for city search results
    base_city_query_url = "https://www.booking.com/searchresults.html?ss={city}&lang=en-us&rows=25"
    
    log.logger.info(" ")
    log.logger.info("-We are dealing with hotels in {city}-".format(city=city))
    
    # Construct the URL for the first page of city search results
    origin_city_query_url = base_city_query_url.format(city=city)
    
    log.logger.info("---Corresponding query url is: {city_query_url} ---".format(city_query_url=origin_city_query_url))
    
    # Fetch the content of the first page
    origin_city_page = get_page(origin_city_query_url)[0]
    
    log.logger.info('---We connect to origin page of {city}: \n Page : {city_query_url} ---'.format(city=city,city_query_url=origin_city_query_url))
    
    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(origin_city_page, 'lxml')
    
    log.logger.info("---{}---".format(soup.find("h1").get_text(strip=True)))

    # Get the total number of hotels in the city
    # and check if all hotels have already been processed

    saved_file_num = len(set(os.listdir()))
    total_hotel_num = int(re.findall(r'\d+',  soup.find("h1").get_text(strip=True))[0])
    
    if total_hotel_num <= saved_file_num:
        log.logger.info('--- There have already been {saved_file_num} files, more than total, city pass ---'
                        .format(saved_file_num=saved_file_num))
        os.chdir("..")
        return
    try:
        # Determine the number of pages in the city search results
        max_city_page_number = int(soup.findAll("button", {"class": "fc63351294 f9c5690c58"})[-1].get_text(strip=True))
    except:
        max_city_page_number = 1

    log.logger.info("---There are {max_city_page_number} pages in {city} results, each page has 25 results is fixed---"
          .format(max_city_page_number=max_city_page_number, city=city))

    # Use ThreadPoolExecutor to process all pages of the city concurrently
    executor_one_city = ThreadPoolExecutor(max_workers=14)
    one_city_tasks = []
    
    # Submit tasks for processing each page
    for page_number in range(max_city_page_number):
        one_city_tasks.append(executor_one_city.submit(one_page_of_one_city, page_number, max_city_page_number, city))
    wait(one_city_tasks, return_when=ALL_COMPLETED)
    os.chdir("..")


if __name__ == "__main__":
    os.chdir(Path('Path/to/output/city_result'))
    os.listdir()

    city_list = [
    "Tokyo",
    "Nagoya",
    "Delhi",
    "Hyderabad",
    "Manila",
    "Chicago",
    "Seoul",
    "Johannesburg",
    "Karachi",
    "Shenyang",
    "Shanghai",
    "Wuhan",
    "Mumbai",
    "Kuala Lumpur",
    "New York",
    "Hong Kong",
    "Sao Paulo",
    "Boston",
    "Beijing",
    "Zhengzhou",
    "Mexico City",
    "Hangzhou",
    "Guangzhou",
    "Dusseldorf",
    "Dhaka",
    "Toronto",
    "Osaka",
    "Dallas",
    "San Francisco",
    "Cairo",
    "Nanjing",
    "Bangkok",
    "Madrid",
    "Los Angeles",
    "Santiago",
    "Buenos Aires",
    "Houston",
    "Kolkata",
    "Miami",
    "Tehran",
    "Riyadh",
    "Istanbul",
    "Singapore",
    "Tianjin",
    "Xi'an",
    "Rio de Janeiro",
    "Philadelphia",
    "Lima",
    "Nairobi",
    "Chengdu",
    "Milan",
    "Paris",
    "Atlanta",
    "Bangalore",
    "London",
    "Washington",
    "Chennai",
    "Barcelona"
]

    log.logger.debug("-----------This is a new start at {current_time}--------".format(current_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    try:
        for city_origin in city_list:
            one_city_info(city_origin)
    except Exception as e:
        log.logger.critical(e)
    log.logger.info("Congratulation! This is the end of this program")
