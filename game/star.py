import uuid
from dataclasses import dataclass
from typing import Dict, Tuple
from uuid import UUID

from colour import Color

from game.gameobject import GameObject
from game.geometry import Point


class StarID(UUID):
    @staticmethod
    def generate():
        return StarID(str(uuid.uuid4()))

class ClusterID(Point):
    pass

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