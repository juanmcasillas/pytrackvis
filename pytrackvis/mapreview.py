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
        self.direction_width = self.config['direction_width'] if 'direction_width' in self.config else 0
        self.arrow_width = self.config['arrow_width'] if 'arrow_width' in self.config else 0
        self.radius = self.config['radius'] if 'radius' in self.config else 0
        self.small_img_size = self.config['small_img_size'] if 'small_img_size' in self.config else 0
        self.direction_width_big = self.config['direction_width_big'] if 'direction_width_big' in self.config else 0
        self.arrow_width_big = self.config['arrow_width_big'] if 'arrow_width_big' in self.config else 0
        self.radius_big = self.config['radius_big'] if 'radius_big' in self.config else 0 

        # fixme
        self.direction_color = self.config['direction_color'] if 'direction_color' in self.config else 0
        self.arrows_color = self.config['arrows_color'] if 'arrows_color' in self.config else 0 
        self.center_color = self.config['center_color'] if 'center_color' in self.config else 0 
        self.center_radius = self.config['center_radius'] if 'center_radius' in self.config else 0

        self.start_color = self.config['start_color'] if 'start_color' in self.config else 0
        self.start_radius = self.config['start_radius'] if 'start_radius' in self.config else 0
        self.start_outline_color = self.config['start_outline_color'] if 'start_outline_color' in self.config else 0
        
        self.end_color = self.config['end_color'] if 'end_color' in self.config else 0 
        self.end_radius = self.config['end_radius'] if 'end_radius' in self.config else 0
        self.end_outline_color = self.config['end_outline_color'] if 'end_outline_color' in self.config else 0

    def create_map_preview(self, track, img_size=None, track_color=None, track_width=None, empty_map=False, zoom_level=None):

        img_size = self.config["track_size"] if img_size is None and 'track_size' in self.config else img_size
        track_color = self.config["track_color"] if track_color is None  and 'track_color' in self.config else track_color
        track_width = self.config["track_width"] if track_width is None  and 'track_width' in self.config else track_width
        
        mapper = OSMMapper(img_size, 
                           cachedir=self.cachedir, 
                           unsafe_ssl=self.config["unsafe_ssl"] if "unsafe_ssl" in self.config else False)
        mapper.Debug(self.debug)

        map = mapper.GetMapBB(track.bounds(), mapempty=empty_map, bounding_box=False, zoom_base=zoom_level)

        if len(track.points) > 0:
            mapper.ProjectPoints(track.points, 
                                 map, 
                                 color=tuple(track_color), 
                                 width=track_width,
                                 use_gradient = self.config["use_gradient"] if 'use_gradient' in self.config else False,
                                 gradient_value= self.config["gradient_value"] if 'gradient_value' in self.config else 0,
                                 draw_bar = self.config["draw_bar"],
                                 elevation_extremes=track._gpx.get_elevation_extremes()
                                 )
            
            if self.config["draw_ccw"]:
                arrow_width = self.arrow_width
                radius = self.radius
                direction_width = self.direction_width

                if img_size[0] > self.small_img_size: 
                    arrow_width = self.arrow_width_big
                    radius = self.radius_big
                    direction_width = self.direction_width_big
                
                if self.config["draw_center"]:
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
                                    track.points, map, color=tuple(self.arrows_color), 
                                    width=arrow_width)


            if self.config["draw_startstop"]:
                mapper.ProjectCircle(track.points[0], map, 
                                    color=tuple(self.start_color), 
                                    radius=self.start_radius, 
                                    outline=tuple(self.start_outline_color))
                mapper.ProjectCircle(track.points[-1], map, 
                                    color=tuple(self.end_color), 
                                    radius=self.end_radius, 
                                    outline=tuple(self.end_outline_color))
                
        #map.imagemap.save("map.png", 'PNG')
        return map.imagemap