# https://www.reddit.com/r/FantasyPL/comments/dg1to7/an_analysis_of_overanalysis_my_adventure_in_fpl/
import math
from fpl_api import get_team_numbers, get_past_fixtures, get_future_fixtures, \
    get_player_history


"""
Given a predicted goal count(expected_goals), returns the probability that
test_goals goals will be scored using the Poisson Distribution formula
"""


def goal_count_probability(expected_goals, test_goals):
    return (expected_goals ** test_goals) * (math.e ** (-1 * expected_goals)) \
        / math.factorial(test_goals)


"""
Returns a dict in the form {team: defensive strength, attacking strength}
where lower defensive strength and higher attacking strength is good

gameweeks is a list of gameweeks to consider when calculating. Note that
gameweeks must be consecutive gameweeks. weights is a list where each element
represents the amount its respective gameweek should be weighted, refresh_data
should be set to True if we want to regrab info from the FPL api, avg_scored
is the average goals per game, iterations is the number of times to update the
weights, and num_samples is the number of iterations to average for the final
weight amount
"""


def team_strengths(gameweeks, weights=None, refresh_data=False,
                   avg_scored=1.36, iterations=50, num_samples=4):
    fixtures = get_past_fixtures(gameweeks[-1] + 1, refresh_data)
    # By default, weigh each gameweek equally
    if weights is None:
        weights = [1] * len(gameweeks)
    else:
        # Make sure weights is the right size
        weights = weights[-len(gameweeks):]
    # Start each team with [offensive strength, defensive_strength] = [1, 1]
    strengths = dict(zip(get_team_numbers().values(), [[1, 1]] * 20))
    # The dict that will be returned which will be populated by the average
    # strength after all iterations have been completed
    avg_strengths = dict(zip(get_team_numbers().values(), [[0, 0]] * 20))
    # Only keep the fixtures from the specified gameweeks
    for cur_team in fixtures:
        fixtures[cur_team] = fixtures[cur_team][-1 * len(gameweeks):]
    while iterations + num_samples > 0:
        new_strengths = dict()
        for team_index, current_team in enumerate(strengths):
            defensive_strengths = list()
            offensive_strengths = list()
            for i, game in enumerate(fixtures[current_team]):
                goals_scored = game[1]
                goals_conceeded = game[2]
                opp_d_strength = strengths[game[0]][0]
                opp_a_strength = strengths[game[0]][1]
                # calculate defensive and offensive strengths. Cap them at 3
                # to reduce influence of extreme outliers
                defensive_strengths.append(
                    min(3, goals_conceeded / avg_scored / opp_a_strength) *
                    weights[i])
                offensive_strengths.append(
                    min(3, goals_scored / avg_scored / opp_d_strength) *
                    weights[i])
            # Take the weighted average of the newly calculated score
            new_strengths[current_team] = \
                [sum(defensive_strengths) / sum(weights),
                 sum(offensive_strengths) / sum(weights)]
        strengths = new_strengths
        # Frees up memory. Without this, program slows with more iterations
        del new_strengths
        # Once initial iterations are finished, start taking average of new
        # iterations
        if iterations <= 0:
            for team in strengths:
                avg_strengths[team] = \
                    [strengths[team][0] / num_samples + avg_strengths[team][0],
                     strengths[team][1] / num_samples + avg_strengths[team][1]]
        iterations -= 1
    return avg_strengths


# Predicts the score between team2 and team2 based on strengths
def predict_score(team1, team2, strengths, avg_scored=1.36):
    strength1 = strengths[team1]
    strength2 = strengths[team2]
    return avg_scored * strength1[1] * strength2[0], \
        avg_scored * strength2[1] * strength1[0]


