import glob
import os

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder

from NBAScrapper.src.repository import PredictionRepository, GameRepository
from NBAScrapper.src.utils import DataBase
from NBAScrapper.src.utils.DataBase import Connection


CSV_NAME = "team_game"
RESULT_NAME = "visitor_win"
NUM_PREVIOUS_GAME = 0
IS_FULL = False
SCALER = "StandardScaler"
CF = SGDClassifier()


def create_dataset(connection: Connection, season: int, is_prediction: bool, is_current_season: bool):
    """Create the dataset from the season to predict results"""
    vars = ['game_id', 'visitor_team', 'home_team', 'date', 'month', 'season',
            'tp_v', 'tpp_v', 'dp_v', 'dpp_v', 'ft_v', 'ftp_v', 'tp_h', 'tpp_h', 'dp_h', 'dpp_h', 'ft_h', 'ftp_h']
    if is_prediction:
        vars.append('to_predict')
        games = PredictionRepository.get_games_team_last_games_predict(connection, season)
    else:
        vars.append(RESULT_NAME)
        games = PredictionRepository.get_games_team_last_games(connection, season)
    games = pd.DataFrame(games, columns=vars)
    min_season = games["season"].min()

    for i in range(len(games)):
        if games.loc[i, "season"] == min_season:
            break

        if IS_FULL:
            visitor_games = games[((games.visitor_team == games.loc[i, "visitor_team"]) |
                                   (games.home_team == games.loc[i, "visitor_team"])) &
                                  (games.date < games.loc[i, "date"]) &
                                  (games.season > (games.loc[i, 'season'] - 2))]
            home_games = games[((games.visitor_team == games.loc[i, "home_team"]) |
                                (games.home_team == games.loc[i, "home_team"])) &
                               (games.date < games.loc[i, "date"]) &
                               (games.season > (games.loc[i, 'season'] - 2))]
        else:
            visitor_games = games[(games.visitor_team == games.loc[i, "visitor_team"]) &
                                  (games.date < games.loc[i, "date"]) &
                                  (games.season > (games.loc[i, 'season'] - 2))]
            home_games = games[(games.home_team == games.loc[i, "home_team"]) &
                               (games.date < games.loc[i, "date"]) &
                               (games.season > (games.loc[i, 'season'] - 2))]

        tp_v = 0
        tpp_v = 0
        dp_v = 0
        dpp_v = 0
        ft_v = 0
        ftp_v = 0
        tp_h = 0
        tpp_h = 0
        dp_h = 0
        dpp_h = 0
        ft_h = 0
        ftp_h = 0

        cont = NUM_PREVIOUS_GAME
        for j in visitor_games.index:
            if games.loc[i, "visitor_team"] == visitor_games.loc[j, "visitor_team"]:
                tp_v += visitor_games.loc[j, "tp_v"]
                tpp_v += visitor_games.loc[j, "tpp_v"]
                dp_v += visitor_games.loc[j, "dp_v"]
                dpp_v += visitor_games.loc[j, "dpp_v"]
                ft_v += visitor_games.loc[j, "ft_v"]
                ftp_v += visitor_games.loc[j, "ftp_v"]
            elif IS_FULL:
                tp_v += visitor_games.loc[j, "tp_h"]
                tpp_v += visitor_games.loc[j, "tpp_h"]
                dp_v += visitor_games.loc[j, "dp_h"]
                dpp_v += visitor_games.loc[j, "dpp_h"]
                ft_v += visitor_games.loc[j, "ft_h"]
                ftp_v += visitor_games.loc[j, "ftp_h"]

            cont -= 1
            if cont == 0:
                break

        cont = NUM_PREVIOUS_GAME
        for j in home_games.index:
            if games.loc[i, "home_team"] == home_games.loc[j, "home_team"]:
                tp_h += home_games.loc[j, "tp_h"]
                tpp_h += home_games.loc[j, "tpp_h"]
                dp_h += home_games.loc[j, "dp_h"]
                dpp_h += home_games.loc[j, "dpp_h"]
                ft_h += home_games.loc[j, "ft_h"]
                ftp_h += home_games.loc[j, "ftp_h"]
            elif IS_FULL:
                tp_h += home_games.loc[j, "tp_v"]
                tpp_h += home_games.loc[j, "tpp_v"]
                dp_h += home_games.loc[j, "dp_v"]
                dpp_h += home_games.loc[j, "dpp_v"]
                ft_h += home_games.loc[j, "ft_v"]
                ftp_h += home_games.loc[j, "ftp_v"]

            cont -= 1
            if cont == 0:
                break

        if NUM_PREVIOUS_GAME > 0:
            games.loc[i, "tp_v"] = tp_v / NUM_PREVIOUS_GAME
            games.loc[i, "tpp_v"] = tpp_v / NUM_PREVIOUS_GAME
            games.loc[i, "dp_v"] = dp_v / NUM_PREVIOUS_GAME
            games.loc[i, "dpp_v"] = dpp_v / NUM_PREVIOUS_GAME
            games.loc[i, "ft_v"] = ft_v / NUM_PREVIOUS_GAME
            games.loc[i, "ftp_v"] = ftp_v / NUM_PREVIOUS_GAME
            games.loc[i, "tp_h"] = tp_h / NUM_PREVIOUS_GAME
            games.loc[i, "tpp_h"] = tpp_h / NUM_PREVIOUS_GAME
            games.loc[i, "dp_h"] = dp_h / NUM_PREVIOUS_GAME
            games.loc[i, "dpp_h"] = dpp_h / NUM_PREVIOUS_GAME
            games.loc[i, "ft_h"] = ft_h / NUM_PREVIOUS_GAME
            games.loc[i, "ftp_h"] = ftp_h / NUM_PREVIOUS_GAME

    games = games[games.season != min_season]
    if is_current_season:
        games = games.drop(columns=["date", "season"])
    else:
        games = games.drop(columns=["date"])

    return games


