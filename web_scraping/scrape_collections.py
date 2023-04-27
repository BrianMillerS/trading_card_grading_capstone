import os
import re
import sys
import requests
import argparse
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

"""
Insert Script Description Here..

USAGE:
./web_scraping_collectors_PSA_baseball.py --grade {} --card_num {} --files_dir {} --photo_dir {}

ARGS:
--grade     (-g): (INT): The PSA grade value (1-10) of cards to scrape from www.collectors.com
--card_num  (-c): (INT): The card number to start scraping from, there are 24 cards per page
--files_dir (-f): (STR): The path to where you want the metadata and scripting log files to be saved
--photo_dir (-p): (STR): The path to where you want the photos downloaded

EXAMPLE:
./web_scraping_collectors_PSA_baseball.py
--grade 1 
--card_num 1
--files_dir /Users/brianmiller/Desktop/collection_files 
--photo_dir /Users/brianmiller/Desktop/collection_files/images_psa1 
"""

# define and parse the user args 
parser = argparse.ArgumentParser(description='Scrape PSA1-10 images from www.collectors.com')
parser.add_argument('-g', '--grade', type=int, choices=range(1, 11), help='PSA grade value (1-10) of cards to scrape')
parser.add_argument('-c', '--card_num', type=int, help='Card number to start scraping from')
parser.add_argument('-f', '--files_dir', type=str, help='Path to dir for metadata and log data saves')
parser.add_argument('-p', '--photo_dir', type=str, help='Path to dir for photo download')
args = parser.parse_args()


def load_metadata(metadata_pickle_file_location):
    """_summary_

    Args:
        metadata_pickle_file_location (str):
    Returns:
        pandas.dataframe: _description_
    """

    # if the metadata file exists, load it
    if os.path.isfile(metadata_pickle_file_location):
        print("LOG: Picklefile exists, loading existing metadata")
        metadata_df = pd.read_pickle(metadata_pickle_file_location)
    
    # if it does not exist, make it
    else:
        # Create an empty DataFrame, save it, and reopen it, this helps if the script fails without warning
        metadata_df = pd.DataFrame(columns=['id', 'grade', 'image_name', 'price', 'desc', 'source'])
        metadata_df.to_pickle(metadata_pickle_filename)  # save the empty metadata
        metadata_df = pd.read_pickle(metadata_pickle_file_location)
        
    return metadata_df


