import random
import sqlite3
import uuid
from sqlite3 import Connection
from typing import List, Dict, Callable
from uuid import UUID

from game.geometry import Point
from game.player import Player
from game.ship import Ship
from game.star import Star, Cluster, ClusterID, StarID
from game.universe import Universe, Dimension


class SQLite3Db:
    def __init__(self):
        self.connection = sqlite3.connect('starlines.db')
        self.connection.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        with self.connection as con:
            # cursor.execute(''' CREATE TABLE IF NOT EXISTS universe(id VARCHAR(36), PRIMARY KEY (id)) ''')
            con.execute(''' CREATE TABLE IF NOT EXISTS star(id VARCHAR(36), current_mass INTEGER, maximum_mass INTEGER, PRIMARY KEY (id)) ''')
            # cursor.execute(''' CREATE TABLE IF NOT EXISTS star_in_cluster(universe_id VARCHAR(36), cluster_in_universe_x INTEGER, cluster_in_universe_y INTEGER, star_in_cluster_x INTEGER, star_in_cluster_y INTEGER, star_id VARCHAR(36), PRIMARY KEY(universe_id, cluster_in_universe_x, cluster_in_universe_y, star_in_cluster_x, star_in_cluster_y), FOREIGN KEY (cluster_id) REFERENCES cluster(id), FOREIGN KEY (star_id) REFERENCES star(id)) ''')
            con.execute(''' CREATE TABLE IF NOT EXISTS star_in_cluster(cluster_in_universe_x INTEGER, cluster_in_universe_y INTEGER, star_in_cluster_x INTEGER, star_in_cluster_y INTEGER, star_id VARCHAR(36), PRIMARY KEY(cluster_in_universe_x, cluster_in_universe_y, star_in_cluster_x, star_in_cluster_y), FOREIGN KEY (star_id) REFERENCES star(id)) ''')
            con.execute(''' CREATE TABLE IF NOT EXISTS player (id VARCHAR(36), name TEXT, PRIMARY KEY (id)) ''')
            con.execute(''' CREATE TABLE IF NOT EXISTS player_ship(id VARCHAR(36), ship_type VARCHAR(10), player_id VARCHAR(36), orbiting_star_id VARCHAR(36), PRIMARY KEY(id), FOREIGN KEY (player_id) REFERENCES player(id), FOREIGN KEY (orbiting_star_id) REFERENCES star(id)) ''')

    def load_player_only(self, player_id: UUID):
        with self.connection as con:
            row = con.execute(''' SELECT id, name FROM player WHERE id = ? LIMIT 1 ''', [str(player_id)]).fetchone()
            return Player(UUID(row[0]), row[1])

    def load_player_ships(self, player_id: UUID):
        with self.connection as con:
            row = con.execute(''' SELECT  FROM player_ships WHERE player_id = ? LIMIT 1 ''', [str(player_id)]).fetchone()
            return Player(UUID(row[0]), row[1])

    def save_new_player(self, player_id: UUID, name: str):
        with self.connection as con:
            success = con.execute(''' INSERT INTO player (id, name) VALUES (?, ?) ''', [str(player_id), name]).rowcount == 1
            return success

    def load_universe(self) -> Dict[ClusterID, Cluster]:
        with self.connection as con:
            clusters = {}
            for row in con.execute(''' SELECT cluster_in_universe_x, cluster_in_universe_y, star_in_cluster_x, star_in_cluster_y, star_id FROM star_in_cluster ''', []).fetchall():
                cluster_point = ClusterID(row[0], row[1])
                if cluster_point not in clusters:
                    clusters[cluster_point] = Cluster(cluster_point, dict())
                star_point = Point(row[2], row[3])
                clusters[cluster_point].stars[star_point] = StarID(row[4])

            return clusters

    def deep_load_cluster(self):
        with self.connection as con:
            ''' SELECT
                star_in_cluster.star_in_cluster_x,
                star_in_cluster.star_in_cluster_y,
                star.id,
                star.current_mass,
                star.maximum_mass,
                IFNULL(player_ship_count.ship_count, 0)
                FROM star_in_cluster LEFT JOIN star ON (star_in_cluster.star_id = star.id)
                LEFT JOIN
                (SELECT player_ship.orbiting_star_id, COUNT(1) as ship_count FROM player_ship GROUP BY player_ship.orbiting_star_id) AS player_ship_count ON player_ship_count.orbiting_star_id = star_in_cluster.star_id
                WHERE star_in_cluster.cluster_in_universe_x = ?
                AND star_in_cluster.cluster_in_universe_y = ? '''
        pass

    def load_cluster_only(self, cluster_coordinate: ClusterID) -> Cluster:
        with self.connection as con:
            stars = {}

            for row in con.execute(''' SELECT star_in_cluster_x, star_in_cluster_y, star_id FROM star_in_cluster WHERE cluster_in_universe_x = ? AND cluster_in_universe_y = ? ''', [cluster_coordinate.x, cluster_coordinate.y]).fetchall():
                star_point = Point(row[0], row[1])
                stars[star_point] = StarID(row[2])

            return Cluster(cluster_coordinate, stars)

    def load_cluster_stars(self, cluster_coordinate: ClusterID) -> Dict[Point, Star]:
        with self.connection as con:
            return self.load_cluster_stars_query(con, cluster_coordinate)

    @staticmethod
    def load_cluster_stars_query(con: Connection, cluster_coordinate: ClusterID) -> Dict[Point, Star]:
        stars = {}
        for row in con.execute(''' SELECT
                star_in_cluster.star_in_cluster_x,
                star_in_cluster.star_in_cluster_y,
                star.id,
                star.current_mass,
                star.maximum_mass,
                IFNULL(player_ship_count.ship_count, 0)
                FROM star_in_cluster LEFT JOIN star ON (star_in_cluster.star_id = star.id)
                LEFT JOIN
                (SELECT player_ship.orbiting_star_id, COUNT(1) as ship_count FROM player_ship GROUP BY player_ship.orbiting_star_id) AS player_ship_count ON player_ship_count.orbiting_star_id = star_in_cluster.star_id
                WHERE star_in_cluster.cluster_in_universe_x = ?
                AND star_in_cluster.cluster_in_universe_y = ? ''', [cluster_coordinate.x, cluster_coordinate.y]).fetchall():
            star_point = Point(row[0], row[1])
            stars[star_point] = Star(StarID(row[2]), row[3], row[4])
        return stars

    def load_ships_at_star(self, star_id: StarID):
        with self.connection as con:
            result = con.execute(''' SELECT player_id, COUNT(1) as ship_count FROM player_ship WHERE orbiting_star_id = ? GROUP BY player_ship.player_id ''', [str(star_id)])
            return {UUID(row[0]): row[1] for row in result.fetchall()}


    def save_new_star(self, star: Star) -> bool:
        with self.connection as con:
            success = con.execute(''' INSERT INTO star (id, current_mass, maximum_mass) VALUES (?, ?, ?)''', [str(star.id), star.current_mass, star.maximum_mass]).rowcount > 0
            return success


    @staticmethod
    def save_new_stars_query(con: Connection, cluster_coordinate: ClusterID, star_map: Dict[Point, Star]):
        success = con.executemany(''' INSERT INTO star (id, current_mass, maximum_mass) VALUES (?, ?, ?)''', [(str(star.id), star.current_mass, star.maximum_mass) for star in star_map.values()]).rowcount > 0
        success = success & con.executemany(''' INSERT INTO star_in_cluster (cluster_in_universe_x, cluster_in_universe_y, star_in_cluster_x, star_in_cluster_y, star_id) VALUES (?, ?, ?, ?, ?, ?)''', [(cluster_coordinate.x, cluster_coordinate.y, coordinate.x, coordinate.y, str(star.id)) for coordinate, star in star_map.items()]).rowcount > 0
        return success

    def save_new_stars(self, cluster_coordinate: ClusterID, star_map: Dict[Point, Star]):
        with self.connection as con:
            success = self.save_new_stars_query(con, cluster_coordinate, star_map)
            return success

    def save_new_ship(self, player: Player, ship: Ship, star: Star):
        with self.connection as con:
            success = SQLite3Db.save_new_ship_query(con, player, ship, star).rowcount == 1
            return success

    @staticmethod
    def save_new_ship_query(con: Connection, player: Player, ship: Ship, orbiting_star: Star):
        return con.execute(''' INSERT INTO player_ship (id, ship_type, player_id, orbiting_star_id) VALUES (?, ?, ?, ?)''', [str(ship.id), ship.model, str(player.id), str(orbiting_star.id)])


    def assign_player_to_empty_cluster(self, player: Player, ship_to_place: Ship, star_picking_algorithm = lambda s: max(s, key=lambda x: s.current_mass)):
        with self.connection as con:
            empty_cluster = random.choice(self.empty_generated_clusters_query(con))
            star_map = SQLite3Db.load_cluster_stars_query(con, empty_cluster)
            best_star = star_picking_algorithm(star_map.values())
            SQLite3Db.save_new_ship_query(con, player, ship_to_place, best_star)


    def ensure_minimum_universe_size(self, cluster_creator: Callable[[ClusterID], Dict[Point, Star]]):
        with self.connection as con:
            if SQLite3Db.universe_size_query(con) == 0:
                for x,y in range(-5, 5), range(-5, 5):
                    cluster_id = ClusterID(x,y)
                    star_map = cluster_creator(cluster_id)
                    SQLite3Db.save_new_stars_query(con, cluster_id, star_map)

    @staticmethod
    def universe_size_query(con: Connection):
        return con.execute(''' SELECT COUNT(DISTINCT cluster_in_universe_x, cluster_in_universe_y) AS cluster_count FROM star_in_cluster; ''').fetchone()['cluster_count']

    @staticmethod
    def not_generated_clusters_query(con: Connection, limits: Dict[Dimension, int]):
        con.execute(''' SELECT  ''')

    @staticmethod
    def cluster_limit_query(con: Connection):
        row = con.execute(''' SELECT MIN(cluster_in_universe_x) AS left, MAX(cluster_in_universe_x) AS right, MIN(cluster_in_universe_y) AS bottom, MAX(cluster_in_universe_y) AS top FROM star_in_cluster ''').fetchone()
        return {Dimension.UP: row["top"], Dimension.LEFT: row["left"], Dimension.DOWN: row["bottom"], Dimension.RIGHT: row["right"]}

    @staticmethod
    def empty_generated_clusters_query(con) -> List[ClusterID]:
        return [ClusterID(row[0], row[1]) for row in con.execute(''' SELECT
    star_in_cluster.cluster_in_universe_x,
    star_in_cluster.cluster_in_universe_y,
    IFNULL(player_ship_count.ship_count, 0) AS sc,
    SUM(IFNULL(player_ship_count.ship_count, 0)) AS cluster_population
    FROM star_in_cluster LEFT JOIN star ON (star_in_cluster.star_id = star.id)
    LEFT JOIN
    (SELECT player_ship.orbiting_star_id, COUNT(1) as ship_count FROM player_ship GROUP BY player_ship.orbiting_star_id) AS player_ship_count ON player_ship_count.orbiting_star_id = star_in_cluster.star_id
    GROUP BY star_in_cluster.cluster_in_universe_x, star_in_cluster.cluster_in_universe_y HAVING cluster_population = 0''', []).fetchall()]


