from flask import render_template
from app.errors import bp

@bp.app_errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404
