# https://stackoverflow.com/questions/51657000/how-to-convert-an-html-table-into-a-python-dictionary
import re
import os
import pickle
from bs4 import BeautifulSoup

import fpl_api
from player import Player


def get_cs_data(in_file):
    file = open(in_file, 'r')
    data = file.read()
    soup = BeautifulSoup(data, 'lxml')
    cleansheets = dict()
    for tr in soup.select('tr'):
        if(not re.search('csTeam', tr.__str__())):
            continue
        team = tr.text.strip().splitlines()[0]
        gameweek = int(tr.text.strip().splitlines()[4])
        probability = float(tr.text.strip().splitlines()[1][:-1])
        cleansheets.setdefault(team, dict()).setdefault(gameweek, 0)
        cleansheets[team][gameweek] += probability
    return cleansheets


def get_player_data(cs_file, attack_file, refresh_data=False):
    if refresh_data or not os.path.exists('./data/player_data'):
        attack_data = open(attack_file, 'r').read()
        soup = BeautifulSoup(attack_data, 'lxml')
        cs_data = get_cs_data(cs_file)
        players = dict()
        for tr in soup.select('tr'):
            if(re.search('xG|xA', tr.__str__())):
                continue
            if re.search('ioA', tr.__str__()):
                currentStat = 'assists'
            elif re.search('ioG', tr.__str__()):
                currentStat = 'goals'
            else:
                continue
            team = tr.__str__().strip().splitlines()[1][17:20]
            stats = tr.text.strip().splitlines()
            position = stats[0].strip()
            name = stats[1].strip()
            expected = float(stats[2].strip())
            gameweek = int(stats[6].strip())
            players.setdefault(Player(name, position, team), dict()) \
                .setdefault(gameweek, dict()).setdefault(currentStat, 0)
            players[Player(name, position, team)][gameweek][currentStat] += \
                expected
            players[Player(name, position, team)][gameweek]['cleansheets'] = \
                cs_data[team][gameweek] / 100.0
            with open('./data/player_data', 'wb') as handle:
                pickle.dump(players, handle)
    else:
        with open('./data/player_data', 'rb') as handle:
            players = pickle.load(handle)
    return players


# Possible statuses are a, d
def calculate_points(cs_file, attack_file, gameweeks, min_mins,
                     good_status=['a'], refresh_data=False):
    player_data = get_player_data(cs_file, attack_file, refresh_data)
    history = fpl_api.get_player_history(gameweeks, refresh_data)
    for current_player in player_data:
        factor = 1
        if sum(history[current_player]['gw_history'][0]) < min_mins or \
                history[current_player]['status'] not in good_status:
            factor = 0
        for gameweek in player_data[current_player]:
            player_current_gw = player_data[current_player][gameweek]
            player_current_gw['points'] = \
                current_player.points(player_current_gw['cleansheets'],
                                      player_current_gw['assists'],
                                      player_current_gw['goals']) * factor
    return player_data, history


if __name__ == '__main__':
    should_print = True
    if should_print:
        points = calculate_points("data/cs.html", "data/attack.html", [13, 14, 15, 16], 270)
        for player in players:
            current_player_data = points[0][player]
            point_value = sum(current_player_data[i]['points'] for i in current_player_data)
            print(point_value)
