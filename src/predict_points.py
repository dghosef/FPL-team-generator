# https://www.reddit.com/r/FantasyPL/comments/dg1to7/an_analysis_of_overanalysis_my_adventure_in_fpl/
from fpl_api import get_team_numbers, get_fixtures
import math
import itertools


def team_strengths(cur_gw, num_gws=5, refresh_data=False, avg_scored=1.36,
                   iterations=50, num_samples=1):
    fixtures = get_fixtures(cur_gw, refresh_data)
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


def goal_count_probability(expected_goals, test_goals):
    return (expected_goals ** test_goals) * (math.e ** (-1 * expected_goals)) \
        / math.factorial(test_goals)


def score_probabilities(team1, team2, strengths, avg_scored=1.36,
                        max_goals=10):
    # https://en.wikipedia.org/wiki/Poisson_distribution
    max_goals = max_goals
    predicted_score = predict_score(team1, team2, strengths, avg_scored)
    possible_scores = list(itertools.product(range(max_goals + 1),
                                             range(max_goals + 1)))
    scores_dict = dict()
    for test_score in possible_scores:
        scores_dict[test_score] = \
            goal_count_probability(predicted_score[0], test_score[0]) * \
            goal_count_probability(predicted_score[1], test_score[1])
    return scores_dict


# returns prob of team1 winning, prob of team2 winning, prob of draw
def winner_probability(team1, team2, strengths, avg_scored=1.36, max_goals=10):
    scores = \
        score_probabilities(team1, team2, strengths, avg_scored, max_goals)
    return sum(scores[i] for i in scores if i[0] > i[1]), \
        sum(scores[i] for i in scores if i[0] < i[1]), \
        sum(scores[i] for i in scores if i[0] == i[1])


if __name__ == "__main__":
    team1 = "BUR"
    team2 = "SOU"
    for i in range(200):
        strengths = team_strengths(16, iterations=i, num_samples=4)
        print(predict_score(team1, team2, strengths))
