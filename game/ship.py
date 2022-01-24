from dataclasses import dataclass
from typing import Union
from uuid import UUID

from game.gameobject import GameObject
from game.star import Star, StarID


@dataclass
class Ship(GameObject):
    id: UUID
    orbiting_star_id: Union[StarID, None]
    model = None


@dataclass
class Probe(Ship):
    model = "probe"

@dataclass
class Harvester(Ship):
    model = "harvester"

@dataclass
class Stabiliser(Ship):
    model = "stabiliser"