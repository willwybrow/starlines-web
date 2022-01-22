from gameservice.gameservice import GameService


class StarService(GameService):
    def __init__(self, repository):
        super(StarService, self).__init__(repository)