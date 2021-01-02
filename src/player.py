position_names = {'G': 1, 'D': 2, 'M': 3, 'F': 4}
# position: (cleansheets, assists, goals)
point_values = {1: (4, 3, 6),
                2: (4, 3, 6),
                3: (1, 3, 5),
                4: (0, 3, 4)}


# Player class that stores a player's name, position, and team name. Every
# EPL player as of Jan 1 2021 has a unique player object
class Player():
    def __init__(self, name, position, team):
        self.name = name
        if position in position_names:
            self.position = position_names[position]
        else:
            self.position = position
        self.team = team

    # Calculate a player's points from parameters
    def points(self, cleansheets, assists, goals, saves=0, bonus=0,
               prob_of_conceeding_2=0):
        return cleansheets * point_values[self.position][0] + assists * \
            point_values[self.position][1] + \
            goals * point_values[self.position][2] + 2 + bonus - \
            (prob_of_conceeding_2 if self.position in [1, 2] else 0) + \
            (saves / 3.0 if self.position == 1 else 0)

    def __hash__(self):
        return hash((self.name, self.position, self.team))

    def __eq__(self, other):
        print(other)
        return (self.name, self.position, self.team) == \
            (other.name, other.position, other.team)

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        return f"{self.name}({self.team})({self.position})"

    def __repr__(self):
        return f"{self.name}({self.team})({self.position})"
