##!/usr/bin/env python
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // place.py
# //
# // Define the class to map abstract tracks (collection of points)
# //
# // 23/10/2024 10:00:14
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# /////////////////////////////////////////////////////////////////////////////

import re
import gpxpy
import uuid
import datetime
import os
import time
import datetime
import copy
import hashlib
import os.path
import pprint 

from .helpers import bearing, distancePoints, module, C, remove_accents
from .geojson import GeoJSON


class Place:

    def __init__(self, name="Place", id=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.hash = None #see set_internal_data() for details
        self.name = name
        self.searchname = remove_accents(self.name)
        self.link = None
        self.latitude = None
        self.longitude = None
        self.elevation = None
        self.description = ""
        self.kind = ""
        self.radius = 25.0
        self.stamp = None
        
        self.kind_default_icon = 'nc'
        self.kind_mapping = {
            'home':                      '10',
            'bridge':                    '93',
            'tree':                      '46',
            'camera':                    '48',
            'circle with x':             '63',
            'controlled area':           '52',
            'danger area':               '53',
            'fishing hot spot facility': '36',
            'flag, red':                 '140',
            'flag, blue':                '141',
            'flag, green':               '142',
            'park':                      '105',
            'restricted area':           '54',
            'skull and crossbones':      '14',
            'waypoint':                  'nc',
            'peak':                      '106',
        }
        
    def kind_to_wpt(self, kind):
        if kind.lower() in self.kind_mapping.keys():
            return self.kind_mapping[kind.lower()]
        else:
            return self.kind_default_icon


    def calculate_hash(self):
        # hash in python3 is randomized.
        s = "%f %f %f" % (self.latitude, self.longitude, self.elevation)
        self.hash = hashlib.md5(s.encode('utf-8')).hexdigest()
        return self.hash

    def from_dict(self, d):
        for i in d:
            self.__setattr__(i, d[i])
        return self

    def pprint(self):
        pprint.pprint(self.as_dict(), indent=4)

    def as_dict(self):
        d = {}
        d['id']           = self.id         
        d['hash']         = self.hash       
        d['name']         = self.name       
        d['searchname']   = self.searchname 
        d['link']         = self.link       
        d['latitude']     = self.latitude   
        d['longitude']    = self.longitude  
        d['elevation']    = self.elevation  
        d['description']  = self.description
        d['kind']         = self.kind       
        d['radius']       = self.radius     
        d['stamp']        = self.stamp      
        return d

    def as_geojson_point(self):
        coords = self.longitude, self.latitude, self.elevation


        properties = {
            'name': self.name,
            'link': self.link,
            'description': self.description,
            'kind': self.kind,
            'icon': self.kind_to_wpt(self.kind)
        }
        return GeoJSON.point_feature(coords, properties )
 


    def as_tuple(self, db=False):

        if not db:
            # return the current object
            # else, return also the stats in db format
            pass
        # id not passed
        return (self.hash, self.name, self.searchname, self.link,
                self.latitude, self.longitude, self.elevation, 
                self.description,
                self.kind, 
                self.radius,
                self.stamp
        )
    
   