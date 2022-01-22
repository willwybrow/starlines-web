import random
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Dict

from game.gameobject import GameObject
from game.geometry import Point
from game.star import Star, Cluster, ClusterID, StarID

CLUSTER_SIZE = 5
MASS_PER_NEW_CLUSTER = 20

class Dimension(Enum):
    UP = 1,
    DOWN = 2,
    LEFT = 3,
    RIGHT = 4

@dataclass
class Universe(GameObject):
    id: uuid.UUID
    all_clusters: Dict[Point, Cluster]

    @property
    def left_boundary(self):
        return min(self.all_clusters.keys(), key=lambda c: c.x).x

    @property
    def right_boundary(self):
        return max(self.all_clusters.keys(), key=lambda c: c.x).x

    @property
    def bottom_boundary(self):
        return min(self.all_clusters.keys(), key=lambda c: c.y).y

    @property
    def top_boundary(self):
        return max(self.all_clusters.keys(), key=lambda c: c.y).y

    @property
    def x_values(self):
        return range(self.left_boundary, self.right_boundary + 1)

    @property
    def y_values(self):
        return range(self.bottom_boundary, self.top_boundary + 1)

    def extend_universe(self):
        extend_universe_in = random.choice(list(Dimension))
        if extend_universe_in == Dimension.UP:
            new_y = self.top_boundary + 1
            return [self.create_new_cluster_at(Point(x, new_y)) for x in self.x_values]
        if extend_universe_in == Dimension.DOWN:
            new_y = self.bottom_boundary - 1
            return [self.create_new_cluster_at(Point(x, new_y)) for x in self.x_values]
        if extend_universe_in == Dimension.LEFT:
            new_x = self.left_boundary - 1
            return [self.create_new_cluster_at(Point(new_x, y)) for y in self.y_values]
        if extend_universe_in == Dimension.RIGHT:
            new_x = self.right_boundary + 1
            return [self.create_new_cluster_at(Point(new_x, y)) for y in self.y_values]
