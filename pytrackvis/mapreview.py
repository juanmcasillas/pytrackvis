#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ############################################################################
#
# mapreview.py
# 12/01/2024 (c) Juan M. Casillas <juanm.casillas@gmail.com>
#
# create a simple map preview using osm and some classes.
#
# ############################################################################


from .mapper import OSMMapper
from .helpers import C
import gpxpy

class MapPreviewManager:
    def __init__(self, config, cachedir="osm_cache", debug=True):
        self.cachedir = cachedir
        self.debug = debug
        self.config = config

        # for compute the clockwise image.
        self.direction_width = self.config['direction_width']
        self.arrow_width = self.config['arrow_width']
        self.radius = self.config['radius']
        self.small_img_size = self.config['small_img_size']
        self.direction_width_big = self.config['direction_width_big']
        self.arrow_width_big = self.config['arrow_width_big']
        self.radius_big = self.config['radius_big']

        # fixme
        self.direction_color = self.config['direction_color']
        self.arrows_color = self.config['arrows_color']
        self.center_color = self.config['center_color']
        self.center_radius = self.config['center_radius']

        self.start_color = self.config['start_color']
        self.start_radius = self.config['start_radius']
        self.start_outline_color = self.config['start_outline_color']
        
        self.end_color = self.config['end_color']
        self.end_radius = self.config['end_radius']
        self.end_outline_color = self.config['end_outline_color']

    def create_map_preview(self, track, img_size=None, track_color=None, track_width=None):

        img_size = self.config["track_size"] if img_size is None else img_size
        track_color = self.config["track_color"] if track_color is None else track_color
        track_width = self.config["track_width"] if track_width is None else track_width
        
        
        mapper = OSMMapper(img_size, cachedir=self.cachedir, unsafe_ssl=self.config["unsafe_ssl"])
        mapper.Debug(self.debug)
        min_pos, max_pos = track.bounds()
        min_lat, min_lon = min_pos
        max_lat, max_lon = max_pos
        NW = gpxpy.geo.Location(max_lat or 0.0, min_lon or 0.0)
        NE = gpxpy.geo.Location(max_lat or 0.0, max_lon or 0.0)
        SE =  gpxpy.geo.Location(min_lat or 0.0, max_lon or 0.0)
        SW =  gpxpy.geo.Location(min_lat or 0.0, min_lon  or 0.0)
        map = mapper.GetMapBB((NW, NE, SE, SW), mapempty=False, bounding_box=False)
        
        if len(track._gpx_points) > 0:
            mapper.ProjectPoints(track._gpx_points, map, color=tuple(track_color), width=track_width)
             
            arrow_width = self.arrow_width
            radius = self.radius
            direction_width = self.direction_width

            if img_size[0] > self.small_img_size: 
                arrow_width = self.arrow_width_big
                radius = self.radius_big
                direction_width = self.direction_width_big
                
                center = track.track_center(as_point=True)
                mapper.ProjectCircle(center, map, color=tuple(self.center_color), radius=self.center_radius)
            
            # clockwise position (height)
            position = (10 + radius, img_size[1] - 10 - radius) 
            
            # 0   -> not clockwise (default, stats)
            # 1   -> clockwise  (default, stats)
            # 2   -> not clockwise (WEB)
            # 3   -> clockwise (WEB)    
            
            cw = track.stats().is_clockwise
            #print "CW: %s, %d" % (cw, track.clockwise)
            
            mapper.ProjectDirection(position, map, cw, color=tuple(self.direction_color), 
                                    radius=radius, width=direction_width)

            mapper.ProjectArrows(track.stats().length_2d, 
                                track._gpx_points, map, color=tuple(self.arrows_color), 
                                width=arrow_width)



            mapper.ProjectCircle(track._gpx_points[0], map, 
                                 color=tuple(self.start_color), 
                                radius=self.start_radius, 
                                outline=tuple(self.start_outline_color))
            mapper.ProjectCircle(track._gpx_points[-1], map, 
                                color=tuple(self.end_color), 
                                radius=self.end_radius, 
                                outline=tuple(self.end_outline_color))
                
        #map.imagemap.save("map.png", 'PNG')
        return map.imagemap