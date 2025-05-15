import os
from flask_minify  import Minify
from flask import Flask, render_template

from config import config_dict
from app import create_app

# DEVELOPMENT_ENV = True

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

# app = Flask(__name__)

# app_data = {
#     "name": "Peter's Starter Template for a Flask Web App",
#     "description": "A basic Flask app using bootstrap for layout",
#     "author": "Peter Simeth",
#     "html_title": "Peter's Starter Template for a Flask Web App",
#     "project_name": "Starter Template",
#     "keywords": "flask, webapp, template, basic",
# }


# @app.route("/")
# def index():
#     return render_template("index.html", app_data=app_data)


# @app.route("/about")
# def about():
#     return render_template("about.html", app_data=app_data)


# @app.route("/service")
# def service():
#     return render_template("service.html", app_data=app_data)


# @app.route("/contact")
# def contact():
#     return render_template("contact.html", app_data=app_data)

app = create_app(app_config)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)
    
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    # app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)

if __name__ == "__main__":
    app.run()