# Boardgame Recommendation System

## Summary
In this project, I collect the user ratings from [BoardgameGeek](https://boardgamegeek.com/)'s top 100 games, and train a collaborative-filtering recommendation system on it. The user enters a few games with their ratings, and the model returns a list of games the user would probably rate high. 

## Keywords
BeatifulSoup, Web Scraping, API requests, Collaborative-Filtering Recommender Systems, Scikit-Surprise, Cross-Validation, K-Nearest Neighbour, Singular Value Decomposition, Stochastic Gradient Descent, Alternating Least Squares, 

## Links
I published a series of articles on the topic in Towards Data Science, see the links below: 
<br>
[Part 1 - KNN-Style Recommenders](https://towardsdatascience.com/how-to-build-a-memory-based-recommendation-system-using-python-surprise-55f3257b2cf4)
<br>
[Part 2 - My Additional Python Code](https://towardsdatascience.com/my-python-code-for-flexible-recommendations-b4d838e9e0e0)
<br>
[Part 3 - Matrix Factorisation Recommenders](https://towardsdatascience.com/how-to-build-a-model-based-recommendation-system-using-python-surprise-2df3b77ab3e5)

This project was the basis of my capstone project at Flatiron School:
<br>
[Presentation](https://docs.google.com/presentation/d/1qKxO2TLHGmGMCSOYO37v1a-bLFWAbEmGfutsNbDwyew/edit#slide=id.p)

## Data
I obtained the data using a combination of web scraping with `BeautifulSoup` and `API` requests. For each game, I collected all the ratings where the user actually rated the game (as opposed to entries where they just mark the game as owned, or put in a text comment) as of March 31, 2020. 

The complete data contains 2.3m ratings from over 200k users. The average number of games rated by an individual user is about 10, meaning the database is about 90% sparse. 

Most of the users have a relatively high average rating.  

![chart showing number of users per average ratings](./charts/users_by_average_ratings.png)

A large portion of the users rated only one game, and there are users who rated more than 40 (and in fact, there are users who rated all the 100 games).

![chart showing number of users per total number of ratings](./charts/users_by_number_of_ratings.png)

## Modelling

### Metric
I am using `RMSE`, which stands for Root Mean Squared Error, to compare the performance of different models. Other available metrics in the `Surprise` package were `MAE` and `MSE`. 

### Model Training Process
I trained all the different available models in the `surprise` library. My process was the following: 
- for the selected model type, tuned the hyperparameters using cross-validation, either with the built-in `cross_validate` method, or `GridSearchCV`;
- I fit the model with the selected hyperparameters on the training dataset;
- tested the performance on the test dataset;
- repeated the process with all the model types. 

### KNN-Type Models

The three available models in `surprise` are: `KNNBaseline`, `KNNWithMeans`, `KNNWithZScore`. They all build on similarity matrices, the difference is that `KNNWithMeans` also takes average ratings into account, while `KNNWithZScores` also modifies with standard deviation. The best performing model was `KNNWithMeans` with `k = 10` and `similarity_option = pearson`, the test `RMSE` score was 1.253.  

### Models with Matrix Factorisation

In these models, a Singular Value Decomposition method is used to reduce the dimensions to the latent factors. There are two models in the `surprise` library, `SVD` and `SVDpp`. The difference between the two is that `SVDpp` also utilises the information that a user rated a certain item at all. 

These model runs were very computational-heavy, especially with the `GridSearchCV` calculations, so I set up a Virtual Machine on Google Cloud Platform and ran the calculations there. 

The best performing model was the default `SVD`, with parameters `n_factors= 50`, `n_epochs=20`, `lr_all=0.006`, and `reg_all=0.7`. The `RMSE` score was 1.3214. 

### Combination of KNN-Type and Matrix Factorisation

The corresponding model in `surprise` is `KNNBaseline`. This class combines the other two groups by first fitting a baseline rating using matrix factorisation techniques, and then tries to explain the remaining variation with a KNN-Type approach. There are two different baseline convergence patterns built in `surprise`: 

- `SGD` is the Stochastic Gradient Descent where the parameters are tuned every step based on the cost function, 
- `ALS` is the Alternating Least Squares method, where the two latent factor matrices are determined step by step. In every step, we assume that one of the matrices is fix and optimal, and then tweak the other based on the Least Squares method, which has a closed solution. This process is repeated with the other matrix being assumed optimal. 

Out of the two methods, `ALS` performed slightly better, `RMSE` score was 1.2456. 

### Misc. Models

For the sake of completeness, I trained two other available models in `surprise` library, `SlopeOne` and `CoClustering`, but did not consider using them for predictions over their more sophisticated counterparts. 

## Prediction Functionality
The best-performing model was the `KNNWithBaseline` model. However, one issue with these models is that in order to make predictions, the user needs to be part of the training data. So for a new user, we would need to add their ratings to the large database, and run again. That is fine if you want to give regular recommendations for all the users, but I wanted to showcase my model's capabilities on the run. 

I picked the `KNNWithMeans` model, because it was the best-performing simple KNN-Style model. Its performance actually was almost as good as the best model, the hybrid `KNNWithBaseline`. 

I created a Python class that used the results of the `surprise` library model fitting, but was capable of creating recommendations for a user without re-running the model. 

A couple of examples of predictions (I did not build a graphical interface for the model, these images are from my presentation): 

![recommendation example 1](./charts/recomm_1.png)

![recommendation example 2](./charts/recomm_2.png)


## Files
The project contains the following files: 
- Jupyter notebooks: 
    - `01_dataprep.ipynb`: process of collecting and organising the data
    - `02_modelling_neighbours.ipynb`: the `kNN` models from `surprise`, training and cross-validating
    - `03_modelling_latent_factors.ipynb`: the `SVD` models from `surprise`, training and cross-validating
    - `04_results_data_and_predictions.ipynb`: all the code I needed for final presentation, including data visualisations and prediction functionality
- Individual Python scripts:
    - `bgg_data_func.py`: functions for data collecting, specifically tuned for boardgamegeek
    - `bgg_model_func.py`: functions for modelling
    - `game_name_converter.py`: converts raw boardgamegeek game id's to names
    - `recomm_func.py`: contains the main recommender class, `kNNMeansRecommender`
- Data:
    - `games_master_list.csv`: list of games in the project, along with boardgamegeek links and publication year
- Results (in `results` folder):
    - `top_10_similar_games_..._.csv`: for each game, saved the 10 closest games, according to three distance metric, `MSD`, `cosine`, and `pearson`
    - `kNN_..._scores.csv`: the `rmse` scores of `cross_validate` results of different model types
