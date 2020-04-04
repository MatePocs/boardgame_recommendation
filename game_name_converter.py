import pandas as pd
import numpy as np
import bgg_data_func


class NameConverter:

    def __init__(self, game_csv_filepath):

        df = pd.read_csv(game_csv_filepath)

        self.id_to_name_dict = {}

        game_names = df['name']
        game_ids = df['link'].map(lambda x: bgg_data_func.link_to_gameid(x)) 

        for index in range(0, len(game_ids)):
            self.id_to_name_dict[str(game_ids[index])] = game_names[index]

    def get_game_name_from_id(self, game_id):
        return self.id_to_name_dict[str(game_id)]

