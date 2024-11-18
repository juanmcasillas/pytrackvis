# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/

from flask import Blueprint, render_template, \
                  flash, redirect, url_for, current_app, request, Response, \
                  after_this_request, send_file, jsonify

#from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from markupsafe import escape
import flask_login
import flask
import pythoncom          
import traceback
import logging
import os
import sys
import time

impl = Blueprint('impl', __name__)

# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.
@impl.route('/')
def index():
    return render_template('index.html')

@impl.route('/error', methods=['GET', 'POST'])
def error():
    msg = request.args.get("msg","Unknown error")
    return render_template('error.html',msg=msg)


@impl.route('/tracks/get_gjson', methods=['GET', 'POST'])
def tracks_get_gjson():
    id = request.args.get("id",None)
    if not id:
        return redirect(url_for('impl.error', msg="Invalid id"))
    
    # mockup
    trk_name =  current_app.file_manager.file_names[0]
    trk = current_app.file_manager.tracks[trk_name]
    return jsonify(trk.as_geojson_line()["data"]) 
    # default stuff to test things here.
    