# https://towardsdatascience.com/looping-through-the-fantasy-premier-league-api-element-summary-endpoint-to-download-player-df4ab5151fcb
import pickle
import os
import pandas as pd
import requests
from pprint import pprint
from player import Player, position_numbers
# If player isn't injured and has only been benched 1/4 of last few gamaes he is a starter or Ftsarted 2 in a row


def get_player_history(gameweeks):
    main_api_endpoint =\
        'https://fantasy.premierleague.com/api/bootstrap-static/'
    main_api_response = requests.get(main_api_endpoint)
    players_df = pd.DataFrame(main_api_response.json()['elements'])
    players_dict = dict()
    gameweek_dict = dict()
    if not os.path.exists("gameweeks"):
        os.makedirs("gameweeks")
    for gameweek in gameweeks:
        if os.path.isfile(f"./gameweeks/{gameweek}"):
            gameweek_df = pd.read_pickle(f"./gameweeks/{gameweek}")
        else:
            gameweek_api_endpoint = f'https://fantasy.premierleague.com/api/event/{gameweek}/live/'
            gameweek_api_response = requests.get(gameweek_api_endpoint)
            gameweek_df = pd.DataFrame(gameweek_api_response.json()['elements'])
            gameweek_df.to_pickle(f"./gameweeks/{gameweek}")
        for player_index in gameweek_df.index:
            player_id = gameweek_df.id[player_index]
            minutes_played = gameweek_df.stats[player_index]['minutes']
            gameweek_dict.setdefault(player_id, list()).append(int(minutes_played))
    player_list = list()
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
        players_dict[current_player]['gw_history'] = gameweek_dict[player_id] if player_id in gameweek_dict else list()
    return players_dict

if __name__ == '__main__':
    pprint(get_player_history([1, 3, 5]))
