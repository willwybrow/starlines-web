import uuid

from flask import render_template, g, url_for, request, make_response, Blueprint
from werkzeug.utils import redirect

from game.geometry import Point
from game.universe import CLUSTER_SIZE
from gameservice.gameservice import GameService
from web.db import get_db

bp = Blueprint("web", __name__, static_folder="static", template_folder="templates", url_prefix="/web")


@bp.before_request
def initialise_services():
    g.game_service = GameService(get_db())
    try:
        g.player_id = uuid.UUID(request.cookies['player_id'])
    except:
        pass

@bp.route("/")
def index():
    if 'player_id' not in request.cookies:
        return render_template('login.html')
    universe = g.game_service.universe_service.new_universe()
    return redirect(url_for('.view_universe_page', universe_id=str(universe.id)))


@bp.route("/universe/<universe_id>")
def view_universe_page(universe_id=None):
    uid = uuid.UUID(universe_id)
    return render_template('universe.html', universe_id=uid)


@bp.route("/login", methods=['POST'])
def login():
    name = request.form.get("name")
    player = g.game_service.new_player(name)
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('player_id', str(player.id))
    return resp

@bp.route("/universe/<universe_id>/cluster/<int(signed=True):x>/<int(signed=True):y>")
def view_cluster_page(universe_id=None, x=None, y=None):
    uid = uuid.UUID(universe_id)
    cp = Point(x, y)
    stars = g.game_service.get_cluster_stars(uid, cp)
    star_grid = []
    for xi in range(0, CLUSTER_SIZE):
        star_grid.append([])
        for yi in range(0, CLUSTER_SIZE):
            star_grid[xi].append(stars.get(Point(xi, yi)))
    return render_template('cluster.html', universe_id=universe_id, cluster_coordinate=cp, list_of_list_of_stars=star_grid)


@bp.route("/star/<star_id>")
def view_star_details(star_id):
    sid = uuid.UUID(star_id)
    star_ship_count = g.game_service.get_star_details(sid)
    return render_template('star.html', star_ship_count=star_ship_count)