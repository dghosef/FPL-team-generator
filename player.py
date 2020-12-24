position_numbers = {1: 'G', 2: 'D', 3: 'M', 4: 'F'}


class Player():
    def __init__(self, name, position):
        self.name = name
        self.position = position

    def __hash__(self):
        return hash((self.name, self.position))

    def __eq__(self, other):
        return (self.name, self.position) == \
            (other.name, other.position)

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
