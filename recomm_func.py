import pandas as pd
import numpy as np


class kNNMeans_Recommender:

    def __init__(self, distance_dataframe, average_ratings_by_game):

        self.distance_dataframe = distance_dataframe
        self.average_ratings_by_game = average_ratings_by_game

    def estimate_all_for_user(self, user_input_dict):

        estimated_ratings = {}

        for game_to_estimate in self.distance_dataframe.columns:
            if game_to_estimate in user_input_dict.keys():
                pass
                # going to leave it here in case we ever want to estimate, but pass as a defalt
            else:
                # we need to estimate
                distances_from_game = self.distance_dataframe[game_to_estimate].copy()
                distances_from_game.sort_values(inplace = True, ascending = False)
                estimated_ratings[game_to_estimate] = \
                self.estimate_game(game_to_estimate, distances_from_game, user_input_dict)

        return estimated_ratings
                

    def estimate_game(self, game_to_estimate, distances_from_game, user_input_dict):

        numerator = 0
        denominator = 0
        number_of_ratings_used = 0

        i = 1
        while i < len(distances_from_game):
            if distances_from_game.index[i] in user_input_dict.keys():

                number_of_ratings_used += 1
                if number_of_ratings_used == 10:
                    i = len(distances_from_game) + 1

                current_game = distances_from_game.index[i]
                current_distance = distances_from_game[current_game]
                current_rating = user_input_dict[current_game]
                denominator += current_distance
                numerator += current_distance * \
                (user_input_dict[current_game] - self.average_ratings_by_game.loc[current_game]['rating'])

            i += 1
            
        estimation = self.average_ratings_by_game.loc[game_to_estimate]['rating'] + numerator / denominator

        return estimation

