from flask import Flask

from gameservice.gameservice import GameService
from web import api, html
from web.db import get_db

app = Flask(__name__)

with app.app_context() as context:
    context.g.game_service = GameService(get_db())

app.register_blueprint(api.bp)
app.register_blueprint(html.bp)