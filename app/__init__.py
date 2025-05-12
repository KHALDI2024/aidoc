import os
from flask import Flask
# from flask_login import LoginManager
# from flask_sqlalchemy import SQLAlchemy
from importlib import import_module

# db = SQLAlchemy()
# login_manager = LoginManager()

# def register_extensions(app):
#     db.init_app(app)
    # login_manager.init_app(app)

# def register_blueprints(app):
#     for module_name in ('home', ):
#         module = import_module('app.{}.routes'.format(module_name))
#         app.register_blueprint(module.blueprint)

# from app.authentication.oauth import github_blueprint, google_blueprint

def create_app(config):

    # Contextual
    static_prefix = '/static'

    TEMPLATES_FOLDER = os.path.join(config.BASE_DIR, 'app', 'templates')
    STATIC_FOLDER = os.path.join(config.BASE_DIR, 'app', 'static')

    print(' > TEMPLATES_FOLDER: ' + TEMPLATES_FOLDER)
    print(' > STATIC_FOLDER:    ' + STATIC_FOLDER)

    app = Flask(__name__, static_url_path=static_prefix, template_folder=TEMPLATES_FOLDER, static_folder=STATIC_FOLDER)

    app.config.from_object(config)
    # register_extensions(app)
    # register_blueprints(app)
    module = import_module('app.routes')
    app.register_blueprint(module.blueprint)
    # app.register_blueprint(github_blueprint, url_prefix="/login")    
    # app.register_blueprint(google_blueprint, url_prefix="/login")    
    return app
