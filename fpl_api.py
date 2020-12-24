# https://towardsdatascience.com/looping-through-the-fantasy-premier-league-api-element-summary-endpoint-to-download-player-df4ab5151fcb
import pandas as pd
import requests
from pprint import pprint
# If player isn't injured and has only been benched 1/4 of last few gamaes he is a starter or Ftsarted 2 in a row


def get_gw_history(gameweeks):
    main_api_endpoint = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    main_api_response = requests.get(main_api_endpoint)
    players_df = pd.DataFrame(main_api_response.json()['elements'])
    players_dict = dict()
    gameweek_dict = dict()
    for gameweek in gameweeks:
        gameweek_api_endpoint = f'https://fantasy.premierleague.com/api/event/{gameweek}/live/'
        gameweek_api_response = requests.get(gameweek_api_endpoint)
        gameweek_df = pd.DataFrame(gameweek_api_response.json()['elements'])
        for player_index in gameweek_df.index:
            player_id = gameweek_df.id[player_index]
            minutes_played = gameweek_df.stats[player_index]['minutes']
            gameweek_dict.setdefault(player_id, list()).append(int(minutes_played))
    for player_index in players_df.index:
        player_id = players_df.id[player_index]
        player_name = players_df.web_name[player_index]
        news = players_df.news[player_index]
        position = players_df.element_type[player_index]
        status = players_df.status[player_index]
        players_dict[player_name] = dict()
        players_dict[player_name]['id'] = player_id
        players_dict[player_name]['news'] = news
        players_dict[player_name]['status'] = status
        players_dict[player_name]['position'] = position
        players_dict[player_name]['gw_history'] = gameweek_dict[player_id] if player_id in gameweek_dict else list()
        # players_dict[player_name]['gw_history'] = list(current_player_df.minutes)
    return players_dict

if __name__ == '__main__':
    pprint(get_gw_history([1, 3, 5]))
