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
import json
from webapp.caching import cache
from pytrackvis.helpers import remove_accents
from .webhelpers import *


web_impl = Blueprint('web_impl', __name__)

#remove after touch the JS files (in static path)
#@web_impl.route('/static/<path>')
#@cache.cached(timeout=60*60*24)  # Cache for 24 hours
def static_files(path):
    return send_from_directory('static', path)

# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.
@web_impl.route('/')
def index():
    return redirect(url_for('web_impl.tracks_list'))

@web_impl.route('/error', methods=['GET', 'POST'])
def error():
    msg = request.args.get("msg","Unknown error")
    return render_template('error.html',msg=msg)

# page handlers

@web_impl.route('/dashboard.html', methods=['GET'])
def tracks_dashboard():

    stats = current_app.manager.getstats_from_db()
    return render_template('dashboard.html',stats=stats, stats_json=json.dumps(stats))

@web_impl.route('/tracks/query', methods=['POST'])
def tracks_query():
    
    data = request.get_json(silent=True)
    if not data:
        return JsonResultError(500, "invalid json").response()

    if not 'query' in data.keys():
        return JsonResultError(500, "invalid json - no keys").response()
    
    query = data['query']
    if query is None:
        query = current_app.manager.config.queries['default']
    else:
        query = remove_accents(query)
        result, query = current_app.manager.query_parser.run(query)
        if not result:
            return jsonify(error = True,
                          text = 'malformed query: %s' % query,
                          code = 1,
                          tracks = [])
                
    current_app.logger.info("Parsed query: <%s>" % query)
    
    try:
        tracks = current_app.manager.db_get_tracks_info(query)
    except Exception as e:
        return jsonify(error = True,
                        text = 'bad query: %s' % e,
                        code = 2,
                        tracks = [])

    return jsonify(error = False,
                   text = 'success',
                   code = 0,
                   tracks = tracks)

@web_impl.route('/tracks/list', methods=['GET'])
def tracks_list():

    query = request.args.get("query",None)
    if query is None:
        query = ""
    return render_template('list.html', query=query)




@web_impl.route('/tracks/view', methods=['GET', 'POST'])
def tracks_view():
    id = request.args.get("id",None)
    if not id:
        return redirect(url_for('web_impl.error', msg="Invalid id"))
    track = current_app.manager.db_get_track(id)

    return render_template('view.html',track=track, TOKENS=current_app.manager.config.tokens)



# json handlers
