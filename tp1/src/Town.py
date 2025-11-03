class Town:

    def __init__(self, dept_id, name, latitude, longitude):
        self.dept_id = dept_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.neighbours = dict()
