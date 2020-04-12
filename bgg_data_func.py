import requests
from bs4 import BeautifulSoup

import os
import json
import csv
import pandas as pd
import numpy as np

# ----------------------------------------
# GENERAL DATA FUNCTIONS
# ----------------------------------------

def link_to_gameid(link):
    """
    Returns the game_id from the link. Splits link by '/' characters, returns index 2
    """
    return link.split('/')[2]

def create_directories(game_ids):
    """
    For each id in game_ids, creates a folder in json_data folder.
    """
    for game_id in game_ids:
        os.mkdir('./json_data/game_' + game_id)


def get_list_of_filenames(game_id):
    """
    For a certain game_id, navigates to the corresponding json_data folder, creates a list
    of the files that are not empty.
    """

    directory = './json_data/game_' + str(game_id)

    filenames = []

    for filename in os.listdir(directory):
        if filename.endswith(".json") and filename[-6].isdigit() and filename[-7].isdigit() and filename[-8].isdigit():
            filenames.append(filename)
            
    filenames.sort()

    return filenames

def create_csv_summary(game_id, filenames = None, detailed = False):
    """
    Creates a summary file for a certain game, in the json_data folder, and saves it in a csv.

    Parameters:
    ----------
    game_id: id of the game to be processed

    filenames: optional input, if None, will process all the files in the folder

    detailed: optional input, if set to True, also includes the country and ownership
        status of user - item pairs
    """

    username_list = []
    rating_list = []
    
    # the following is for detailed view only
    own_list = []
    country_list = []

    if filenames == None:
        filenames = get_list_of_filenames(game_id)

    for filename in filenames:
        with open('./json_data/game_' + game_id + '/' + filename) as json_file:
            data = json.load(json_file)
            if not(is_empty_page_json(data)):
                for usernum, user_dict in enumerate(data['items']):
                    if not(type(user_dict['user']) == type(None)):
                        username = clean_username(user_dict['user']['username'])
                        username_list.append(username)
                        rating_list.append(user_dict['rating'])
                        if detailed:
                            if 'own' in user_dict['status'].keys():
                                own_list.append(user_dict['status']['own'])
                            else:
                                own_list.append(False)
                            country_list.append(user_dict['user']['country'])

    if detailed:
        with open('./json_data/game_' + game_id + '/' + game_id + '_summary_detailed.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(zip(username_list, rating_list, own_list, country_list))
    else:
        with open('./json_data/game_' + game_id + '/' + game_id + '_summary.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(zip(username_list, rating_list))

def clean_username(name):
    """
    Replaces ',' with '_' in the string.
    """
    return name.replace(',','_')
    # this was the only issue I ran into while processing the names

def get_game_names(raw_id_list_input):
    """
    Returns a list of game names from the master games file. 
    """

    df = pd.read_csv('games_master_list.csv')
    game_ids = df['link'].map(lambda x: link_to_gameid(x))
    game_names = df['name']
    
    game_names_output = []
    
    for id_input in raw_id_list_input:
        game_names_output.append(game_names[np.argwhere(game_ids == id_input)[0][0]])
        
    return game_names_output

# ----------------------------------------
# API FUNCTIONS
# ----------------------------------------


# API calls go to this structure:
url_main_1 = "https://api.geekdo.com/api/collections?ajax=1&objectid="
# object_id = str(174430)
url_main_2 = "&objecttype=thing&oneperuser=1&pageid="
# page_id = str(1)
url_main_3_rated = "&rated=1&require_review=true&showcount=50&sort=review_tstamp"
url_main_3_all = "&require_review=true&showcount=50&sort=review_tstamp"


def get_three_digit_code(input_number):
    """
    Re-codes file names so for example '3' becomes '003', '12' becomes '012' etc. 
    """

    if input_number < 10:
        return "00" + str(input_number)
    elif input_number < 100:
        return "0" + str(input_number)
    else:
        return str(input_number)

def handle_one_api_request(game_id_input, page_num_input, rated_only = True):
    """
    Runs and saves one API request. 

    Parameters:
    ----------
    game_id_input: boardgamegeek ID of a game

    page_num_input: number of ratings page we want to save

    rated_only: optional input, if set to False, also saves user entries without
        1-10 ratings, for example if a user only put in a text comment

    Returns:
    ---------
    is_empty_page_response: a boolean, if True, the page was empty, which means
        there is no need to call the next page
    """

    response_to_save = get_api_response(game_id_input, page_num_input, rated_only)
    # runs the request
    save_response_as_json(response_to_save, game_id_input, page_num_input)
    # saves the result in a json file
    return is_empty_page_response(response_to_save)

def get_api_response(game_id_input, page_num_input, rated_only = True):
    """
    Requestss one game's one page of the ratings, can only be called page by page,
    no option to gather all the pages at once, unfortunately. 

    Parameters:
    ----------
    game_id_input: boardgamegeek ID of a game

    page_num_input: number of ratings page we want to save

    rated_only: optional input, if set to False, also saves user entries without
        1-10 ratings, for example if a user only put in a text comment

    Returns:
    ---------
    requests.get(url): the result of the request
    """
    if rated_only:
        url_main_3 = url_main_3_rated
    else:
        url_main_3 = url_main_3_all

    url = url_main_1 + game_id_input + url_main_2 + str(page_num_input) + url_main_3
    return requests.get(url)

def save_response_as_json(response_input, game_id_input, page_num_input):
    """
    Saves one request as a json file in the corresponding folder.

    Prameters:
    ----------
    response_input: the response to save as json

    game_id_input: game id, to be used in finding the corresponding folder and 
        naming the file

    page_num_input: number of page, to be used in naming the file
    """
    with open(
        './json_data/game_' + game_id_input + '/' + 
        game_id_input + '_' + get_three_digit_code(page_num_input) + 
        '.json', 'w') as outfile:
        # example: ./json_data/game_174430/174430_001.json
        json.dump(response_input.json(), outfile)

def is_empty_page_response(response_input):
    """
    Checks if an input is empty, by calling the is josn empty function.
    """
            
    return is_empty_page_json(response_input.json())

def is_empty_page_json(json_input):
    """
    Checks if a page is empty. If list of 'items' is 0, there are no ratings, and 
    the page is empty. If the page is empty, no need to call the next page. 

    Returns:
    --------
    empty_page: a boolean, True, if the page is empty
    """
    empty_page = False
    if 'items' in json_input.keys():
        if len(json_input['items']) == 0:
            empty_page = True
    else:
        empty_page = True
            
    return empty_page

