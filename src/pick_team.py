# https://github.com/joconnor-ml/forecasting-fantasy-football
import pulp

from calculate_points import calculate_points


def get_data(gameweeks, min_mins, refresh_data):
    min_mins = len(gameweeks) * 60
    player_data, history = calculate_points("data/cs.html", "data/attack.html",
                                            gameweeks, min_mins,
                                            refresh_data=refresh_data)
    players = list()
    teams = list()
    points = list()
    positions = list()
    prices = list()
    for player in player_data:
        players.append(player)
        teams.append(player.team)
        current_player_data = player_data[player]
        points.append(
            sum(current_player_data[i]['points'] for i in current_player_data))
        prices.append(history[player]['price'])
        positions.append(player.position)
    return players, teams, points, positions, prices


def pick_team(gameweeks, budget=100, min_mins=4*60, refresh_data=False,
              sub_factors=[0.3, 0.2, 0.1], next_gw=None,
              num_captains=1):
    players, teams, points, positions, prices =  \
        get_data(gameweeks, min_mins, refresh_data)
    model = pulp.LpProblem("Constrained value maximisaiton", pulp.LpMaximize)
    num_players = len(players)
    starting_decisions = [
        pulp.LpVariable("x{}".format(i), lowBound=0, upBound=1, cat='Integer')
        for i in range(num_players)
    ]
    captain_decisions = [
        pulp.LpVariable("y{}".format(i), lowBound=0, upBound=1, cat='Integer')
        for i in range(num_players)
    ]
    sub_1_decision = [
        pulp.LpVariable("z{}".format(i), lowBound=0, upBound=1, cat='Integer')
        for i in range(num_players)
    ]
    sub_2_decision = [
        pulp.LpVariable("2{}".format(i), lowBound=0, upBound=1, cat='Integer')
        for i in range(num_players)
    ]
    sub_3_decision = [
        pulp.LpVariable("3{}".format(i), lowBound=0, upBound=1, cat='Integer')
        for i in range(num_players)
    ]
    # objective function:
    model += sum((captain_decisions[i] * (1.0 / num_captains) +
                  starting_decisions[i] +
                  sub_1_decision[i] * sub_factors[0] +
                  sub_2_decision[i] * sub_factors[1] +
                  sub_3_decision[i] * sub_factors[2]) * points[i]
                 for i in range(num_players)), "Objective"
    # max cost
    model += sum((starting_decisions[i] + sub_1_decision[i] + sub_2_decision[i]
                  + sub_3_decision[i]) * prices[i]
                 for i in range(num_players)) <= budget  # total cost
    # 1 starting gk
    model += sum(starting_decisions[i] for i in range(num_players)
                 if positions[i] == 1) == 1
    # No GK Subs
    model += sum(sub_1_decision[i] + sub_2_decision[i] + sub_3_decision[i]
                 for i in range(num_players) if positions[i] == 1) == 0
    # 3-5 starting defenders
    model += sum(starting_decisions[i] for i in range(num_players)
                 if positions[i] == 2) >= 3
    model += sum(starting_decisions[i] for i in range(num_players)
                 if positions[i] == 2) <= 5
    # 5 total defenders
    model += sum(starting_decisions[i] + sub_1_decision[i] +
                 sub_2_decision[i] + sub_3_decision[i]
                 for i in range(num_players) if positions[i] == 2) == 5
    # 3-5 starting midfielders
    model += sum(starting_decisions[i] for i in range(num_players)
                 if positions[i] == 3) >= 3
    model += sum(starting_decisions[i] for i in range(num_players)
                 if positions[i] == 3) <= 5
    # 5 total midfielders
    model += sum(starting_decisions[i] + sub_1_decision[i] +
                 sub_2_decision[i] + sub_3_decision[i]
                 for i in range(num_players) if positions[i] == 3) == 5
    # 1-3 starting strikers
    model += sum(starting_decisions[i] for i in range(num_players)
                 if positions[i] == 4) >= 1
    model += sum(starting_decisions[i] for i in range(num_players)
                 if positions[i] == 4) <= 3
    # 5 total strikers
    model += sum(starting_decisions[i] + sub_1_decision[i] +
                 sub_2_decision[i] + sub_3_decision[i]
                 for i in range(num_players) if positions[i] == 4) == 3
    # club constraint
    for team in teams:
        model += sum(starting_decisions[i] + sub_1_decision[i] +
                     sub_2_decision[i] + sub_3_decision[i]
                     for i in range(num_players) if teams[i] == team) <= 3
    for i in range(num_players):
        # captain must also be on team
        model += (starting_decisions[i] - captain_decisions[i]) >= 0
        # subs must not be on team
        model += (starting_decisions[i] + sub_1_decision[i]) <= 1
        model += (starting_decisions[i] + sub_2_decision[i]) <= 1
        model += (starting_decisions[i] + sub_3_decision[i]) <= 1
        # subs must be unique
        model += (sub_2_decision[i] + sub_1_decision[i]) <= 1
        model += (sub_3_decision[i] + sub_2_decision[i]) <= 1
        model += (sub_1_decision[i] + sub_3_decision[i]) <= 1
    model += sum(starting_decisions) == 11
    model += sum(captain_decisions) == num_captains
    model += sum(sub_1_decision) == 1
    model += sum(sub_2_decision) == 1
    model += sum(sub_3_decision) == 1
    model.solve()
    print("Total expected score = {}".format(model.objective.value()))
    return players, starting_decisions, sub_1_decision, sub_2_decision, \
        sub_3_decision, captain_decisions


if __name__ == "__main__":
    players, starting, sub1, sub2, sub3, captain = \
        pick_team([11, 12, 13, 14, 15], num_captains=2, budget=96)
    print(list(players[i] for i in range(len(players)) if
          starting[i].value() != 0))
    for sub in (sub1, sub2, sub3):
        print(list(players[i] for i in range(len(players))
                   if sub[i].value() != 0))
    print(list(players[i] for i in range(len(players)) if
          captain[i].value() != 0))
