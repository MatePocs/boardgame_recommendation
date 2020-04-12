import pandas as pd
import numpy as np

k_factor = 10

class kNNMeans_Recommender:

    """
    Recommender that works with k-Nearest Neighbours with Means Method. 
    See kNNWithMeans section for the math background:
    https://surprise.readthedocs.io/en/stable/knn_inspired.html
    The reason why I added this class is because the classes in surprise
    are only able to recommend for a user after training on the whole data
    with the user included. With simple kNN methods, it is possible to train
    the model once, and recommend for a new user without re-training. 

    Parameters
    ----------
    distance_dataframe : a pandas DataFrame where the number of rows and columns is 
        equal to the number of items, individual elements are the distance from one 
        item to the other, indeces and column names are names of items

    average_ratings_by_game : a pandas DataFrame, index is name of the game, each row
        contains the average of ratings of the game from the analysed population
    """

    def __init__(self, distance_dataframe, average_ratings_by_game):

        self.distance_dataframe = distance_dataframe
        self.average_ratings_by_game = average_ratings_by_game

    def estimate_all_for_user(self, user_input_dict):
        """
        Estimate all the unknown games to a particular user. 

        Parameters
        ----------
        user_input_dict: a dictionary where keys are names of the games, values are
            ratings the user gave to those games

        Returns
        ----------
        estimated_ratings: dictionary where keys are game names, values are estimated
            ratings, please note that we are not giving estimations for games the user
            already rated
        """

        estimated_ratings = {}

        for game_to_estimate in self.distance_dataframe.columns:
            if game_to_estimate in user_input_dict.keys():
                pass
                # going to leave it here in case we ever want to estimate, but pass as a defalt
            else:
                # we need to estimate that particular game, call the corresponding function
                distances_from_game = self.distance_dataframe[game_to_estimate].copy()
                distances_from_game.sort_values(inplace = True, ascending = False)
                estimated_ratings[game_to_estimate] = \
                self.estimate_game(game_to_estimate, distances_from_game, user_input_dict)

        return estimated_ratings
                

    def estimate_game(self, game_to_estimate, distances_from_game, user_input_dict):
        """
        Estimate the rating of one particular game, based on a user's ratings. 

        Parameters
        ----------
        game_to_estimate: name of the game we want to estimate score for

        distances_from_game: list of distances between game_to_estimate and 
            other games, this is the result of the model being trained on the
            large population

        user_input_dict: a dictionary where keys are names of the games, values are
            ratings the user gave to those games

        Returns
        ----------
        estimation: estimated rating of the particular game

        """

        numerator = 0
        denominator = 0
        number_of_ratings_used = 0

        i = 1
        while i < len(distances_from_game):
            # looping through all the games
            if distances_from_game.index[i] in user_input_dict.keys():

                number_of_ratings_used += 1
                if number_of_ratings_used == k_factor:
                    # if we already used up 10 games, skip the others
                    i = len(distances_from_game) + 1

                current_game = distances_from_game.index[i]
                current_distance = distances_from_game[current_game]
                current_rating = user_input_dict[current_game]
                denominator += current_distance
                numerator += current_distance * \
                (user_input_dict[current_game] - self.average_ratings_by_game.loc[current_game]['rating'])
                # see surprise library for math background

            i += 1
            
        estimation = self.average_ratings_by_game.loc[game_to_estimate]['rating'] + numerator / denominator

        return estimation

