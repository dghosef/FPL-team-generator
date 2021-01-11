# thanks to https://github.com/joconnor-ml/forecasting-fantasy-football
import math
import re

from base_lp_model import base_lp_model
from player import Player
from predict_points import performance_predictions, team_strengths
from fpl_api import get_future_fixtures, get_team_numbers


"""
Given a predicted goal count(expected_goals), returns the probability that
test_goals goals will be scored using the Poisson Distribution formula
"""


def goal_count_probability(expected_goals, test_goals):
    return (expected_goals ** test_goals) * (math.e ** (-1 * expected_goals)) \
        / math.factorial(test_goals)


"""
Returns a list of players, a list of their respective teams, a list of their
respective cumulative predicted points found by passing past_gameweeks,
future_gameweeks, strengths, refresh_data, avg_scored, and avg_assisted
into performance_predictions, a list of their respective positions, and a list
of their respective prices in that order. Discard players who have played less
minutes than min_mins in the past num_gws gameweeks and whose statuses aren't
in good_status.
"""


def get_data(past_gameweeks, future_gameweeks, strengths, min_mins, num_gws,
             refresh_data=False, avg_scored=1.36, avg_assisted=.75,
             good_status=['a'], hivemind=False):
    player_data = performance_predictions(past_gameweeks, future_gameweeks,
                                          strengths, refresh_data, avg_scored,
                                          avg_assisted)
    future_fixtures = get_future_fixtures([future_gameweeks[0]])
    bgw = [i for i in get_team_numbers().values()
           if i not in future_fixtures]
    dgw = [i for i in future_fixtures if len(future_fixtures[i]) == 2]
    players = list()
    teams = list()
    points = list()
    positions = list()
    prices = list()
    next_week = list()
    for player in player_data:
        if sum(player_data[player]['gw_history'][0][-num_gws:]) < min_mins:
            player_data[player]['points'] = [0] * len(future_gameweeks)
        elif player_data[player]['status'] not in good_status:
            news = player_data[player]['news']
            if re.search('75%', news):
                player_data[player]['points'][0] *= .75
            elif re.search('50%', news):
                player_data[player]['points'][0] *= .5
                player_data[player]['points'][1] *= .75
            elif re.search('25%', news):
                player_data[player]['points'][0] *= .25
                player_data[player]['points'][1] *= .5
                player_data[player]['points'][2] *= .75
            elif re.search('Suspended', news):
                player_data[player]['points'][0] = 0
                player_data[player]['points'][1] *= 0.5
            else:
                player_data[player]['points'] = [0] * len(future_gameweeks)
        players.append(player)
        teams.append(player.team)
        if hivemind:
            points.append(player_data[player]['selected_by'])
        else:
            points.append(
                sum(player_data[player]['points']))
        prices.append(player_data[player]['price'])
        positions.append(player.position)
        if player.team not in bgw:
            if player.team in dgw:
                next_week.append(player_data[player]['points'][0] +
                                 player_data[player]['points'][1])
            else:
                next_week.append(player_data[player]['points'][0])
        else:
            next_week.append(0)
    return players, teams, points, positions, prices, next_week


"""
Uses past_gameweeks to determine player strengths and future_gameweeks to
predict future points. Discards players who have played less than min_mins
in past_gameweeks and whose statuses aren't marked as 'a'. Runs PuLP linear
programming solver to maximize points with fpl team selection constraints and
returns a list of players, the starting decisions for each player,
substitution decisions for each player, and captain decisions for each player.
Does not select a backup gk

Selected team will cost at most budget and each player will have played at
least min_mins in the last num_gws gws. sub_factors is a list containing the
probabilities sub1, sub2, and sub3 will play respectively, num_captains is
the expected number of players who the captaincy will be rotated between,
if refresh_data is True, all data from the fpl api will be redownloaded.
"""


