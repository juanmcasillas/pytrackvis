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

# page handlers

@impl.route('/tracks/list')
def tracks_list():
    tracks = current_app.file_manager.get_tracks_info()
    return render_template('list.html', tracks=tracks)

@impl.route('/tracks/show', methods=['GET', 'POST'])
def tracks_show():
    id = request.args.get("id",None)
    if not id:
        return redirect(url_for('impl.error', msg="Invalid id"))
    track = current_app.file_manager.tracks[id]
    return render_template('show.html',track=track)

# json handlers

@impl.route('/tracks/as_geojson', methods=['GET', 'POST'])
def tracks_as_geojson():
    id = request.args.get("id",None)
    if not id:
        return redirect(url_for('impl.error', msg="Invalid id"))
    trk = current_app.file_manager.tracks[id]
    return jsonify(trk.as_geojson_line()["data"]) 
    # default stuff to test things here.

@impl.route('/tracks/get_track_info', methods=['GET', 'POST'])
def tracks_get_track_info():
    id = request.args.get("id",None)
    if not id:
        return redirect(url_for('impl.error', msg="Invalid id"))

    trk = current_app.file_manager.tracks[id]
    center_lat, center_lon, center_alt = trk.track_center()
    obj = { 
        'id': id,
        'start': { 
            'long': trk.start_point().position_long, 
            'lat': trk.start_point().position_lat,
            'altitude': trk.start_point().altitude 
        },
        'end': { 
            'long': trk.end_point().position_long, 
            'lat': trk.end_point().position_lat,
            'altitude': trk.end_point().altitude 
        },
        'center': { 
            'long': center_lon, 
            'lat': center_lat,
            'altitude': center_alt 
        },
        'bounds':  trk.bounds(lonlat=True)
    }

    return jsonify(obj) 
    # default stuff to test things here.