# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/

from flask import Blueprint, render_template, \
                  flash, redirect, url_for, current_app, request, Response, \
                  after_this_request, send_file, jsonify, \
                  send_from_directory



#from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from markupsafe import escape

import flask
import traceback
import logging
import os
import sys
import time

from webapp.caching import cache

web_impl = Blueprint('web_impl', __name__)

@web_impl.route('/static/<path>')
@cache.cached(timeout=60*60*24)  # Cache for 24 hours
def static_files(path):
    return send_from_directory('static', path)

# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.
@web_impl.route('/')
def index():
    return render_template('index.html')

@web_impl.route('/error', methods=['GET', 'POST'])
def error():
    msg = request.args.get("msg","Unknown error")
    return render_template('error.html',msg=msg)

# page handlers

@web_impl.route('/tracks/list')
def tracks_list():
    tracks = current_app.manager.db_get_tracks_info()
    return render_template('list.html', tracks=tracks)

@web_impl.route('/tracks/show', methods=['GET', 'POST'])
def tracks_show():
    id = request.args.get("id",None)
    if not id:
        return redirect(url_for('web_impl.error', msg="Invalid id"))
    track = current_app.manager.db_get_track(id)

    return render_template('show.html',track=track, TOKENS=current_app.manager.config.tokens)

# json handlers

@web_impl.route('/tracks/as_geojson', methods=['GET', 'POST'])
@cache.cached(timeout=50,query_string=True)
def tracks_as_geojson():
    id = request.args.get("id",None)
    if not id:
        return redirect(url_for('web_impl.error', msg="Invalid id"))
    trk = current_app.manager.get_track(id)
    if trk is None:
        return redirect(url_for('web_impl.error', msg="Invalid track id"))
    
    return jsonify(trk.as_geojson_line()["data"]) 
    # default stuff to test things here.

@web_impl.route('/tracks/get_track_info', methods=['GET', 'POST'])
@cache.cached(timeout=50,query_string=True)
def tracks_get_track_info():
    id = request.args.get("id",None)
    if not id:
        return redirect(url_for('web_impl.error', msg="Invalid id"))

    trk = current_app.manager.db_get_track(id)
    #center_lat, center_lon, center_alt = trk.track_center()
    # use the data stored in db:

    obj = { 
        'id': id,
        'start': { 
            'long': trk['begin_long'], 
            'lat': trk['begin_lat'],
            'altitude': trk['begin_elev'] 
        },
        'end': { 
            'long': trk['end_long'], 
            'lat': trk['end_lat'],
            'altitude': trk['end_elev'] 
        },
        'center': { 
            'long': trk["middle_long"], 
            'lat': trk["middle_lat"],
            'altitude': trk["middle_elev"] 
        },
        'bounds': [[trk['min_long'], trk['min_lat']], [trk['max_long'], trk['max_lat']]]
    }

    return jsonify(obj) 
    # default stuff to test things here.