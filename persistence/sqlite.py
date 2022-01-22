import sqlite3
import uuid
from typing import List, Dict
from uuid import UUID

from game.geometry import Point
from game.player import Player
from game.ship import Ship
from game.star import Star, Cluster, ClusterID, StarID
from game.universe import Universe

class SQLite3Db:
    def __init__(self):
        self.db = sqlite3.connect('starlines.db')
        self.init_db()

    def init_db(self):
        cursor = self.db.cursor()

        cursor.execute(''' CREATE TABLE IF NOT EXISTS universe(id VARCHAR(36), PRIMARY KEY (id)) ''')
        cursor.execute(''' CREATE TABLE IF NOT EXISTS star(id VARCHAR(36), current_mass INTEGER, maximum_mass INTEGER, PRIMARY KEY (id)) ''')
        cursor.execute(''' CREATE TABLE IF NOT EXISTS star_in_cluster(universe_id VARCHAR(36), cluster_in_universe_x INTEGER, cluster_in_universe_y INTEGER, star_in_cluster_x INTEGER, star_in_cluster_y INTEGER, star_id VARCHAR(36), PRIMARY KEY(universe_id, cluster_in_universe_x, cluster_in_universe_y, star_in_cluster_x, star_in_cluster_y), FOREIGN KEY (cluster_id) REFERENCES cluster(id), FOREIGN KEY (star_id) REFERENCES star(id)) ''')
        cursor.execute(''' CREATE TABLE IF NOT EXISTS player (id VARCHAR(36), name TEXT, PRIMARY KEY (id)) ''')
        cursor.execute(''' CREATE TABLE IF NOT EXISTS player_ship(id VARCHAR(36), ship_type VARCHAR(10), player_id VARCHAR(36), orbiting_star_id VARCHAR(36), PRIMARY KEY(id), FOREIGN KEY (player_id) REFERENCES player(id), FOREIGN KEY (orbiting_star_id) REFERENCES star(id)) ''')

        self.db.commit()

    def load_player_only(self, player_id: UUID):
        cursor = self.db.cursor()
        row = cursor.execute(''' SELECT id, name FROM player WHERE id = ? LIMIT 1 ''', [str(player_id)]).fetchone()
        return Player(UUID(row[0]), row[1])

    def load_player_ships(self, player_id: UUID):
        cursor = self.db.cursor()
        row = cursor.execute(''' SELECT id, name FROM player WHERE id = ? LIMIT 1 ''', [str(player_id)]).fetchone()
        return Player(UUID(row[0]), row[1])

    def save_new_player(self, player_id: UUID, name: str):
        cursor = self.db.cursor()
        success = cursor.execute(''' INSERT INTO player (id, name) VALUES (?, ?) ''', [str(player_id), name]).rowcount == 1
        self.db.commit()
        return success

    def save_new_universe(self, universe_id: UUID):
        cursor = self.db.cursor()
        success = cursor.execute(''' INSERT INTO universe (id) VALUES (?) ''', [str(universe_id)]).rowcount == 1
        self.db.commit()
        return success

    def load_universe(self, universe_id: UUID) -> Universe:
        cursor = self.db.cursor()

        clusters = {}

        for row in cursor.execute(''' SELECT cluster_in_universe_x, cluster_in_universe_y, star_in_cluster_x, star_in_cluster_y, star_id FROM star_in_cluster WHERE universe_id = ?  ''', [str(universe_id)]).fetchall():
            cluster_point = Point(row[0], row[1])
            if cluster_point not in clusters:
                clusters[cluster_point] = Cluster(ClusterID(universe_id, cluster_point), dict())
            star_point = Point(row[2], row[3])
            clusters[cluster_point].stars[star_point] = StarID(row[4])

        return Universe(universe_id, clusters)

    def deep_load_cluster(self):
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
WHERE star_in_cluster.universe_id = ?
AND star_in_cluster.cluster_in_universe_x = ?
AND star_in_cluster.cluster_in_universe_y = ? '''
        pass

    def load_cluster_only(self, universe_id: UUID, cluster_coordinate: Point) -> Cluster:
        cursor = self.db.cursor()

        stars = {}

        for row in cursor.execute(''' SELECT star_in_cluster_x, star_in_cluster_y, star_id FROM star_in_cluster WHERE universe_id = ? AND cluster_in_universe_x = ? AND cluster_in_universe_y = ? ''', [str(universe_id), cluster_coordinate.x, cluster_coordinate.y]).fetchall():
            star_point = Point(row[0], row[1])
            stars[star_point] = StarID(row[2])

        return Cluster(ClusterID(universe_id, cluster_coordinate), stars)

    def load_cluster_stars(self, universe_id: UUID, cluster_coordinate: Point) -> Dict[Point, Star]:
        cursor = self.db.cursor()

        stars = {}

        for row in cursor.execute(''' SELECT