def data_train(data, result_name: str):
    """Separate and mix data"""
    X_train, X_test, y_train, y_test = train_test_split(
        data.drop(result_name, axis='columns'),
        data[result_name],
        train_size=0.8,
        random_state=1234,
        shuffle=True
    )

    return X_train, X_test, y_train, y_test


def preprocessor_model(scaler, X_train, X_test):
    """Preprocesses the data model before creating the grid"""
    numeric_cols = X_train.select_dtypes(include=['float64', 'int']).columns.to_list()
    cat_cols = X_train.select_dtypes(include=['object', 'category']).columns.to_list()

    if scaler == "StandardScaler":
        numeric_transformer = Pipeline(
            steps=[('scaler', StandardScaler())]
        )
    elif scaler == "MinMaxScaler":
        numeric_transformer = Pipeline(
            steps=[('scaler', MinMaxScaler())]
        )
    else:
        print("ERROR al leer el tipo de scaler")
        numeric_transformer = None

    categorical_transformer = Pipeline(
        steps=[('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ('numeric', numeric_transformer, numeric_cols),
            ('cat', categorical_transformer, cat_cols)
        ],
        remainder='passthrough',
        verbose_feature_names_out=False
    ).set_output(transform="pandas")

    X_train_prep = preprocessor.fit_transform(X_train)
    X_test_prep = preprocessor.transform(X_test)

    return X_train_prep, X_test_prep


def get_full_csv_name(season: int) -> str:
    """Return the full name of the files to save"""
    if IS_FULL:
        full_csv_name = str(season) + '_full_' + str(CSV_NAME) + '_' + str(NUM_PREVIOUS_GAME)
    else:
        full_csv_name = str(season) + '_court_' + str(CSV_NAME) + '_' + str(NUM_PREVIOUS_GAME)

    return full_csv_name


def has_model(season: int) -> bool:
    """Check if the model of the season has been created"""
    for file in glob.glob("src/model/*"):
        if file.split("\\")[1][:4] == str(season):
            return True

    return False


def has_csv(season: int) -> bool:
    """Check if the csv of the season has been created"""
    for file in glob.glob("src/csv/*"):
        if file.split("\\")[1][:4] == str(season):
            return True

    return False


def create_current_model(connection: Connection, season: int):
    """Update the current grid model"""
    full_csv_name = get_full_csv_name(season)

    games_comp = create_dataset(connection, season, False, True)
    path_exist = os.path.exists("src/csv")
    if not path_exist:
        os.makedirs("src/csv")
    games_comp.to_csv('src/csv/' + full_csv_name + '.csv', index=False)
    games = games_comp.drop(columns=["game_id"])

    games['tpp_v'] = games['tpp_v'].astype(float)
    games['dpp_v'] = games['dpp_v'].astype(float)
    games['ftp_v'] = games['ftp_v'].astype(float)
    games['tpp_h'] = games['tpp_h'].astype(float)
    games['dpp_h'] = games['dpp_h'].astype(float)
    games['ftp_h'] = games['ftp_h'].astype(float)

    X_train, X_test, y_train, y_test = data_train(games, RESULT_NAME)
    X_train_prep, X_test_prep = preprocessor_model(SCALER, X_train, X_test)
    grid = CF.fit(X=X_train_prep, y=y_train)

    # Save the model
    path_exist = os.path.exists("src/model")
    if not path_exist:
        os.makedirs("src/model")
    joblib.dump(grid, "src/model" + full_csv_name + ".sav")


def predict_new_games(connection: Connection, season: int):
    """Predict which team will win in the games what have not been played yet"""
    full_csv_name = get_full_csv_name(season)
    # Load the model
    model = joblib.load("src/model/" + full_csv_name + ".sav")
    games = create_dataset(connection, season, True, True)

    games['tpp_v'] = games['tpp_v'].astype(float)
    games['dpp_v'] = games['dpp_v'].astype(float)
    games['ftp_v'] = games['ftp_v'].astype(float)
    games['tpp_h'] = games['tpp_h'].astype(float)
    games['dpp_h'] = games['dpp_h'].astype(float)
    games['ftp_h'] = games['ftp_h'].astype(float)

    full_games_to_predict = games[games.to_predict == 1]
    if len(full_games_to_predict) > 0:
        games_train = games[games.to_predict == 0]
        games_to_predict = full_games_to_predict.drop(columns=["game_id", "to_predict"])
        games_train = games_train.drop(columns=["game_id", "to_predict"])

        games_train_prep, games_to_predict_prep = preprocessor_model(SCALER, games_train, games_to_predict)
        result = model.predict(games_to_predict_prep)
        for i in range(len(full_games_to_predict)):
            game_id = full_games_to_predict.iloc[i].game_id
            if result[i] == 1:
                visitor_win = full_games_to_predict.iloc[i].visitor_team
            else:
                visitor_win = full_games_to_predict.iloc[i].home_team
            GameRepository.save_prediction(connection, game_id, visitor_win)
        DataBase.commit(connection)


def predict_season_games(connection: Connection, season: int):
    """Predict which team will win in the games from a season"""
    full_csv_name = get_full_csv_name(season)

    games = create_dataset(connection, season, False, False)
    path_exist = os.path.exists("src/csv")
    if not path_exist:
        os.makedirs("src/csv")
    games.to_csv('src/csv/' + full_csv_name + '.csv', index=False)

    games['tpp_v'] = games['tpp_v'].astype(float)
    games['dpp_v'] = games['dpp_v'].astype(float)
    games['ftp_v'] = games['ftp_v'].astype(float)
    games['tpp_h'] = games['tpp_h'].astype(float)
    games['dpp_h'] = games['dpp_h'].astype(float)
    games['ftp_h'] = games['ftp_h'].astype(float)

    for month in games[games.season == season]['month'].unique():
        games_train = games[games.index > games.index[
            (games.season == season) & (games.month == month)]
                [len(games.index[(games.season == season) & (games.month == month)])-1]
        ]
        y_train = games_train[RESULT_NAME]
        games_train = games_train.drop(columns=["game_id", "season", RESULT_NAME])
        full_games_test = games[(games.season == season) & (games.month == month)]
        games_test = full_games_test.drop(columns=["game_id", "season", RESULT_NAME])
        games_train_prep, games_test_prep = preprocessor_model(SCALER, games_train, games_test)
        grid = CF.fit(X=games_train_prep, y=y_train)
        result = grid.predict(games_test_prep)

        for i in range(len(full_games_test)):
            game_id = full_games_test.iloc[i].game_id
            if result[i] == 1:
                prediction = full_games_test.iloc[i].visitor_team
            else:
                prediction = full_games_test.iloc[i].home_team
            GameRepository.save_prediction(connection, game_id, prediction)

        DataBase.commit(connection)
