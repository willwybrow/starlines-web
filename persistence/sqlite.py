import random
import sqlite3
from sqlite3 import Connection
from typing import List, Dict, Callable

from game.geometry import Point
from game.player import Player, PlayerID
from game.ship import Ship, Probe, Harvester, Stabiliser
from game.star import Star, Cluster, ClusterID, StarID


class SQLite3Db:
    def __init__(self):
        self.connection = sqlite3.connect('starlines.db')
        self.connection.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        with self.connection as con:
            con.execute(''' CREATE TABLE IF NOT EXISTS star(id VARCHAR(36), current_mass INTEGER, maximum_mass INTEGER, PRIMARY KEY (id)) ''')
            con.execute(''' CREATE TABLE IF NOT EXISTS star_in_cluster(cluster_id INTEGER, star_in_cluster_x INTEGER, star_in_cluster_y INTEGER, star_id VARCHAR(36), PRIMARY KEY(cluster_id, star_in_cluster_x, star_in_cluster_y), FOREIGN KEY (star_id) REFERENCES star(id)) ''')
            con.execute(''' CREATE TABLE IF NOT EXISTS player (id VARCHAR(36), name TEXT, PRIMARY KEY (id)) ''')
            con.execute(''' CREATE TABLE IF NOT EXISTS ship(id VARCHAR(36), model TEXT, player_id VARCHAR(36), orbiting_star_id VARCHAR(36), task TEXT, PRIMARY KEY(id), FOREIGN KEY (player_id) REFERENCES player(id), FOREIGN KEY (orbiting_star_id) REFERENCES star(id)) ''')
            con.execute(''' CREATE TABLE IF NOT EXISTS starline_member(starline_id VARCHAR(36), star_id VARCHAR(36), PRIMARY KEY (starline_id, star_id), FOREIGN KEY (star_id) REFERENCES star(id)) ''')

    def load_player_only(self, player_id: PlayerID):
        with self.connection as con:
            row = con.execute(''' SELECT id, name FROM player WHERE id = ? LIMIT 1 ''', [str(player_id)]).fetchone()
            return Player(PlayerID(row['id']), row['name'])

    def save_new_player(self, player: Player):
        with self.connection as con:
            con.execute(''' INSERT INTO player (id, name) VALUES (?, ?) ''', [str(player.id), player.name])
            return player

    def load_universe(self) -> Dict[ClusterID, Cluster]:
        with self.connection as con:
            clusters = {}
            for row in con.execute(''' SELECT cluster_id, star_in_cluster_x, star_in_cluster_y, star_id FROM star_in_cluster ''', []).fetchall():
                cluster_point = ClusterID.from_id(row['cluster_id'])
                if cluster_point not in clusters:
                    clusters[cluster_point] = Cluster(cluster_point, dict())
                star_point = Point(row['star_in_cluster_x'], row['star_in_cluster_y'])
                clusters[cluster_point].stars[star_point] = StarID(row['star_id'])

            return clusters

    def load_cluster_only(self, cluster_coordinate: ClusterID) -> Cluster:
        with self.connection as con:
            stars = {}

            for row in con.execute(''' SELECT star_in_cluster_x, star_in_cluster_y, star_id FROM star_in_cluster WHERE cluster_id = ? ''', [cluster_coordinate.id]).fetchall():
                star_point = Point(row['star_in_cluster_x'], row['star_in_cluster_y'])
                stars[star_point] = StarID(row['star_id'])

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
                star.id AS star_id,
                star.current_mass AS current_mass,
                star.maximum_mass AS maximum_mass,
                IFNULL(player_probe_count.ship_count, 0) AS probes_at_star
                FROM star_in_cluster LEFT JOIN star ON (star_in_cluster.star_id = star.id)
                LEFT JOIN
                (SELECT ship.orbiting_star_id, COUNT(1) as ship_count FROM ship WHERE ship.model = 'probe' GROUP BY ship.orbiting_star_id) AS player_probe_count ON player_probe_count.orbiting_star_id = star_in_cluster.star_id
                WHERE star_in_cluster.cluster_id = ? ''', [cluster_coordinate.id]).fetchall():
            star_point = Point(row['star_in_cluster_x'], row['star_in_cluster_y'])
            stars[star_point] = Star(StarID(row['star_id']), row['current_mass'], row['maximum_mass'], row['probes_at_star'])
        return stars

    def load_ships_at_star(self, star_id: StarID) -> Dict[PlayerID, Dict[str, int]]:
        with self.connection as con:
            result = con.execute(''' SELECT player_id, model, COUNT(1) as ship_count FROM ship WHERE orbiting_star_id = ? GROUP BY ship.player_id, ship.model ''', [str(star_id)])
            ship_map = {}
            for row in result.fetchall():
                player_id = PlayerID(row['player_id'])
                if player_id not in ship_map:
                    ship_map[player_id] = {}
                model = row['model']
                if model not in ship_map[player_id]:
                    ship_map[player_id][model] = row['ship_count']
            return ship_map

    def load_player_ships(self, player: Player):
        with self.connection as con:
            for row in con.execute(''' SELECT id, model, orbiting_star_id FROM ship WHERE player_id = ? ''', [str(player.id)]).fetchall():
                if row['model'] == 'probe':
                    yield Probe(row['id'], StarID(row['orbiting_star_id']))
                if row['model'] == 'harvester':
                    yield Harvester(row['id'], StarID(row['orbiting_star_id']))
                if row['model'] == 'stabiliser':
                    yield Stabiliser(row['id'], StarID(row['orbiting_star_id']))

    def save_new_star(self, star: Star) -> bool:
        with self.connection as con:
            success = con.execute(''' INSERT INTO star (id, current_mass, maximum_mass) VALUES (?, ?, ?)''', [str(star.id), star.current_mass, star.maximum_mass]).rowcount > 0
            return success

    @staticmethod
    def save_new_stars_query(con: Connection, cluster_coordinate: ClusterID, star_map: Dict[Point, Star]):
        success = con.executemany(''' INSERT INTO star (id, current_mass, maximum_mass) VALUES (?, ?, ?)''', [(str(star.id), star.current_mass, star.maximum_mass) for star in star_map.values()]).rowcount > 0
        success = success & con.executemany(''' INSERT INTO star_in_cluster (cluster_id, star_in_cluster_x, star_in_cluster_y, star_id) VALUES (?, ?, ?, ?)''', [(cluster_coordinate.id, coordinate.x, coordinate.y, str(star.id)) for coordinate, star in star_map.items()]).rowcount > 0
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
        return con.execute(''' INSERT INTO ship (id, model, player_id, orbiting_star_id) VALUES (?, ?, ?, ?)''', [str(ship.id), ship.model, str(player.id), str(orbiting_star.id)])

    def assign_player_to_empty_cluster(self, player: Player, ships_to_place: List[Ship], star_picking_algorithm = lambda s: max(s, key=lambda x: x.current_mass)) -> bool:
        with self.connection as con:
            empty_cluster = random.choice(self.empty_generated_clusters_query(con))
            star_map = SQLite3Db.load_cluster_stars_query(con, empty_cluster)
            best_star = star_picking_algorithm(star_map.values())
            [SQLite3Db.save_new_ship_query(con, player, ship_to_place, best_star) for ship_to_place in ships_to_place]
        return True


    def ensure_minimum_universe_size(self, cluster_creator: Callable[[ClusterID], Dict[Point, Star]]):
        with self.connection as con:
            if SQLite3Db.universe_size_query(con) == 0:
                for x in range(-5, 5):
                    for y in range(-5, 5):
                        cluster_id = ClusterID(x,y)
                        star_map = cluster_creator(cluster_id)
                        SQLite3Db.save_new_stars_query(con, cluster_id, star_map)

    @staticmethod
    def universe_size_query(con: Connection):
        return con.execute(''' SELECT COUNT(DISTINCT cluster_id) AS cluster_count FROM star_in_cluster; ''').fetchone()['cluster_count']

    @staticmethod
    def empty_generated_clusters_query(con) -> List[ClusterID]:
        return [ClusterID.from_id(row['cluster_id']) for row in con.execute(''' SELECT
    star_in_cluster.cluster_id AS cluster_id,
    IFNULL(player_ship_count.ship_count, 0) AS sc,
    SUM(IFNULL(player_ship_count.ship_count, 0)) AS cluster_population
    FROM star_in_cluster LEFT JOIN star ON (star_in_cluster.star_id = star.id)
    LEFT JOIN
    (SELECT ship.orbiting_star_id, COUNT(1) as ship_count FROM ship GROUP BY ship.orbiting_star_id) AS player_ship_count ON player_ship_count.orbiting_star_id = star_in_cluster.star_id
    GROUP BY star_in_cluster.cluster_id HAVING cluster_population = 0''', []).fetchall()]


