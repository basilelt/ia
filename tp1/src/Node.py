class Node:
    def __init__(self, state):
        self.state = state
        self.path_cost = 0
        self.parent = None
        self.road_to_parent = None
