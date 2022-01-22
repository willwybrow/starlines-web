import random
import uuid
from typing import Dict
from uuid import UUID

from game.geometry import Point
from game.player import Player
from game.ship import Ship
from game.star import Star, StarID
from gameservice.service import Service
from gameservice.universeservice import UniverseService
from persistence.sqlite import SQLite3Db


class GameService(Service):
    def __init__(self, repository: SQLite3Db):
        super().__init__(repository)
        self.universe_service = UniverseService(self.repository)

    def new_player(self, universe_id: UUID, name: str):
        player_id = uuid.uuid4()
        player = self.repository.save_new_player(player_id, name)
        return self.join_player_to_universe(player, universe_id)

    def join_player_to_universe(self, player: Player, universe_id: UUID):
        universe = self.universe_service.get_universe(universe_id)
        starting_cluster_point = random.choice(self.repository.find_empty_generated_clusters(universe_id))
        stars = self.repository.load_cluster_stars(universe_id, starting_cluster_point)
        best_star = max(stars.values(), key=lambda s: s.current_mass)
        ship = Ship(uuid.uuid4(), best_star)
        self.repository.save_new_ship(player, ship, best_star)
        return best_star

    def get_cluster_stars(self, universe_id: UUID, cluster_coordinate: Point) -> Dict[Point, Star]:
        return self.repository.load_cluster_stars(universe_id, cluster_coordinate)

    def get_star_details(self, star_id: StarID):
        return self.repository.load_ships_at_star(star_id)