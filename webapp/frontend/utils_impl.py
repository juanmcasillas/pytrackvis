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

utils_impl = Blueprint('utils_impl', __name__)



@utils_impl.route('/utils/check_catastro', methods=['GET','POST'])
def utils_check_catastro():
    # http://localhost:5000/utils/check_catastro?lat=40.392238&lng=-4.266139
    lat = request.args.get("lat",None)
    lng = request.args.get("lng",None)
    
    if 'lat' in request.form.keys():
        lat = request.form['lat']

    if 'lng' in request.form.keys():
        lng = request.form['lng']
       
    if not lat or not lng:
        return jsonify(error = True,
                        text = 'bad lat/lng',
                        code = 2)

    data, geodata = current_app.manager.check_catastro(lat, lng)

    return jsonify(error = False,
                    text = 'ok',
                    data = data,
                    gdata = geodata)


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
