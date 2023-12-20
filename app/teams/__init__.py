from flask import Blueprint

bp = Blueprint('teams', __name__, url_prefix='/team')

from app.teams import routes