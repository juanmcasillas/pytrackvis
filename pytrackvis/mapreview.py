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
    def __init__(self, cachedir="osm_cache", debug=True):
        self.cachedir = cachedir
        self.debug = debug

        # for compute the clockwise image.
        self.direction_width = 2
        self.arrow_width = 6
        self.radius = 8
        self.small_img_size = 400
        self.direction_width_big = 3
        self.arrow_width_big = 8
        self.radius_big = 20

        # fixme
        self.direction_color = (255, 0, 0)
        self.arrows_color = (240, 10, 10)
        self.center_color = (100, 100, 200)
        self.center_radius = 2

        self.start_color = (10, 180, 10)
        self.start_radius = 3
        self.start_outline_color = (10, 100, 10)
        
        self.end_color = (50, 50, 220)
        self.end_radius = 3
        self.end_outline_color = (50, 50, 100)

    def create_map_preview(self, track, img_size, track_color, track_width):

        #img_size = C(width=800,height=600)
        mapper = OSMMapper(img_size, cachedir=self.cachedir)
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
            mapper.ProjectPoints(track._gpx_points, map, color=track_color, width=track_width)
             
            arrow_width = self.arrow_width
            radius = self.radius
            direction_width = self.direction_width

            if img_size.width > self.small_img_size: 
                arrow_width = self.arrow_width_big
                radius = self.radius_big
                direction_width = self.direction_width_big
                
                center = track.track_center(as_point=True)
                mapper.ProjectCircle(center, map, color=self.center_color, radius=self.center_radius)
            
            # clockwise position
            position = (10 + radius, img_size.height - 10 - radius) 
            
            # 0   -> not clockwise (default, stats)
            # 1   -> clockwise  (default, stats)
            # 2   -> not clockwise (WEB)
            # 3   -> clockwise (WEB)    
            
            cw = track.stats().is_clockwise
            #print "CW: %s, %d" % (cw, track.clockwise)
            
            mapper.ProjectDirection(position, map, cw, color=self.direction_color, 
                                    radius=radius, width=direction_width)

            mapper.ProjectArrows(track.stats().length_2d, 
                                track._gpx_points, map, color=self.arrows_color, 
                                width=arrow_width)



            mapper.ProjectCircle(track._gpx_points[0], map, 
                                 color=self.start_color, 
                                radius=self.start_radius, 
                                outline=self.start_outline_color)
            mapper.ProjectCircle(track._gpx_points[-1], map, 
                                color=self.end_color, 
                                radius=self.end_radius, 
                                outline=self.end_outline_color)   
                
        #map.imagemap.save("map.png", 'PNG')
        return map.imagemap