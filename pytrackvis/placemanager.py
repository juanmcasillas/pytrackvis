##!/usr/bin/env python
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // placemanager.py 
# //
# // load the file from FIT or GPX source
# //
# // 23/10/2024 09:33:29  
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# //
# //
# /////////////////////////////////////////////////////////////////////////////


import re
import gpxpy
import datetime

from .trackmanager import TrackManager
from .place import Place
from .appenv import AppEnv

from fastkml.utils import find_all
from fastkml import KML
from fastkml import Placemark

class PlaceManager(TrackManager):
    KML_FILE = ".kml"
    GPX_FILE = ".gpx"
    FILE_EXT = [ KML_FILE, GPX_FILE ]

    def __init__(self, fnames):
        super().__init__(fnames)

        self.FILE_LOADER =  { 
            self.KML_FILE: self._kml_loader,
            self.GPX_FILE: self._gpx_loader
        }


    def _kml_loader(self, fname):

        if self.verbose:
            print("running kml_loader(%s) NOT_IMPLEMENTED" % fname)

        places = []
        mykml = KML.parse(fname, strict=False)
        placemarks = list(find_all(mykml, of_type=Placemark))
        for place in placemarks:
                point = place.geometry
               
                args = {}
                args['name'] = place.name
                args['latitude'] = point.x if point.x else 0.0
                args['longitude'] = point.y if point.y else 0.0
                args['elevation'] = point.z if point.z else 0.0
                args['description'] = place.description
                args['kind'] = "waypoint"
                args['stamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat(sep=' ',timespec='seconds')

                place = Place(args['name']).from_dict(args)
                place.calculate_hash() 
                places.append( place )
    
        return places


    def _gpx_loader(self, fname):
        if self.verbose:
            print("running gpx_loader(%s)" % fname)
       
        extract_fields = [ 
            'timestamp', 'latitude', 'longitude', 'altitude',
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
        
        places = []
        with open(fname, 'r', encoding="utf-8") as gpx_file:
            gpx = gpxpy.parse(gpx_file)
            for wpt in gpx.waypoints:
            
                args = {}
                args['name'] = wpt.name
                args['latitude'] = wpt.latitude if wpt.latitude else 0.0
                args['longitude'] = wpt.longitude if wpt.longitude else 0.0
                args['elevation'] = wpt.elevation if wpt.elevation else 0.0
                args['description'] = wpt.description
                args['kind'] = str(wpt.symbol)
                args['stamp'] = str(wpt.time)

                for e in wpt.extensions:
                    attr = re.sub('{.+}','',e.tag)
                    if attr == "WaypointExtension":
                        for c in e:
                            attr = re.sub('{.+}','',c.tag)
                            args[attr] = c.text
                    else:
                        args[attr] = e.text
                
                place = Place(args['name']).from_dict(args)
                place.calculate_hash() 
                places.append( place )
    
        return places



    def load(self):
        for i in self.file_names:
            if not self.file_types[i]:
                raise ValueError("file %s has not valid type" % i)
            loader = self.FILE_LOADER[self.file_types[i]]
            places =  loader(i)
            self.places = places
           
        return self.places

