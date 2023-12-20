from flask import Blueprint

from app.teams import routes

bp = Blueprint('teams', __name__, url_prefix='/team')