def lp_team_select(past_gameweeks, future_gameweeks, weights=None, budget=96,
                   min_mins=4*60, num_gws=4, refresh_data=False,
                   sub_factors=[0.3, 0.2, 0.1], num_captains=2,
                   hivemind=False):
    strengths = \
        team_strengths(past_gameweeks, weights, refresh_data=refresh_data)
    players, teams, points, positions, prices, next_week =  \
        get_data(past_gameweeks, future_gameweeks, strengths, min_mins,
                 num_gws, refresh_data=refresh_data, hivemind=hivemind)
    num_players = len(players)
    model, starting_decisions, sub_1_decision, sub_2_decision, \
        sub_3_decision, captain_decisions = \
        base_lp_model(players, teams, points, positions, num_captains,
                      sub_factors)
    # max cost constraint
    model += sum((starting_decisions[i] + sub_1_decision[i] + sub_2_decision[i]
                  + sub_3_decision[i]) * prices[i]
                 for i in range(num_players)) <= budget  # total cost
    model.solve()
    return players, starting_decisions, sub_1_decision, sub_2_decision, \
        sub_3_decision, captain_decisions, next_week


"""
Given a current_team which is a list of 14 Player objects(exclude backup gk),
a list of their current selling costs, a maximum number of transfer_count, and
the amount of money in the bank(itb) suggests which players to remove.
Arguments are largely the same as lp_team_select except itb replaces budget.
"""


def lp_transfer(current_team, selling_prices, transfer_count, past_gameweeks,
                future_gameweeks, weights=None, itb=0, min_mins=4*60,
                num_gws=4, refresh_data=False, sub_factors=[0.3, 0.2, 0.1],
                num_captains=1, hivemind=False):
    budget = sum(selling_prices) + itb
    strengths = \
        team_strengths(past_gameweeks, weights, refresh_data=refresh_data)
    players, teams, points, positions, prices, next_week =  \
        get_data(past_gameweeks, future_gameweeks, strengths, min_mins,
                 num_gws, hivemind=hivemind)
    num_players = len(players)
    # Change prices for players already in current_team because of the way
    # FPL handles players' selling prices after price rises.
    for i in range(num_players):
        for j in range(len(current_team)):
            if players[i] == current_team[j]:
                prices[i] = selling_prices[j]
    model, starting_decisions, sub_1_decision, sub_2_decision, \
        sub_3_decision, captain_decisions = \
        base_lp_model(players, teams, points, positions, num_captains,
                      sub_factors)
    # max cost constraint
    model += sum((starting_decisions[i] + sub_1_decision[i] + sub_2_decision[i]
                  + sub_3_decision[i]) * prices[i]
                 for i in range(num_players)) <= budget  # total cost
    # max transfer_count constraints
    model += sum(starting_decisions[i] + sub_1_decision[i] +
                 sub_2_decision[i] + sub_3_decision[i]
                 for i in range(num_players) if players[i] in current_team) \
        >= len(current_team) - transfer_count
    model.solve()
    return players, starting_decisions, sub_1_decision, sub_2_decision, \
        sub_3_decision, captain_decisions, next_week


