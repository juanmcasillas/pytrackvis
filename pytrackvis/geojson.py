#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ############################################################################
#
# geojson.py
# 12/16/2024 (c) Juan M. Casillas <juanm.casillas@gmail.com>
#
# implement some tools for manage geojson objects
#
# ############################################################################

import copy

class GeoJSON:
    
    @staticmethod
    def feature_collection( features = []):
        o = {
             "type": "geojson",
             "data": {
                "type": "FeatureCollection",
                "features": [ ]
             }
        }
        o["data"]["features"].extend(features)
        return o
    
    @staticmethod
    def geojson_line( points, properties):
        o = {}
        o["type"] = "geojson"
        o["data"] = {
                "type": "Feature",
                "properties": { },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [ ]
                }
        }
        o["data"]["geometry"]["coordinates"].extend(points)
        o["data"]["properties"] = copy.copy(properties)
        return o

    @staticmethod
    def point_feature( coords, properties):
        o = {
            "type": "Feature",
            "properties": { },
            "geometry": {
                "type": "Point",
                "coordinates": [ ]
            }
        }
        o["geometry"]["coordinates"] = coords
        o["properties"] = copy.copy(properties)
        return o
    
    @staticmethod
    def polygon_feature( coords, properties):
        o = {
            "type": "Feature",
            "properties": { },
            "geometry": {
                "type": "Polygon",
                "coordinates": [ ]
            }
        }
        # polys are stored inside the coordinates. 
        o["geometry"]["coordinates"].append(coords)
        o["properties"] = copy.copy(properties)
        return o    

    @staticmethod
    def line_feature( coords, properties):
        o = {
            "type": "Feature",
            "properties": { },
            "geometry": {
                "type": "LineString",
                "coordinates": [ ]
            }
        }
        o["geometry"]["coordinates"] = coords
        o["properties"] = copy.copy(properties)
        return o   

    @staticmethod
    def geojson_point( coords, properties):
        o = {}
        o["type"] = "geojson"
        o["data"] = {
                "type": "Feature",
                "properties": { },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [ ]
                }
        }
        o["data"]["geometry"]["coordinates"] = coords
        o["data"]["properties"] = copy.copy(properties)
        return o
    
    def __init__(self):
        pass