from flask import Flask, request, current_app, session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel
from flask_principal import Principal, Permission, RoleNeed, UserNeed,identity_loaded
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from elasticsearch import Elasticsearch
from celery import Celery
import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()
moment = Moment()
babel = Babel()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
principals = Principal()
admin_permission = Permission(RoleNeed('admin'))
moderator_permission = Permission(RoleNeed('moderator'))
user_permission = Permission(RoleNeed('user'))
cache = Cache()
toolbar = DebugToolbarExtension()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = "auth.login"
    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    celery.conf.update(app.config)
    toolbar.init_app(app)
    principals.init_app(app)
    cache.init_app(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        """Change the role via add the Need object into Role.
           Need the access the app object.
        """
        # Set the identity user object
        identity.user = current_user
 
        # Add the UserNeed to the identity user object
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))
 
        # Add each role to the identity user object
        if hasattr(current_user, 'role'):
            for role in current_user.role:
                identity.provides.add(RoleNeed(role.name))

    
    with app.app_context():
        from app.admin.views import admin
        admin.init_app(app)

    from app.models import AnonymousUser
    login.anonymous_user = AnonymousUser

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None


    if not app.debug and not app.testing:

        # Логгирование в файл
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/albom.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app

@babel.localeselector
def get_locale():
    if request.args.get('lang') and request.args.get('lang') in current_app.config['LANGUAGES']:
        session['lang'] = request.args.get('lang')
        return session['lang']
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

from app import models