def find_weights(size, factor, step_size):
    return [factor ** (i // step_size)
            for i in range(size // step_size * step_size + step_size)][-size:]


"""
Pick team and print it nicely.
past_gws - number of past gameweeks to consider when judging player ability
future_gws - number of gameweeks to forecast for
min_mins and num_gws - player must have played min_mins over num_gws
refresh_data - whether or not to grab data from the fpl api
sub_factors - the probability each sub comes on
num_captains - number of estimated players to share the armband
"""


def pick_team(cur_gw, past_gws=10, future_gws=10, budget=96, min_mins=240,
              num_gws=4, refresh_data=False, sub_factors=[.2, .1, .05],
              num_captains=2, weights=None, hivemind=False):
    if cur_gw <= past_gws:
        past_gws = cur_gw - 1
    if weights is None:
        weights = find_weights(past_gws, 2, 5)
    players, starting, sub1, sub2, sub3, captain, next_week = \
        lp_team_select(range(cur_gw - past_gws, cur_gw),
                       range(cur_gw, cur_gw+future_gws),
                       weights=weights, budget=budget,
                       min_mins=min_mins, num_gws=num_gws,
                       refresh_data=refresh_data, sub_factors=sub_factors,
                       num_captains=num_captains, hivemind=hivemind)
    next_week = [next_week[i] for i in range(len(players)) if
                 starting[i].value() != 0 or sub1[i].value() != 0 or
                 sub2[i].value() != 0 or sub3[i].value() != 0]
    players = [players[i] for i in range(len(players)) if
               starting[i].value() != 0 or sub1[i].value() != 0 or
               sub2[i].value() != 0 or sub3[i].value() != 0]
    print(players)
    print(next_week)

    starting_xi, subs, captains = pick_xi(players, next_week)
    print(f'gw {cur_gw} starters:')
    print_xi(starting_xi)
    print('')
    print('Subs:')
    print(subs)
    print('')
    print('Captains:')
    print(captains)


"""
Suggests transfers and prints them nicely
Team is a list of players who are in the current team
prices is a list of team's respective prices
transfer_count is the number of transfers we are allowed to make
itb is the amount left in the bank
The rest of the params are the same as pick_team
"""


def transfer(cur_gw, team, prices, transfer_count, past_gws=9, future_gws=10,
             itb=0, min_mins=240, num_gws=4, refresh_data=False,
             sub_factors=[.2, .1, .05], num_captains=2, weights=None,
             hivemind=False):
    if weights is None:
        weights = find_weights(past_gws, 2, 5)
    players, starting, sub1, sub2, sub3, captain, next_week = \
        lp_transfer(team, prices, transfer_count, range(cur_gw - past_gws,
                                                        cur_gw),
                    range(cur_gw, cur_gw+future_gws),
                    weights=weights, itb=itb,
                    min_mins=min_mins, num_gws=num_gws,
                    refresh_data=refresh_data, sub_factors=sub_factors,
                    num_captains=num_captains, hivemind=hivemind)
    starting_xi = [players[i] for i in range(len(players)) if
                   starting[i].value() != 0]
    next_week_prev_team = [next_week[i] for i in range(len(players)) if
                           players[i] in team]
    next_week = [next_week[i] for i in range(len(players)) if
                 starting[i].value() != 0 or sub1[i].value() != 0 or
                 sub2[i].value() != 0 or sub3[i].value() != 0]
    # Save a transfer if our team is going to perform worse next week
    if sum(next_week_prev_team) < sum(next_week):
        next_week = next_week_prev_team
    players = [players[i] for i in range(len(players)) if
               starting[i].value() != 0 or sub1[i].value() != 0 or
               sub2[i].value() != 0 or sub3[i].value() != 0]
    starting_xi, subs, captains = pick_xi(players, next_week)
    print(f'gw {cur_gw} starters:')
    print_xi(starting_xi)

    print('')
    print('Subs:')
    print(subs)
    print('')
    print('Captains:')
    print(captains)
    new_team = starting_xi + list(subs)
    print('\n Buy:')
    print([i for i in new_team if i not in team])
    print('\n Sell:')
    print([i for i in team if i not in new_team])


"""
Players - a list of player objects
next_week - a list of each player's respective points

Returns the optimal starting xi, the subs in order, and the captain pick
"""


def pick_xi(players, next_week):
    teams = [i.team for i in players]
    positions = [i.position for i in players]
    model, starting_decisions, sub_1_decision, sub_2_decision, \
        sub_3_decision, captain_decision = \
        base_lp_model(players, teams, next_week, positions, 1,
                      sub_factors=[0, 0, 0])
    model.solve()
    starters = [players[i] for i in range(len(players))
                if starting_decisions[i].value() != 0]
    starter_points = [next_week[i] for i in range(len(players))
                      if starting_decisions[i].value() != 0]
    # Order starters by points so we can pick captain
    starter_points, starters = zip(*sorted(zip(starter_points,
                                               starters), reverse=True))
    subs = list()
    sub_points = list()
    for sub in (sub_1_decision, sub_2_decision, sub_3_decision):
        subs += [players[i] for i in range(len(players))
                 if sub[i].value() != 0]
        sub_points += [next_week[i] for i in range(len(players))
                       if sub[i].value() != 0]
    # order the subs according to their points
    sub_points, subs = zip(*sorted(zip(sub_points, subs), reverse=True))
    captains = starters[:2]
    return starters, subs, captains


def print_xi(xi):
    team = {1: list(), 2: list(), 3: list(), 4: list()}
    for player in xi:
        team[player.position].append(player)
    for position in team:
        print(team[position])