def calc_page_counter_from_card_counter(card_counter):
    """
    Given the card counter, calculate what page this scraping script should jump to in order to skip already scraped images
    Args:
        card_counter (int): counter for card ids
    Returns:
        the page counter int of what page the script should start on
    """
    if card_counter <= 24:
        return card_counter
    else:
        return (card_counter // 24) + 1

# define the output locations
image_save_dir = args.photo_dir
metadata_pickle_filename = "{}/PSA{}_collectors_metadata.pkl".format(args.files_dir, args.grade)
log_filename = "{}/PSA{}_collectors_LOGS.txt".format(args.files_dir, args.grade)

# define the base search url, low and high bound the search on their website so we only get PSA grades of that int
base_url = "https://www.collectors.com/trading-cards/sport-baseball-cards/20003?lowgrade={}&highgrade={}&gradingservice=2&page=".format(args.grade, args.grade)

# load the metadata pandas df, if it doesn't exist, make one
metadata_df = load_metadata(metadata_pickle_filename)

# open a log file, if it doesn't exist, make one
log_file = open(log_filename, 'a')

# initiate a counter of what card to start on
card_counter = args.card_num

# until ctrl-c to exit, infintly do the following
# I know that this is bay programming practice, but the website that I am scraping constantanly goes in and out of service
# so this is one way to 'wait out' those times when the page won't load
try:
    while True:
        # create a page counter, to know which page of results to load
        page_counter = calc_page_counter_from_card_counter(card_counter)
        page_url = base_url + str(page_counter)

        # GET the page, parse the response using Beautiful Soup
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # check to see if the website is live, sometimes it is simply broken
        if soup.select("#error_message"):
            # print("ERROR: WEBSITE DOWN TEMPORARILY: Internal error: Page {}\n".format(page_counter))
            # log_file.write("ERROR: WEBSITE DOWN TEMPORARILY: Internal error: Page {}\n".format(page_counter))
            continue
            
        elif soup.select("#error-information-popup-content > div.error-code"):
            # print("ERROR: WEBSITE DOWN TEMPORARILY: 503 error: Page {}\n".format(page_counter))
            # log_file.write("ERROR: WEBSITE DOWN TEMPORARILY: 503 error: Page {}\n".format(page_counter))
            continue

        # use CSS selector, to get all of the 24 divs, for the 24 card results, per page. recursive = False to not get the sub divs
        child_divs = soup.select("#searchresults > div:nth-child(1) > div > div > div", recursive=False)

        # for each of the cards to scrape
        for child_div in child_divs:

            # CARD DESCRIPTION
            try:
                desc_div = child_div.find("div", {"class": "itemdescr"})
                desc_txt = desc_div.text

            except AttributeError:
                log_file.write("LOG: page {}: card {}: Description: AttributeError: returning NA\n".format(page_counter, card_counter))
                desc_txt = np.nan
            except NoSuchElementException:
                log_file.write("LOG: page {}: card {}: Description: NoSuchElementException: returning NA\n".format(page_counter, card_counter))
                desc_txt = np.nan


            # CARD GRADE
            try:
                grade_div = child_div.find("div", {"class": "itemgrade"})
                grade_txt = grade_div.text

                # get the grade int from the string
                pattern = r"Grade: PSA (\d+(\.\d+)?)"  # matches one or more digits followed by an optional decimal point and one or more digits
                match = re.search(pattern, grade_txt)  # find the first instance of this pattern
                if match:
                    # Get the matched number and replace "." with "_"
                    grade_num_str = match.group(1).replace(".", "_")
                else:
                    log_file.write("ERROR: page {}: card {}: regex failed: returning 'NA' \n".format(page_counter, card_counter))
                    grade_txt = "NA"

            except AttributeError:
                log_file.write("ERROR: page {}: card {}: Grade: AttributeError: returning 'NA' \n".format(page_counter, card_counter))
                grade_txt = "NA"
            except NoSuchElementException:
                log_file.write("ERROR: page {}: card {}: Grade: NoSuchElementException: returning 'NA' \n".format(page_counter, card_counter))
                grade_txt = "NA"


            # CARD PRICE
            try:
                price_div = child_div.find("div", {"class": "itemsaleprice"})
                price_txt = price_div.text

            except AttributeError:
                log_file.write("LOG: page {}: card {}: Price: AttributeError: Price data not found, trying Bid data\n".format(page_counter, card_counter))
                try:
                    price_div = child_div.find("div", {"class": "itembidprice"})
                    price_txt = price_div.text
                except AttributeError:
                    log_file.write("LOG: page {}: card {}: Bid: AttributeError: Bid data not found, returning NA\n".format(page_counter, card_counter))
                    price_txt = np.nan

            except NoSuchElementException:
                log_file.write("LOG: page {}: card {}: Price: NoSuchElementException: returning NA\n".format(page_counter, card_counter))
                price_txt = np.nan


            # LISTING SOURCE (e.g. EBAY, AMAZON, etc.)
            try:
                source_a = child_div.find("a", {"class": "itemseller seller-level-med"})
                source_txt = source_a.text

            except AttributeError:
                log_file.write("LOG: page {}: card {}: Source: AttributeError: returning NA\n".format(page_counter, card_counter))
                source_txt = np.nan
            except NoSuchElementException:
                log_file.write("LOG: page {}: card {}: Source: NoSuchElementException: returning NA\n".format(page_counter, card_counter))
                source_txt = np.nan

            ## IMAGE DOWNLOAD
            try:
                # grab the image element
                img_element = child_div.find("img", {"class": "itemimage"})

                # image URL attempt 1 (works in most cases)
                image_url = img_element["data-zoom-img"]

                # image URL attempt 2
                # if the resulting image is less than 5 kb, it's probably not an actual image,
                # just a placeholder file in their database, so try option 2
                image_response = requests.get(image_url)  # load image1 into memory
                if len(image_response.content) < 5120:  # 5kb = 5120 bytes
                    log_file.write("LOG: page {}: card {}: Image: Image < 5KB, attempting image 2\n".format(page_counter, card_counter))
                    image_url = img_element["backup-img"]  # still not fully confident in this, but it does work.
                    image_response = requests.get(image_url) # load image2 into memory, replacing image1

                # creating the card image filename
                match = re.search(r'\.([a-zA-Z]+)$', image_url)  # use a regular expression to get the file extension
                if match:
                    file_extension = match.group(1)  # extract the extension from the match object
                cardimage_filename = image_save_dir + "/card" + str(card_counter) + "_PSA" + grade_num_str + "." + file_extension  # full image path

                # saving ths image
                with open(cardimage_filename, "wb") as f:
                    f.write(image_response.content)  # save it

            except AttributeError:
                log_file.write("ERROR: page {}: card {}: Image: AttributeError\n".format(page_counter, card_counter))
                card_counter +=1
                continue  # skip to the next image
            except NoSuchElementException:
                log_file.write("ERROR: page {}: card {}: Image: NoSuchElementException\n".format(page_counter, card_counter))
                card_counter +=1
                continue  # skip to the next image
            except KeyError:
                log_file.write("ERROR: page {}: card {}: Image: KeyError (data-zoom-img not found)\n".format(page_counter, card_counter))
                card_counter +=1
                continue  # skip to the next image

            # print(card_counter)
            # print(desc_txt)
            # print(grade_txt)
            # print(grade_num_str)
            # print(price_txt)
            # print(source_txt)
            # print(cardimage_filename)
            # print(image_url)
            # print("\n")

            # add metadata for card to the metadata df
            metadata_df.loc[card_counter] = [card_counter, grade_txt, cardimage_filename, price_txt, desc_txt, source_txt]
            metadata_df.to_pickle(metadata_pickle_filename)  # save the metadata

            # go to the next card
            card_counter +=1
            
except KeyboardInterrupt:
    # Handle the case when the user presses Ctrl+C
    print('Script interrupted by user')
    metadata_df.to_pickle(metadata_pickle_filename)  # save the metadata
    log_file.close()  # close the log file
    sys.exit(0)