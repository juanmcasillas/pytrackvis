##!/usr/bin/env python
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // filemanager.py 
# //
# // load the file from FIT or GPX source
# //
# // 23/10/2024 09:33:29  
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# //
# //
# /////////////////////////////////////////////////////////////////////////////

import argparse
import fitdecode
import os
import sys
import gpxpy
import gpxpy.gpx
import re
import configparser
import random
import uuid

# not needed due we do the magic from the frontend.
#import folium
#import folium.plugins
#import pydeck
#import leafmap.maplibregl as leafmap
#from maplibre.plugins import MapboxDrawControls, MapboxDrawOptions

from .helpers import C
from .track import Track, TrackPointFit, TrackPointGPX
from .appenv import AppEnv


class FileManager:
    FIT_FILE = ".fit"
    GPX_FILE = ".gpx"
    FILE_EXT = [ FIT_FILE, GPX_FILE ]

    def __init__(self, fnames):
        self.file_names = fnames
        self.verbose = AppEnv.config().verbose
        self.logger = None
        

        self.FILE_LOADER =  { 
            self.FIT_FILE: self._fit_loader,
            self.GPX_FILE: self._gpx_loader
        }
        self.file_types= {}
        self.tracks = {}
        for f in self.file_names:
            self.file_types[f] = self.guess_file_type(f)
        
    def guess_file_type(self, fname=None):
        fname = fname if fname else self.file_name
        file_name, file_extension = os.path.splitext(fname)
        file_extension = file_extension.lower()
        if file_extension in self.FILE_EXT:
            return file_extension
        return False

    def load_tokens(self):
        tokens = configparser.ConfigParser()
        tokens.read(AppEnv.config().api_key_file)
        if not 'TOKENS' in tokens.keys() or not 'MAPTILER_KEY' in tokens["TOKENS"]:
            print("can't get maptiler token")
            sys.exit(0)
        os.environ["MAPTILER_KEY"] = tokens["TOKENS"]["MAPTILER_KEY"]

    def _fit_loader(self, fname):

        if self.verbose:
            print("running fit_loader(%s)" % fname)

        extract_fields = [ 
            'timestamp', 'position_lat', 'position_long', 'altitude',
            # "optional"
            'enhanced_altitude',
            'enhanced_speed',
            'speed',
            'power',
            'grade',
            'heart_rate',
            'cadence',
            'temperature'
        ]

        track_points = Track(name=fname)

        with fitdecode.FitReader(fname) as fit:
            for frame in fit:
                # The yielded frame object is of one of the following types:
                # * fitdecode.FitHeader (FIT_FRAME_HEADER)
                # * fitdecode.FitDefinitionMessage (FIT_FRAME_DEFINITION)
                # * fitdecode.FitDataMessage (FIT_FRAME_DATA)
                # * fitdecode.FitCRC (FIT_FRAME_CRC)

                if frame.frame_type == fitdecode.FIT_FRAME_DATA and  \
                   frame.name == "record":
                    
                    # Here, frame is a FitDataMessage object.
                    # A FitDataMessage object contains decoded values that
                    # are directly usable in your script logic.
                    args = {}
                    for field in extract_fields:
                        if frame.has_field(field):
                            data = frame.get_field(field)
                            args[data.name] = data.value
                    point = TrackPointFit(**args)
                    track_points.add_point(point)
        
        return track_points


    def _gpx_loader(self, fname):
        if self.verbose:
            print("running gpx_loader(%s)" % fname)
       
        extract_fields = [ 
            'timestamp', 'position_lat', 'position_long', 'altitude',
            # "optional"
            'enhanced_altitude',
            'enhanced_speed',
            'speed',
            'power',
            'grade',
            'heart_rate',
            'cadence',
            'temperature'
        ]
        
        track_points = Track(name=fname)
        with open(fname, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        args = {}
                        args['lat'] = point.latitude
                        args['lon'] = point.longitude
                        args['ele'] = point.elevation
                        args['timestamp'] = str(point.time)

                        for e in point.extensions:
                            attr = re.sub('{.+}','',e.tag)
                            if attr == "TrackPointExtension":
                                for c in e:
                                    attr = re.sub('{.+}','',c.tag)
                                    args[attr] = c.text
                            else:
                                args[attr] = e.text
                        
                        point = TrackPointGPX(**args)
                        track_points.add_point(point)

        return track_points

    def load(self, optimize_points=True):
        for i in self.file_names:
            if not self.file_types[i]:
                raise ValueError("file %s has not valid type" % i)
            loader = self.FILE_LOADER[self.file_types[i]]
            track =  loader(i)
            track.set_internal_data(i, optimize_points=optimize_points)
            self.tracks[track.id] = track
        return self.tracks

    def stats(self,f):
        return self.tracks[f].stats()
    
    def get_track_ids(self):
        return list(self.tracks.keys())
    
    def get_tracks_info(self):
        tracks = []
        for t_id,t_data in self.tracks.items():
            tracks.append(C(id=t_data.id, name=t_data.name, stats=t_data.stats()))
        return tracks