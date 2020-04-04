import requests
from bs4 import BeautifulSoup

import os
import json
import csv
import pandas as pd
import numpy as np


# GENERAL DATA FUNCTIONS

def link_to_gameid(link):
    return link.split('/')[2]

def create_directories(game_ids):
	for game_id in game_ids:
	    os.mkdir('./json_data/game_' + game_id)


def get_list_of_filenames(game_id):

	directory = './json_data/game_' + str(game_id)

	filenames = []

	for filename in os.listdir(directory):
	    if filename.endswith(".json") and filename[-6].isdigit() and filename[-7].isdigit() and filename[-8].isdigit():
	        filenames.append(filename)
	        
	filenames.sort()

	return filenames

def create_csv_summary(game_id, filenames = None):

	username_list = []
	rating_list = []

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
	            
	with open('./json_data/game_' + game_id + '/' + game_id + '_summary.csv', 'w') as f:
	    writer = csv.writer(f)
	    writer.writerows(zip(username_list, rating_list))

def clean_username(name):
	"""
	Replaces ',' with '_' for now
	"""
	return name.replace(',','_')

def get_game_names(raw_id_list_input):
    df = pd.read_csv('games_master_list.csv')
    game_ids = df['link'].map(lambda x: link_to_gameid(x))
    game_names = df['name']
    
    game_names_output = []
    
    for id_input in raw_id_list_input:
        game_names_output.append(game_names[np.argwhere(game_ids == id_input)[0][0]])
        
    return game_names_output

# API FUNCTIONS


# API calls go to this structure:
url_main_1 = "https://api.geekdo.com/api/collections?ajax=1&objectid="
# object_id = str(174430)
url_main_2 = "&objecttype=thing&oneperuser=1&pageid="
# page_id = str(1)
url_main_3_rated = "&rated=1&require_review=true&showcount=50&sort=review_tstamp"
url_main_3_all = "&require_review=true&showcount=50&sort=review_tstamp"


def get_three_digit_code(input_number):
    if input_number < 10:
        return "00" + str(input_number)
    elif input_number < 100:
        return "0" + str(input_number)
    else:
        return str(input_number)

def handle_one_api_request(game_id_input, page_num_input, rated_only = True):
    response_to_save = get_api_response(game_id_input, page_num_input, rated_only)
    save_response_as_json(response_to_save, game_id_input, page_num_input)
    return is_empty_page_response(response_to_save)

def get_api_response(game_id_input, page_num_input, rated_only = True):
    if rated_only:
        url_main_3 = url_main_3_rated
    else:
        url_main_3 = url_main_3_all

    url = url_main_1 + game_id_input + url_main_2 + str(page_num_input) + url_main_3
    return requests.get(url)

def save_response_as_json(response_input, game_id_input, page_num_input):
    with open(
        './json_data/game_' + game_id_input + '/' + 
        game_id_input + '_' + get_three_digit_code(page_num_input) + 
        '.json', 'w') as outfile:
        # example: ./json_data/game_174430/174430_001.json
        json.dump(response_input.json(), outfile)

def is_empty_page_response(response_input):
            
    return is_empty_page_json(response_input.json())

def is_empty_page_json(json_input):
    empty_page = False
    if 'items' in json_input.keys():
        if len(json_input['items']) == 0:
            empty_page = True
    else:
        empty_page = True
            
    return empty_page

