import pandas as pd
import numpy as np
import bgg_data_func


class NameConverter:
    """
    Basically a dynamically-created dictionary, main part is setting up list of 
    game names and raw ids from a master games list. Ids are the boardgamegeek ids
    of the games, which is a 1-6 digit long number, can be observed in the url.

    Parameters:
    ----------
    game_csv_filepath: filepath to the master game list, which is assumed to have a 
        'name' and a 'link' column
    """

    def __init__(self, game_csv_filepath):

        df = pd.read_csv(game_csv_filepath)

        self.id_to_name_dict = {}

        game_names = df['name']
        game_ids = df['link'].map(lambda x: bgg_data_func.link_to_gameid(x)) 
        # we are getting the id from the link, using functions in the bgg_data_func file

        for index in range(0, len(game_ids)):
            self.id_to_name_dict[str(game_ids[index])] = game_names[index]

    def get_game_name_from_id(self, game_id):
        return self.id_to_name_dict[str(game_id)]