star_in_cluster.star_in_cluster_x,
star_in_cluster.star_in_cluster_y,
star.id,
star.current_mass,
star.maximum_mass,
IFNULL(player_ship_count.ship_count, 0)
FROM star_in_cluster LEFT JOIN star ON (star_in_cluster.star_id = star.id)
LEFT JOIN
(SELECT player_ship.orbiting_star_id, COUNT(1) as ship_count FROM player_ship GROUP BY player_ship.orbiting_star_id) AS player_ship_count ON player_ship_count.orbiting_star_id = star_in_cluster.star_id
WHERE star_in_cluster.universe_id = ?
AND star_in_cluster.cluster_in_universe_x = ?
AND star_in_cluster.cluster_in_universe_y = ? ''', [str(universe_id), cluster_coordinate.x, cluster_coordinate.y]).fetchall():
            star_point = Point(row[0], row[1])
            stars[star_point] = Star(StarID(row[2]), row[3], row[4])

        return stars


    def load_ships_at_star(self, star_id: StarID):
        cursor = self.db.cursor()
        result = cursor.execute(''' SELECT player_id, COUNT(1) as ship_count FROM player_ship WHERE orbiting_star_id = ? GROUP BY player_ship.player_id ''', [str(star_id)])
        return {UUID(row[0]): row[1] for row in result.fetchall()}


    def save_new_star(self, star: Star) -> bool:
        cursor = self.db.cursor()

        success = cursor.execute(''' INSERT INTO star (id, current_mass, maximum_mass) VALUES (?, ?, ?)''', [str(star.id), star.current_mass, star.maximum_mass]).rowcount > 0
        self.db.commit()
        return success

    def save_new_stars(self, universe_id: UUID, cluster_coordinate: Point, star_map: Dict[Point, Star]):
        cursor = self.db.cursor()
        success = cursor.executemany(''' INSERT INTO star (id, current_mass, maximum_mass) VALUES (?, ?, ?)''', [(str(star.id), star.current_mass, star.maximum_mass) for star in star_map.values()]).rowcount > 0
        success = success & cursor.executemany(''' INSERT INTO star_in_cluster (universe_id, cluster_in_universe_x, cluster_in_universe_y, star_in_cluster_x, star_in_cluster_y, star_id) VALUES (?, ?, ?, ?, ?, ?)''', [(str(universe_id), cluster_coordinate.x, cluster_coordinate.y, coordinate.x, coordinate.y, str(star.id)) for coordinate, star in star_map.items()]).rowcount > 0
        self.db.commit()
        return success

    def save_new_ship(self, player: Player, ship: Ship, star: Star):
        cursor = self.db.cursor()
        success = cursor.execute(''' INSERT INTO player_ship (id, ship_type, player_id, orbiting_star_id) VALUES (?, ?, ?, ?)''', [str(ship.id), ship.model, str(player.id), str(star.id)]).rowcount > 0
        self.db.commit()
        return success

    def find_empty_generated_clusters(self, universe_id):
        cursor = self.db.cursor()
        results = cursor.execute(''' SELECT
star_in_cluster.cluster_in_universe_x,
star_in_cluster.cluster_in_universe_y,
IFNULL(player_ship_count.ship_count, 0) AS sc,
SUM(IFNULL(player_ship_count.ship_count, 0)) AS cluster_population
FROM star_in_cluster LEFT JOIN star ON (star_in_cluster.star_id = star.id)
LEFT JOIN
(SELECT player_ship.orbiting_star_id, COUNT(1) as ship_count FROM player_ship GROUP BY player_ship.orbiting_star_id) AS player_ship_count ON player_ship_count.orbiting_star_id = star_in_cluster.star_id
WHERE star_in_cluster.universe_id = ? GROUP BY star_in_cluster.cluster_in_universe_x, star_in_cluster.cluster_in_universe_y HAVING cluster_population = 0''', [str(universe_id)])
        return [Point(row[0], row[1]) for row in results.fetchall()]
