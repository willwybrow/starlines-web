import random
import uuid
from typing import Generator

from game.geometry import Point
from game.star import Cluster, ClusterID, Star, StarID
from game.universe import Universe, MASS_PER_NEW_CLUSTER, CLUSTER_SIZE
from gameservice.service import Service


class UniverseService(Service):
    def __init__(self, repository):
        super().__init__(repository)

    def get_universe(self, universe_id: uuid.UUID) -> Universe:
        return self.repository.load_universe(universe_id)


    def new_universe(self):
        universe_id = uuid.uuid4()
        for x in range(-1 * CLUSTER_SIZE, CLUSTER_SIZE + 1):
            for y in range(-1 * CLUSTER_SIZE, CLUSTER_SIZE + 1):
                self.create_new_cluster_of_stars_at(universe_id, Point(x, y))
        return Universe(universe_id, dict())

    def create_new_cluster_of_stars_at(self, universe_id: uuid.UUID, cluster_coordinate: Point):
        total_mass_to_distribute = MASS_PER_NEW_CLUSTER
        new_star_masses = []
        while total_mass_to_distribute >= 0:
            star_mass = random.randint(1, MASS_PER_NEW_CLUSTER // 2)
            new_star_masses.append(star_mass)
            total_mass_to_distribute -= star_mass
        random_points = random.sample([Point(x, y) for x in range(1, CLUSTER_SIZE) for y in range(1, CLUSTER_SIZE)], len(new_star_masses))
        stars = {random_points[i]: Star(StarID.generate(), new_star_masses[i], int(new_star_masses[i] * 1.75)) for i in range(len(random_points))}
        self.repository.save_new_stars(universe_id, cluster_coordinate, stars)
        return stars


    def free_cluster_points(self, universe) -> Generator[Point, None, None]:
        for x in universe.x_values:
            for y in universe.y_values:
                coordinate = Point(x, y)
                if coordinate in universe.all_clusters:
                    if not any(len(star.orbiting_ships) > 0 for star in universe.all_clusters[coordinate].stars.values()):
                        yield coordinate

    def inhabit_new_cluster(self, universe_id, player_id):
        pass