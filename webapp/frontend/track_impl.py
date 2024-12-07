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
        return JsonResultError(500, "invalid json").response()

    if not 'id' in data.keys() or not 'rating' in data.keys():
        return JsonResultError(500, "invalid json - no keys").response()
    
    id = data['id']
    rating = data['rating']
    if id is None or rating is None:
        return JsonResultError(500, "invalid json - bad values").response()
    
    trk = current_app.manager.db_track_exists_id(id)
    if not trk:
        return JsonResultError(500, "invalid json - bad track id").response()
    
    current_app.manager.db_update_track_field('rating', id, rating)
    
    return jsonify(JsonResultOK(message="rating update successfully").response()) 
    # default stuff to test things here.


@track_impl.route('/track/edit/name', methods=['POST'])
def track_edit_name():
    
    if not 'id' in request.form.keys() or not 'name' in request.form.keys():
        return JsonResultError(500, "invalid form - no keys").response()
      
    id = request.form['id']
    name = request.form['name']
    if id is None or name is None:
        return JsonResultError(500, "invalid form - bad values").response()
    
    trk = current_app.manager.db_track_exists_id(id)
    if not trk:
        return JsonResultError(500, "invalid form - bad track id").response()
    
    current_app.manager.db_update_track_field('name', id, name)
    
    return name,200
    # default stuff to test things here.




@track_impl.route('/track/edit/description', methods=['POST'])
def track_edit_description():
    if not 'id' in request.form.keys() or not 'description' in request.form.keys():
        return JsonResultError(500, "invalid form - no keys").response()
      
    id = request.form['id']
    description = request.form['description']
    if id is None or description is None:
        return JsonResultError(500, "invalid form - bad values").response()
    
    trk = current_app.manager.db_track_exists_id(id)
    if not trk:
        return JsonResultError(500, "invalid form - bad track id").response()
    
    current_app.manager.db_update_track_field('description', id, description)
    
    return description,200
    # default stuff to test things here.