class Activity:
    max_level = 100

    def set_max_level(max):
        max_level = max
    def __init__(self, name="", level=-1):
        self.level = level
        self.name = name

    def all_activity_for_level(self, level):
        activities = set()
        for leaf in self.leafs:
            if leaf.level == level:
                activities.add(leaf)
        return activities
