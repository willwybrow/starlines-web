import random
import uuid
from typing import Dict
from uuid import UUID

from game.geometry import Point
from game.player import Player
from game.ship import Ship, Probe
from game.star import Star, StarID, ClusterID
from gameservice.service import Service
from gameservice.universeservice import UniverseService
from persistence.sqlite import SQLite3Db


class GameService(Service):
    def __init__(self, repository: SQLite3Db):
        super().__init__(repository)
        self.universe_service = UniverseService(self.repository)

    def new_player(self, name: str):
        player = self.repository.save_new_player(Player.generate(name))
        return self.join_player_to_universe(player)

    def get_player(self, player_id: UUID):
        player = self.repository.load_player_only(player_id)
        return player

    def join_player_to_universe(self, player: Player):
        ship = Probe(uuid.uuid4(), None)
        return player if self.repository.assign_player_to_empty_cluster(player, ship) else None

    def get_cluster_stars(self, cluster_coordinate: ClusterID) -> Dict[Point, Star]:
        return self.repository.load_cluster_stars(cluster_coordinate)

    def get_star_details(self, star_id: StarID):
        return self.repository.load_ships_at_star(star_id)

    def get_player_ships(self, player: Player):
        return self.repository.load_player_ships(player)