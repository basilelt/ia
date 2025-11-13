class Node:
    def __init__(self, state, parent=None, road_to_parent=None):
        self.state = state
        self.path_cost = 0
        self.parent = parent
        self.road_to_parent = road_to_parent

    def __lt__(self, other):
            # Chooses the first instance when comparing to another instance of Node
            # Resolves path cost tie
            return id(self) < id(other)