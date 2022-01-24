import random
from typing import Dict

from game.geometry import Point
from game.star import ClusterID, Star, StarID
from game.universe import MASS_PER_NEW_CLUSTER, CLUSTER_SIZE
from gameservice.service import Service


class UniverseService(Service):
    def __init__(self, repository):
        super().__init__(repository)
        self.repository.ensure_minimum_universe_size(UniverseService.create_new_cluster_of_stars_at)

    def new_universe(self):
        for x in range(-1 * CLUSTER_SIZE, CLUSTER_SIZE + 1):
            for y in range(-1 * CLUSTER_SIZE, CLUSTER_SIZE + 1):
                self.create_new_cluster_of_stars_at(ClusterID(x, y))
        return

    @staticmethod
    def create_new_cluster_of_stars_at(cluster_coordinate: ClusterID) -> Dict[Point, Star]:
        total_mass_to_distribute = MASS_PER_NEW_CLUSTER
        new_star_masses = []
        while total_mass_to_distribute >= 0:
            star_mass = random.randint(1, MASS_PER_NEW_CLUSTER // 2)
            new_star_masses.append(star_mass)
            total_mass_to_distribute -= star_mass
        random_points = random.sample([Point(x, y) for x in range(1, CLUSTER_SIZE) for y in range(1, CLUSTER_SIZE)], len(new_star_masses))
        stars = {random_points[i]: Star(StarID.generate(), new_star_masses[i], int(new_star_masses[i] * 1.75), 0) for i in range(len(random_points))}
        return stars