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

import flask
import traceback
import logging
import os
import sys
import time

track_impl = Blueprint('track_impl', __name__)

@track_impl.route('/track/edit/rating', methods=['POST'])
def track_edit_rating():
    data = request.get_json(silent=True)
    if not data:
        return JsonResultError(404, "invalid json")

    if not 'id' in data.keys() or not 'rating' in data.keys():
        return JsonResultError(404, "invalid json - no keys")
    
    id = data['id']
    rating = data['rating']
    if id is None or rating is None:
        return JsonResultError(404, "invalid json - bad values")
    
    trk = current_app.manager.db_track_exists_id(id)
    if not trk:
        return JsonResultError(404, "invalid json - bad track id")
    
    current_app.manager.db_update_track_field('rating', id, rating)
    
    return jsonify(JsonResultOK(message="rating update successfully").response()) 
    # default stuff to test things here.