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

from .webhelpers import *

#from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from markupsafe import escape

import io
import flask
import traceback
import logging
import os
import sys
import time
from webapp.caching import cache

places_impl = Blueprint('places_impl', __name__)



@places_impl.route('/places/as_geojson', methods=['GET', 'POST'])
##@cache.cached(timeout=100000,query_string=True)
def places_as_geojson():

    data = current_app.manager.get_places_as_geojson()["data"]
    return jsonify(data) 

    #geojson_fname_abs = current_app.manager.geojson_previews.map_object(trk['hash'],create_dirs=True)
    #geojson_fname = "%s.geojson" % geojson_fname_abs
    # if not os.path.exists(geojson_fname):
    #     current_app.logger.info("creating persistent geojson for track %s" % id)
    #     # read the full track (costly)
    #     track = current_app.manager.get_track(id)
    #     with open(geojson_fname,"w+") as geojson_fd:
    #         data = json.dumps(track.as_geojson_line()["data"])
    #         geojson_fd.write(data)
    # else:
    #     with open(geojson_fname,"r+") as geojson_fd:
    #         data = geojson_fd.read()
    
    return data
    # return jsonify(trk.as_geojson_line()["data"]) 
    # default stuff to test things here.
