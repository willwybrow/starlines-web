from dataclasses import dataclass
from uuid import UUID

from game.gameobject import GameObject
from game.star import Star


@dataclass
class Ship(GameObject):
    id: UUID
    model = None


@dataclass
class Probe(Ship):
    model = "probe"