position_names = {'G': 1, 'D': 2, 'M': 3, 'F': 4}
# position: (cleansheets, assists, goals)
point_values = {1: (4, 3, 6),
                2: (4, 3, 6),
                3: (1, 3, 5),
                4: (0, 3, 4)}


class Player():
    def __init__(self, name, position, team):
        self.name = name
        if position in position_names:
            self.position = position_names[position]
        else:
            self.position = position
        self.team = team

    def __hash__(self):
        return hash((self.name, self.position, self.team))

    def __eq__(self, other):
        return (self.name, self.position, self.team) == \
            (other.name, other.position, other.team)

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        return f"{self.name}({self.team})({self.position})"

    def __repr__(self):
        return f"{self.name}({self.team})({self.position})"

    def points(self, cleansheets, assists, goals):
        return cleansheets * point_values[self.position][0] + assists * \
            point_values[self.position][1] + \
            goals * point_values[self.position][2] + 2
