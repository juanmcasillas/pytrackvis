from flask import Flask, render_template 
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap5
from flask_socketio import SocketIO
from flask.logging import default_handler
import logging
import time
import datetime 
import os

from .caching import cache
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
    app.logger.setLevel(AppEnv.config().logs["level"])
    handler = logging.FileHandler(AppEnv.config().logs["app"])
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s:%(funcName)s:%(lineno)d: %(message)s'))
    app.logger.addHandler(handler)

    app.manager = Manager(AppEnv.config())
    app.manager.logger = app.logger
    app.manager.startup()
    app.manager.load_tokens()
    
    cache.init_app(app)
    # inventory_helper.shutdown()

    #@app.context_processor
    #def add_imports():
        # # to add modules to jinja2
        # # Note: we only define the top-level module names!
        # # return dict(email=email, datetime=datetime, os=os)
        # pass
        # return dict(flask_login=flask_login)

    @app.template_filter('strftimestamp')
    def _jinja2_filter_strfftimestamp(stamp, fmt=None):
        
        if not stamp:
            return "--/--/---- --:--:--"
        fmt = fmt if fmt is not None else "%d/%m/%Y %H:%M:%S"
        
        dt = datetime.datetime.fromtimestamp(stamp)
        return  dt.strftime(fmt)

    @app.template_filter('strftimedelta')
    def _jinja2_filter_strftimedelta(stamp):
        
        hours = stamp // 3600 
        # remaining seconds
        stamp = stamp - (hours * 3600)
        # minutes
        minutes = stamp // 60
        # remaining seconds
        seconds = stamp - (minutes * 60)
        return "%02d:%02d:%02d" % (hours, minutes, seconds)
        

    @app.template_filter('humandistance')
    def _jinja2_filter_humandistance(distance):
        if distance >= 1000.0:
            s =  "%3.2f Km" % (float(distance) / 1000)
            return(s)

        return "%3.2f m" % float(distance)

    @app.template_filter('as_thumb')
    def _jinja2_filter_as_thumb(url):
        "add the tb suffix so we can manage thumbs in the web without breaking anything e.g. map.png -> map_tb.png"
        fname, extension = os.path.splitext(url)
        return "%s_tb%s" % (fname, extension)



    return app

def register_extensions(app):
    cache.init_app(app)
    with app.app_context():
        cache.clear()