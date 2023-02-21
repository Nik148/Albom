from flask_login import login_required
from flask import render_template
from app.messender import bp

@bp.route('/messenger')
@login_required
def messenger():
    return render_template('messender/chats.html')