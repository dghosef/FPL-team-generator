import itertools
from pick_team import goal_count_probability
from predict_points import predict_score


"""
Returns a dict of the form
{(team1 goals, team2 goals): probability of that score occuring}
and tests every score up to and including (max_goals, max_goals)
"""


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
