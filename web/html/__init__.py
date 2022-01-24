import uuid

from flask import render_template, g, url_for, request, make_response, Blueprint
from werkzeug.utils import redirect

from game.geometry import Point
from game.player import PlayerID
from game.star import ClusterID, StarID
from game.universe import CLUSTER_SIZE
from gameservice.gameservice import GameService
from web.db import get_db

bp = Blueprint("web", __name__, static_folder="static", template_folder="templates", url_prefix="/web")

@bp.before_request
def initialise_services():
    g.game_service = GameService(get_db())
    try:
        g.player = g.game_service.get_player(PlayerID(request.cookies['player_id']))
    except:
        pass

@bp.route("/")
def index():
    if 'player_id' not in request.cookies:
        return render_template('login.html')
    universe = g.game_service.universe_service.new_universe()
    return redirect(url_for('.view_universe_page'))


@bp.route("/universe")
def view_universe_page():
    my_ships = g.game_service.get_player_ships(g.player)
    return render_template('universe.html', ships=my_ships)


@bp.route("/login", methods=['POST'])
def login():
    name = request.form.get("name")
    player = g.game_service.new_player(name)
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('player_id', str(player.id))
    return resp

@bp.route("/universe/cluster/<int(signed=True):x>/<int(signed=True):y>")
def view_cluster_page(x=None, y=None):
    cp = ClusterID(x, y)
    stars = g.game_service.get_cluster_stars(cp)
    star_grid = []
    for xi in range(0, CLUSTER_SIZE):
        star_grid.append([])
        for yi in range(0, CLUSTER_SIZE):
            star_grid[xi].append(stars.get(Point(xi, yi)))
    return render_template('cluster.html', cluster_coordinate=cp, list_of_list_of_stars=star_grid)


@bp.route("/star/<star_id>")
def view_star_details(star_id):
    sid = StarID(star_id)
    star_ship_count = g.game_service.get_star_details(sid)
    return render_template('star.html', star_id=sid, star_ship_count=star_ship_count)