# Returns the team's total creativity/game, threat/game, and
# get_player_history over gameweeks
def team_ct(gameweeks, refresh_data=False):
    history = get_player_history(gameweeks, refresh_data)
    creativities = dict(zip(get_team_numbers().values(), [0]*20))
    threats = dict(zip(get_team_numbers().values(), [0]*20))
    for current_player in history:
        # If any player has no history, give him 0 mins/creativity/threat
        # This only really applies to players FPL Towers introduce mid-season
        if history[current_player]['gw_history'] == []:
            history[current_player]['gw_history'] = [[0], [0.0], [0.0]]
            continue
        threats[current_player.team] += \
            sum(history[current_player]['gw_history'][2])
        creativities[current_player.team] += \
            sum(history[current_player]['gw_history'][1])
    # Find average creativity and threat per game
    for team in creativities:
        creativities[team] /= len(gameweeks)
        threats[team] /= len(gameweeks)
    return creativities, threats, history


# Predict save count in each of future_fixtures
def predict_saves(strengths, past_fixtures, future_fixtures, past_saves,
                  minutes, team):
    num_games = len(past_fixtures[team])
    # saves / opponent attacking strength
    save_rate = 0
    for index, saves in enumerate(past_saves[:-1]):
        if minutes[index] == 0:
            continue
        # opponent attacking strength
        strength = strengths[past_fixtures[team][index + num_games -
                                                 len(past_saves)][0]][1]
        save_rate += saves / strength / num_games * minutes[index] / 90
    return [save_rate * strengths[i][1] for i in future_fixtures[team]]


"""
Using performances from past_gameweeks and strengths in strengths, predicts
each player's future points in each of their fixtures in future_gameweeks

avg_assisted is the average number of goals that have an assist in the leadup
refresh_data indicates whether to used previously saved data or to re-download
from the FPL api
avg_scored is the average goals per game
"""


def performance_predictions(past_gameweeks, future_gameweeks, strengths,
                            refresh_data=False, avg_scored=1.36,
                            avg_assisted=.75):
    creativities, threats, history = team_ct(past_gameweeks, refresh_data)
    future_fixtures = get_future_fixtures(future_gameweeks, refresh_data)
    past_fixtures = get_past_fixtures(future_gameweeks[0])
    for player in history:
        total_minutes = sum([i for i in history[player]['gw_history'][0]])
        # To avoid divide by 0 errors
        if total_minutes == 0:
            goals = [0] * len(future_gameweeks)
            assists = [0] * len(future_gameweeks)
            cleansheets = [0] * len(future_gameweeks)
            conceed_2 = [0] * len(future_gameweeks)
            points = [0] * len(future_gameweeks)
            saves = [0] * len(future_gameweeks)
        else:
            total_creativity = \
                sum([i for i in history[player]['gw_history'][1]])
            total_threat = sum([i for i in history[player]['gw_history'][2]])
            creativity_per_90 = total_creativity / total_minutes * 90
            threat_per_90 = total_threat / total_minutes * 90
            # creativity of player compared to creativity of team
            creativity_influence = \
                creativity_per_90 / creativities[player.team]
            threat_influence = threat_per_90 / threats[player.team]
            if player.team not in future_fixtures:
                future_fixtures[player.team] = []
            predicted_scores = \
                [predict_score(player.team, i, strengths, avg_scored)
                 for i in future_fixtures[player.team]]
            saves = predict_saves(strengths, past_fixtures, future_fixtures,
                                  history[player]['gw_history'][3],
                                  history[player]['gw_history'][0],
                                  player.team)
            assists = list()
            goals = list()
            cleansheets = list()
            conceed_2 = list()
            points = list()
            for index, score in enumerate(predicted_scores):
                cleansheets.append(goal_count_probability(score[1], 0))
                conceed_2.append(sum([goal_count_probability(score[1], i)
                                      for i in range(2, 7)]))
                assists.append(score[0] * creativity_influence * avg_assisted)
                goals.append(score[0] * threat_influence)
                points.append(
                    player.points(cleansheets[-1], assists[-1], goals[-1],
                                  saves[index], conceed_2[-1]))
        history[player]['goals'] = goals
        history[player]['assists'] = assists
        history[player]['cleansheets'] = cleansheets
        history[player]['saves'] = saves
        history[player]['points'] = points
    return history


if __name__ == "__main__":
    strengths = team_strengths([11, 12, 13, 14, 15])
    past_fixtures = get_past_fixtures(15)
    future_fixtures = get_future_fixtures(range(19, 30))
    past_saves = [10] * 14
