from flask import Blueprint

bp = Blueprint('adm',__name__)

from app.admin import views