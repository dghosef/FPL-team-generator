# https://stackoverflow.com/questions/51657000/how-to-convert-an-html-table-into-a-python-dictionary
import re
from bs4 import BeautifulSoup
from pprint import pprint
from player import Player

team_names = ["MCI", "LIV", "EVE", "TOT", "CHE", "LEE", "AVL", "SOU", "WHU",
              "WOL", "MUN", "BHA", "FUL", "LEI", "ARS", "CRY", "SHU", "BUR",
              "WBA", "NEW"]


def get_attacking_data(in_file):
    data = open(in_file, 'r').read()
    soup = BeautifulSoup(data, 'lxml')
    players = dict()
    for tr in soup.select("tr"):
        if(re.search("xG|xA", tr.__str__())):
            continue
        if re.search("ioA", tr.__str__()):
            currentStat = "assists"
        elif re.search("ioG", tr.__str__()):
            currentStat = "goals"
        else:
            continue
        stats = tr.text.strip().splitlines()
        position = stats[0].strip()
        name = stats[1].strip()
        expected = float(stats[2].strip())
        gameweek = int(stats[6].strip())
        players.setdefault(Player(name, position), dict()) \
            .setdefault(gameweek, dict()).setdefault(currentStat, 0)
        players[Player(name, position)][gameweek][currentStat] += expected
    return players


def get_cs_data(in_file):
    file = open(in_file, "r")
    data = file.read()
    soup = BeautifulSoup(data, 'lxml')
    cleansheets = dict()
    for tr in soup.select("tr"):
        if(not re.search("csTeam", tr.__str__())):
            continue

        team = tr.text.strip().splitlines()[0]
        gameweek = int(tr.text.strip().splitlines()[4])
        probability = float(tr.text.strip().splitlines()[1][:-1])
        cleansheets.setdefault(team, dict()).setdefault(gameweek, 0)
        cleansheets[team][gameweek] += probability
    return cleansheets


if __name__ == "__main__":
    pprint(get_cs_data("cs.html"))
