import uuid
from dataclasses import dataclass
from uuid import UUID

from game.gameobject import GameObject
from game.objectid import ID


class PlayerID(ID):
    @staticmethod
    def generate() -> 'PlayerID':
        return PlayerID(str(uuid.uuid4()))

@dataclass
class Player(GameObject):
    id: PlayerID
    name: str

    @staticmethod
    def generate(name: str) -> 'Player':
        return Player(PlayerID.generate(), name)


