import json
from uuid import UUID

from flask import g, request, Blueprint

from game.geometry import Point
from game.star import Star, ClusterID
from game.universe import CLUSTER_SIZE
from gameservice.gameservice import GameService
from web.db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.before_request
def initialise_services():
    g.game_service = GameService(get_db())
    try:
        g.player_id = UUID(request.cookies['player_id'])
    except:
        pass

@bp.route('/universe/cluster/<x>/<y>')
def view_cluster(x=0, y=0):
    coordinate = ClusterID(x, y)
    stars = g.game_service.get_cluster_stars(coordinate)
    star_grid = []
    for xi in range(0, CLUSTER_SIZE):
        star_grid.append([])
        for yi in range(0, CLUSTER_SIZE):
            star_grid[xi].append(json_star(stars.get(Point(xi, yi))))
    return json.dumps(star_grid)


def json_star(star: Star):
    if star is None:
        return {}
    return {
        "id": str(star.id),
        "current_mass": star.current_mass,
        "maximum_mass": star.maximum_mass,
        "colour": star.colour.hex
    }