import pandas as pd
import numpy as np


# SIMILARITY METRIC FUNCTIONS

def return_top_similar_dataframe(similarity_matrix, raw_ids, top_x):
    """
    Takes a similarity matrix, where each element is the distance between 
    two items. For each item, returns the top_x similar items, sorted. 

    Parameters:
    ----------
    similarity_matrix: a pandas DataFrame with distances

    raw_ids: ids to use in the result

    top_x: an integer, defines how many similar games we want to be listed
        for each game


    Returns:
    --------
    similarity_df: a pandas DataFrame, with top_x + 1 columns, first column
        is called 'game', which is a list of games, and then we have similar_1, 
        similar_2, ..., similar_x columns, with the names of the closest games
    """

    length = similarity_matrix.shape[0]

    closest_ids = np.zeros((top_x,length))

    for item in range(0,length):
    
        similarity_metrics = similarity_matrix[item]
        
        sorted_metrics, sorted_raw_ids = zip(*sorted(zip(similarity_metrics, raw_ids))) 
        
        for index in range(0, top_x):
            closest_ids[index][item] = sorted_raw_ids[-2-index]


        similarity_df = pd.DataFrame()
        similarity_df['game'] = raw_ids
        for index in range(0, top_x): 
            similarity_df['similar_' + str(index + 1)] = closest_ids[index].astype(int)

    return similarity_df