import uuid
from dataclasses import dataclass
from uuid import UUID

from game.gameobject import GameObject


@dataclass
class Player(GameObject):
    id: UUID
    name: str

    @staticmethod
    def generate(name: str) -> 'Player':
        return Player(uuid.uuid4(), name)


