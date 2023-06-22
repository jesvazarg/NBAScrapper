class Season:
    def __init__(self, id: int, name: str):
        self.id = int(id)
        self.name = str(name)

    def __str__(self):
        return "Season -> id: " + str(self.id) + ", name: " + self.name
