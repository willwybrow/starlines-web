import uuid
from dataclasses import dataclass
from typing import Dict, Tuple
from uuid import UUID
from pairing_functions import szudzik

from colour import Color

from game.gameobject import GameObject
from game.geometry import Point


class StarID(UUID):
    @staticmethod
    def generate():
        return StarID(str(uuid.uuid4()))

class ClusterID(Point):

    @staticmethod
    def natural_to_integer(natural: int) -> int:
        if natural < 0:
            return (-2 * natural) - 1
        return 2 * natural

    @staticmethod
    def integer_to_natural(integer: int) -> int:
        if integer < 0:
            raise ValueError("Cannot be negative")
        if integer % 2 == 0:
            return integer // 2
        return (integer + 1) // -2

    @staticmethod
    def from_id(id: int) -> 'ClusterID':
        integer_x, integer_y = szudzik.unpair(id)
        return ClusterID(ClusterID.integer_to_natural(integer_x), ClusterID.integer_to_natural(integer_y))

    @property
    def id(self):
        return szudzik.pair(ClusterID.natural_to_integer(self.x), ClusterID.natural_to_integer(self.y))



@dataclass
class Star(GameObject):
    id: StarID
    current_mass: int
    maximum_mass: int

    @property
    def colour(self) -> Color:
        return Color(hue=float(self.id.bytes[0])/255, saturation=1.0, luminance=0.9)

    @property
    def offset(self) -> Tuple[float, float]:
        return self.id.bytes[1]/2.55 - 50, self.id.bytes[2]/2.55 - 50

@dataclass
class Cluster(GameObject):
    cluster_id: ClusterID
    stars: Dict[Point, StarID]