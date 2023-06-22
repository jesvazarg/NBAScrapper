class GameVisitorPlayer:
    def __init__(self, game_id: str, player_id: str, mp: int):
        self.id = self.get_id(game_id, player_id)
        self.game_id = str(game_id) if game_id is not None else None
        self.player_id = str(player_id) if player_id is not None else None
        self.mp = int(mp)

    def __str__(self):
        return "GameVisitorPlayer -> id: " + self.id + ", game_id: " + str(self.game_id) + \
            ", player_id: " + self.player_id + ", mp: " + str(self.mp // 60) + ":" + str(self.mp % 60)

    @classmethod
    def get_id(cls, game_id: str, player_id: str) -> str:
        """Create id from a game_visitor_player"""
        return game_id + player_id
