from flask import Flask, render_template 
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask.logging import default_handler
import flask_login 
import logging


from .frontend import register_frontend

import sys
sys.path.append('..')
from pytrackvis.appenv import AppEnv
from pytrackvis.manager import Manager

def create_app(configfile=None):
    # We are using the "Application Factory"-pattern here, which is described
    # in detail inside the Flask docs:
    # http://flask.pocoo.org/docs/patterns/appfactories/

    app = Flask(__name__)
    @app.errorhandler(404) 
    # inbuilt function which takes error as parameter 
    def not_found(e): 
    # defining function 
        return render_template("404.html") 


    # We use Flask-Appconfig here, but this is not a requirement
    AppConfig(app)

    # Install our Bootstrap extension
    Bootstrap5(app)
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    # Our application uses blueprints as well; these go well with the
    # application factory. We already imported the blueprint, now we just need
    # to register it:
    # app.register_blueprint(frontend)
    app = frontend.register_frontend(app)

    # add the inventory helper
    AppEnv.config(app.config['PYTRACKVIS_CONFIG_FILE'])
    AppEnv.config_set("verbose",app.config['VERBOSE'])

    # Because we're security-conscious developers, we also hard-code disabling
    # the CDN support (this might become a default in later versions):
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    # redirect the log to a file
    app.logger.setLevel(logging.INFO)
    handler = logging.FileHandler(AppEnv.config().logs["app"])
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
    app.logger.addHandler(handler)

    app.manager = Manager(AppEnv.config())
    app.manager.logger = app.logger
    app.manager.startup()
    
    # inventory_helper.shutdown()

    @app.context_processor
    def add_imports():
        # to add modules to jinja2
        # Note: we only define the top-level module names!
        # return dict(email=email, datetime=datetime, os=os)
        return dict(flask_login=flask_login)
    return app