from flask import Blueprint

bp = Blueprint("messenger", __name__)

from app.messender import routes