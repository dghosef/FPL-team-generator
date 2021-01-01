# thanks to https://github.com/joconnor-ml/forecasting-fantasy-football
from base_lp_model import base_lp_model
from player import Player
from predict_points import performance_predictions, team_strengths


"""
Returns a list of players, a list of their respective teams, a list of their
respective cumulative predicted points found by passing past_gameweeks,
future_gameweeks, strengths, refresh_data, avg_scored, and avg_assisted
into performance_predictions, a list of their respective positions, and a list
of their respective prices in that order. Discard players who have played less
minutes than min_mins and whose statuses aren't in good_status
"""


def get_data(past_gameweeks, future_gameweeks, strengths, min_mins,
             refresh_data=False, avg_scored=1.36, avg_assisted=.75,
             good_status=['a']):
    player_data = performance_predictions(past_gameweeks, future_gameweeks,
                                          strengths, refresh_data, avg_scored,
                                          avg_assisted)
    players = list()
    teams = list()
    points = list()
    positions = list()
    prices = list()
    for player in player_data:
        if sum(player_data[player]['gw_history'][0]) < min_mins or \
                player_data[player]['status'] not in good_status:
            continue
        players.append(player)
        teams.append(player.team)
        points.append(
            sum(player_data[player]['points']))
        prices.append(player_data[player]['price'])
        positions.append(player.position)
    return players, teams, points, positions, prices


"""
Uses past_gameweeks to determine player strengths and future_gameweeks to
predict future points. Discards players who have played less than min_mins
in past_gameweeks and whose statuses aren't marked as 'a'. Runs PuLP linear
programming solver to maximize points with fpl team selection constraints and
returns a list of players, the starting decisions for each player,
substitution decisions for each player, and captain decisions for each player.
Does not select a backup gk

Selected team will cost at most budget and each player will have played at
least min_mins in past_gameweeks. sub_factors is a list containing the
probabilities sub1, sub2, and sub3 will play respectively, num_captains is
the expected number of players who the captaincy will be rotated between,
if refresh_data is True, all data from the fpl api will be redownloaded.
"""


def lp_team_select(past_gameweeks, future_gameweeks, budget=100, min_mins=4*60,
                   refresh_data=False, sub_factors=[0.3, 0.2, 0.1],
                   num_captains=1):
    strengths = \
        team_strengths(future_gameweeks[0], len(past_gameweeks), refresh_data)
    players, teams, points, positions, prices =  \
        get_data(past_gameweeks, future_gameweeks, strengths, min_mins,
                 refresh_data=refresh_data)
    num_players = len(players)
    model, starting_decisions, sub_1_decision, sub_2_decision, \
        sub_3_decision, captain_decisions = \
        base_lp_model(players, teams, points, positions, prices,
                      num_captains, sub_factors)
    # max cost constraint
    model += sum((starting_decisions[i] + sub_1_decision[i] + sub_2_decision[i]
                  + sub_3_decision[i]) * prices[i]
                 for i in range(num_players)) <= budget  # total cost
    model.solve()
    print("Total expected score = {}".format(model.objective.value()))
    return players, starting_decisions, sub_1_decision, sub_2_decision, \
        sub_3_decision, captain_decisions


"""
Given a current_team which is a list of 14 Player objects(exclude backup gk),
a list of their current selling costs, a maximum number of transfers, and the
amount of money in the bank(itb) suggests which players to remove.  Arguments
are largely the same as lp_team_select except itb replaces budget.
"""


def lp_transfer(current_team, selling_prices, transfer_count, past_gameweeks,
                future_gameweeks, itb=0, min_mins=5*60, refresh_data=False,
                sub_factors=[0.3, 0.2, 0.1], num_captains=1):
    budget = sum(selling_prices) + itb
    strengths = \
        team_strengths(future_gameweeks[0], len(past_gameweeks), refresh_data)
    players, teams, points, positions, prices =  \
        get_data(past_gameweeks, future_gameweeks, strengths, min_mins)
    num_players = len(players)
    # If a player in current_team but not in our points predictions because of
    # a lack of minutes/injury, add him with 0 points
    for i in range(len(current_team)):
        if not current_team[i] in players:
            players.append(current_team[i])
            prices.append(selling_prices[i])
            points.append(0)
            teams.append(current_team[i].team)
            positions.append(current_team[i].position)
    # Change prices for players already in current_team because of the way
    # FPL handles players' selling prices after price rises.
    for i in range(num_players):
        for j in range(len(current_team)):
            if players[i] == current_team[j]:
                prices[i] = selling_prices[j]
    model, starting_decisions, sub_1_decision, sub_2_decision, \
        sub_3_decision, captain_decisions = \
        base_lp_model(players, teams, points, positions, prices,
                      num_captains, sub_factors)
    # max cost constraint
    model += sum((starting_decisions[i] + sub_1_decision[i] + sub_2_decision[i]
                  + sub_3_decision[i]) * prices[i]
                 for i in range(num_players)) <= budget  # total cost
    # max transfers constraints
    model += sum(starting_decisions[i] + sub_1_decision[i] +
                 sub_2_decision[i] + sub_3_decision[i]
                 for i in range(num_players) if players[i] in current_team) \
        >= len(current_team) - transfer_count
    model.solve()
    print("Total expected score = {}".format(model.objective.value()))
    return players, starting_decisions, sub_1_decision, sub_2_decision, \
        sub_3_decision, captain_decisions


def print_xi(xi):
    team = {1: list(), 2: list(), 3: list(), 4: list()}
    for player in xi:
        team[player.position].append(player)
    for position in team:
        print(team[position])


if __name__ == "__main__":
    current_team = [Player("Martínez", 1, "AVL"),
                    Player("Taylor", 2, "BUR"),
                    Player("Chilwell", 2, "CHE"),
                    Player("Cancelo", 2, "MCI"),
                    Player("Walker-Peters", 2, "SOU"),
                    Player("Kilman", 2, "WOL"),
                    Player("Grealish", 3, "AVL"),
                    Player("Salah", 3, "LIV"),
                    Player("Fernandes", 3, "MUN"),
                    Player("Reed", 3, "FUL"),
                    Player("Son", 3, "TOT"),
                    Player("Bamford", 4, "LEE"),
                    Player("Adams", 4, "SOU"),
                    Player("Kane", 4, "TOT")]
    prices = [4.9, 4.5, 5.8, 5.5, 4.7, 4.1, 7.6, 12.4, 11.0, 4.4, 9.3,
              6.3, 6.0, 10.7]

    players, starting, sub1, sub2, sub3, captain = \
        lp_transfer(current_team, prices, 2, [11, 12, 13, 14, 15],
                    range(16, 26), num_captains=2, itb=.2)
    print(list(players[i] for i in range(len(players)) if
          starting[i].value() != 0))
    for sub in (sub1, sub2, sub3):
        print(list(players[i] for i in range(len(players))
                   if sub[i].value() != 0))
    print(list(players[i] for i in range(len(players)) if
          captain[i].value() != 0))

    players, starting, sub1, sub2, sub3, captain = \
        lp_team_select(range(7, 17), range(17, 27), num_captains=2,
                       min_mins=760, budget=96, refresh_data=False)
    print_xi([players[i] for i in range(len(players)) if
              starting[i].value() != 0])
    for sub in (sub1, sub2, sub3):
        print(list(players[i] for i in range(len(players))
                   if sub[i].value() != 0))
    print(list(players[i] for i in range(len(players)) if
          captain[i].value() != 0))
