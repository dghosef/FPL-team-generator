# https://www.reddit.com/r/FantasyPL/comments/dg1to7/an_analysis_of_overanalysis_my_adventure_in_fpl/
import math
from fpl_api import get_team_numbers, get_past_fixtures, get_future_fixtures, \
    get_player_history


def team_strengths(cur_gw, num_gws=5, refresh_data=False, avg_scored=1.36,
                   iterations=50, num_samples=4):
    fixtures = get_past_fixtures(cur_gw, refresh_data)
    # initialize [defensive strength, offensive strength] to [1, 1]
    strengths = dict(zip(get_team_numbers().values(), [[1, 1]] * 20))
    avg_strengths = dict(zip(get_team_numbers().values(), [[0, 0]] * 20))
    while iterations + num_samples > 0:
        # keep only num_gws fixtures
        for cur_team in fixtures:
            fixtures[cur_team] = fixtures[cur_team][-1 * num_gws:]
        new_strengths = dict()
        for team_index, current_team in enumerate(strengths):
            defensive_scores = list()
            offensive_scores = list()
            for game in fixtures[current_team]:
                goals_scored = game[1]
                goals_conceeded = game[2]
                opp_d_strength = strengths[game[0]][0]
                opp_a_strength = strengths[game[0]][1]
                defensive_scores.append(goals_conceeded / avg_scored
                                        / opp_a_strength)
                offensive_scores.append(
                    goals_scored / avg_scored * opp_d_strength)
            new_strengths[current_team] = [sum(defensive_scores) / num_gws,
                                           sum(offensive_scores) / num_gws]
        strengths = new_strengths
        del new_strengths
        if iterations <= 0:
            for team in strengths:
                avg_strengths[team] = \
                    [strengths[team][0] / num_samples + avg_strengths[team][0],
                     strengths[team][1] / num_samples + avg_strengths[team][1]]
        iterations -= 1
    return avg_strengths


def predict_score(team1, team2, strengths, avg_scored=1.36):
    strength1 = strengths[team1]
    strength2 = strengths[team2]
    return avg_scored * strength1[1] * strength2[0], \
        avg_scored * strength2[1] * strength1[0]


# per 90
def team_ct(gameweeks, refresh_data=False):
    history = get_player_history(gameweeks, refresh_data)
    creativities = dict(zip(get_team_numbers().values(), [0]*20))
    threats = dict(zip(get_team_numbers().values(), [0]*20))
    for current_player in history:
        # Whenever FPL adds a new player, we have illegal data
        if history[current_player]['gw_history'] == []:
            history[current_player]['gw_history'] = [[0], [0.0], [0.0]]
            continue
        threats[current_player.team] += \
            sum(history[current_player]['gw_history'][2])
        creativities[current_player.team] += \
            sum(history[current_player]['gw_history'][1])
    for team in creativities:
        creativities[team] /= len(gameweeks)
        threats[team] /= len(gameweeks)
    return creativities, threats, history


def performance_predictions(past_gameweeks, future_gameweeks, strengths,
                            refresh_data=False, avg_scored=1.36,
                            avg_assisted=.75):
    creativities, threats, history = team_ct(past_gameweeks, refresh_data)
    future_fixtures = get_future_fixtures(future_gameweeks)
    for player in history:
        total_minutes = sum([i for i in history[player]['gw_history'][0]])
        if total_minutes == 0:
            goals = [0]
            assists = [0]
            cleansheets = [0]
            points = [0]
        else:
            total_creativity = \
                sum([i for i in history[player]['gw_history'][1]])
            total_threat = sum([i for i in history[player]['gw_history'][2]])
            creativity_per_90 = total_creativity / total_minutes * 90
            threat_per_90 = total_threat / total_minutes * 90
            percent_creativity = creativity_per_90 / creativities[player.team]
            percent_threat = threat_per_90 / threats[player.team]
            predicted_scores = \
                [predict_score(player.team, i, strengths, avg_scored)
                 for i in future_fixtures[player.team]]
            assists = list()
            goals = list()
            cleansheets = list()
            points = list()
            for score in predicted_scores:
                # poisson distribution
                cleansheets.append(math.e ** (-1 * score[1]))
                assists.append(score[0] * percent_creativity * avg_assisted)
                goals.append(score[0] * percent_threat)
                points.append(
                    player.points(cleansheets[-1], assists[-1], goals[-1]))
        history[player]['goals'] = goals
        history[player]['assists'] = assists
        history[player]['cleansheets'] = cleansheets
        history[player]['points'] = points
    return history


if __name__ == "__main__":
    from pprint import pprint
    strengths = team_strengths(16)
    pprint(performance_predictions([11, 12, 13, 14, 15, 16], [16, 17, 18], strengths))
