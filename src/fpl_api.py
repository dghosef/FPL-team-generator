# https://towardsdatascience.com/looping-through-the-fantasy-premier-league-api-element-summary-endpoint-to-download-player-df4ab5151fcb
import os
import pandas as pd
import requests
from pprint import pprint
from player import Player, position_numbers


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
            gameweek_dict.setdefault(player_id, list()).\
                append(int(minutes_played))
    players_dict = dict()
    for player_index in players_df.index:
        player_id = players_df.id[player_index]
        player_name = players_df.web_name[player_index]
        position = position_numbers[players_df.element_type[player_index]]
        current_player = Player(player_name, position)
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


if __name__ == '__main__':
    (get_player_history([1, 3, 5]))
