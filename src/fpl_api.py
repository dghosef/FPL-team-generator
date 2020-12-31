# https://towardsdatascience.com/looping-through-the-fantasy-premier-league-api-element-summary-endpoint-to-download-player-df4ab5151fcb
import os
import pandas as pd
import requests
import pickle

from player import Player


def get_team_numbers():
    if not os.path.exists('./data/teams'):
        main_api_endpoint =\
            'https://fantasy.premierleague.com/api/bootstrap-static/'
        main_api_response = requests.get(main_api_endpoint)
        teams_df = pd.DataFrame(main_api_response.json()['teams'])
        teams = dict()
        for team_index in teams_df.index:
            team_id = teams_df.id[team_index]
            team_name = teams_df.short_name[team_index]
            teams[team_id] = team_name
        # https://stackoverflow.com/questions/11218477/how-can-i-use-pickle-to-save-a-dict
        with open('./data/teams', 'wb') as handle:
            pickle.dump(teams, handle)
    else:
        with open('./data/teams', 'rb') as handle:
            teams = pickle.load(handle)
    return teams


def get_player_history(gameweeks, refresh_data=False):
    if not os.path.exists('./data/'):
        os.makedirs('./data/')
    if refresh_data or not os.path.exists('./data/general_info_fpl_api'):
        print("grabbing data from the general information fpl api")
        main_api_endpoint =\
            'https://fantasy.premierleague.com/api/bootstrap-static/'
        main_api_response = requests.get(main_api_endpoint)
        players_df = pd.DataFrame(main_api_response.json()['elements'])
        players_df.to_pickle('./data/general_info_fpl_api')
    else:
        players_df = pd.read_pickle('./data/general_info_fpl_api')
    gameweek_dict = dict()
    if not os.path.exists('./data/gameweeks'):
        os.makedirs('./data/gameweeks')
    for gameweek in gameweeks:
        if os.path.isfile(f'./data/gameweeks/{gameweek}') and \
                not refresh_data:
            gameweek_df = pd.read_pickle(f'./data/gameweeks/{gameweek}')
        else:
            print(f"grabbing data for gameweek {gameweek}")
            gameweek_api_endpoint = ('https://fantasy.premierleague.com/api'
                                     f'/event/{gameweek}/live/')
            gameweek_api_response = requests.get(gameweek_api_endpoint)
            gameweek_df = \
                pd.DataFrame(gameweek_api_response.json()['elements'])
            gameweek_df.to_pickle(f'./data/gameweeks/{gameweek}')
        for player_index in gameweek_df.index:
            player_id = gameweek_df.id[player_index]
            minutes_played = gameweek_df.stats[player_index]['minutes']
            creativity = gameweek_df.stats[player_index]['creativity']
            threat = gameweek_df.stats[player_index]['threat']
            gameweek_dict.setdefault(player_id, [list()] * 3)
            gameweek_dict[player_id][0].append(int(minutes_played))
            gameweek_dict[player_id][1].append(float(creativity))
            gameweek_dict[player_id][2].append(float(threat))
    players_dict = dict()
    teams = get_team_numbers()
    for player_index in players_df.index:
        player_id = players_df.id[player_index]
        player_name = players_df.web_name[player_index]
        player_team = teams[players_df.team[player_index]]
        position = players_df.element_type[player_index]
        current_player = Player(player_name, position, player_team)
        # API multiplies actual cost by 10
        price = players_df.now_cost[player_index] / 10.0
        news = players_df.news[player_index]
        status = players_df.status[player_index]
        players_dict[current_player] = dict()
        players_dict[current_player]['price'] = price
        players_dict[current_player]['id'] = player_id
        players_dict[current_player]['news'] = news
        players_dict[current_player]['status'] = status
        players_dict[current_player]['gw_history'] = \
            gameweek_dict[player_id] if player_id in gameweek_dict else list()
    return players_dict


# excludes cur_gw. Matches retured in format (other team, original team goals, other team goals)
def get_fixtures(cur_gw, refresh_data=False):
    if not os.path.exists('./data/'):
        os.makedirs('./data/')
    if not os.path.exists('./data/fixtures'):
        os.makedirs('./data/fixtures')
    scores = dict()
    for gameweek in range(1, cur_gw):
        if refresh_data or not os.path.exists(f'./data/fixtures/{gameweek}'):
            print(f"grabbing data for gameweek {gameweek}")
            gameweek_api_endpoint = ('https://fantasy.premierleague.com/api/'
                                     f'fixtures/?event={gameweek}')
            gameweek_api_response = requests.get(gameweek_api_endpoint)
            gameweek_df = \
                pd.DataFrame(gameweek_api_response.json())
            gameweek_df.to_pickle(f'./data/fixtures/{gameweek}')
        else:
            gameweek_df = pd.read_pickle(f'./data/fixtures/{gameweek}')
        teams = get_team_numbers()
        for i in range(len(gameweek_df['id'])):
            home_team = teams[gameweek_df['team_h'][i]]
            away_team = teams[gameweek_df['team_a'][i]]
            home_score = gameweek_df['team_h_score'][i]
            away_score = gameweek_df['team_a_score'][i]
            scores.setdefault(home_team, list()). \
                append((away_team, home_score, away_score))
            scores.setdefault(away_team, list()). \
                append((home_team, away_score, home_score))
    return scores


if __name__ == "__main__":
    scores = get_fixtures(3)
    log = True
    if log:
        print(scores)
