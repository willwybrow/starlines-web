from dataclasses import dataclass
from uuid import UUID

from game.gameobject import GameObject


@dataclass
class Player(GameObject):
    id: UUID
    name: str


