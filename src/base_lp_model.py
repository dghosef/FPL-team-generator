# https://github.com/joconnor-ml/forecasting-fantasy-football
import pulp


"""
Returns a PuLP model containing the FPL objective function and starting xi,
position count, team count, captaincy count, and sub count constraints. Also
returns an unsolved starting xi decisions list, substitute 1 decisions list,
substitute 2 decisions list, substitute 3 decisions list, and captaincy
decisions list. Model does not include the cost constraint.

Takes in lists of players, their respective teams, their respective predicted
points, their respective positions, their respective prices, the number of
captains, and a tuple/list of size 3 in form [s1, s2, s3], where s1, s2, and
s3 are the probabilities that the first sub, second sub, and third sub will
play respectively.
"""


def base_lp_model(players, teams, points, positions, prices, num_captains,
                  sub_factors):
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
    # No more than 3 players from each club
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
    model += sum(starting_decisions) == 11  # 11 starters
    model += sum(captain_decisions) == num_captains  # num_captains captains
    # 3 subs
    model += sum(sub_1_decision) == 1
    model += sum(sub_2_decision) == 1
    model += sum(sub_3_decision) == 1
    return model, starting_decisions, sub_1_decision, sub_2_decision, \
        sub_3_decision, captain_decisions
