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
import folium
import folium.plugins
import pydeck
import leafmap.maplibregl as leafmap
from maplibre.plugins import MapboxDrawControls, MapboxDrawOptions
import configparser

from track import Track, TrackPointFit, TrackPointGPX




class FileManager:
    FIT_FILE = ".fit"
    GPX_FILE = ".gpx"
    FILE_EXT = [ FIT_FILE, GPX_FILE ]

    def __init__(self, fname, verbose=0):
        self.file_name = fname
        self.verbose = verbose
        self.FILE_LOADER =  { 
            self.FIT_FILE: self._fit_loader,
            self.GPX_FILE: self._gpx_loader
        }
        self.file_type = self.guess_file_type(self.file_name)

    def guess_file_type(self, fname=None):
        fname = fname if fname else self.file_name
        file_name, file_extension = os.path.splitext(fname)
        file_extension = file_extension.lower()
        if file_extension in self.FILE_EXT:
            return file_extension
        return False

    def load_tokens(self):
        config = configparser.ConfigParser()
        config.read('../data/tokens.ini')

        if not 'MAPTILER_KEY' in config["TOKENS"]:
            print("can't get maptiler token")
            sys.exit(0)
        os.environ["MAPTILER_KEY"] = config["TOKENS"]["MAPTILER_KEY"]

    def _fit_loader(self):

        if self.verbose:
            print("running fit_loader()")

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

        track_points = Track(name=self.file_name)

        with fitdecode.FitReader(self.file_name) as fit:
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


    def _gpx_loader(self):
        if self.verbose:
            print("running gpx_loader()")
       
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
        
        track_points = Track(name=self.file_name)
        with open(self.file_name, 'r') as gpx_file:
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

    def load(self):
        if not self.file_type:
            raise ValueError("file %s has not valid type" % self.file_name)
        loader = self.FILE_LOADER[self.file_type]
        self.track = loader()
        self.track.process()
        return self.track

    def stats(self):
        return self.track.stats()


    def create_map(self):
        
        m = folium.Map(location=self.track.track_center(),tiles=None)
        # add tile layers
        folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
            name="ESRI World Map"
        ).add_to(m)
        folium.TileLayer('openstreetmap', name='OpenStreet Map').add_to(m)

        # add the track, fit to bounds,
        folium.PolyLine(self.track.as_poly(), color='blue', weight=4.5, opacity=.7).add_to(m)
        m.fit_bounds(self.track.bounds())

        #start point
        folium.vector_layers.CircleMarker(
            location=self.track.start_point(), 
            radius=9, 
            color='white', 
            weight=1, fill_color='green', 
            fill_opacity=1).add_to(m) 
        #OVERLAY triangle (green)
        folium.RegularPolygonMarker(
            location=self.track.start_point(), 
            fill_color='white', 
            fill_opacity=1, 
            color='white', number_of_sides=3, 
            radius=3, rotation=0).add_to(m)

        #end point
        folium.vector_layers.CircleMarker(
            location=self.track.end_point(), 
            radius=9, 
            color='white', 
            weight=1, fill_color='red', 
            fill_opacity=1).add_to(m) 
        #OVERLAY square (red)
        folium.RegularPolygonMarker(
            location=self.track.end_point(), 
            fill_color='red', 
            fill_opacity=1, 
            color='white', number_of_sides=4, 
            radius=3, rotation=45).add_to(m)


        stats = self.track.stats()
        html_name = """
        <div align="center">
        <h5><b>Track stats</b></h5><br>
        </div>. """
        html = html_name + "<div align='center'>" + stats.to_html() + "</div>"
        popup = folium.Popup(html, max_width=300)
        folium.Marker(self.track.middle_point(), 
                      popup=popup, 
                      icon=folium.Icon(color="darkblue", 
                                       icon_color='white', 
                                       icon='bicycle', 
                                       prefix='fa')
            ).add_to(m)

        # add layer control, full screen buttons
        folium.LayerControl(collapsed=True).add_to(m)
        folium.plugins.Fullscreen(
            position='topright',
            title='Open Full Screen mode',
            title_cancel='Exit Full Screen mode',
            force_separate_button=True
        ).add_to(m)
        return m

    def create_map_3d(self):
        
        # AWS Open Data Terrain Tiles
        TERRAIN_IMAGE = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"

        # Define how to parse elevation tiles
        ELEVATION_DECODER = {"rScaler": 256, "gScaler": 1, "bScaler": 1 / 256, "offset": -32768}
        SURFACE_IMAGE = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}"

        terrain_layer = pydeck.Layer(
            "TerrainLayer", 
            elevation_decoder=ELEVATION_DECODER, 
            texture=SURFACE_IMAGE, 
            elevation_data=TERRAIN_IMAGE
        )
        stats = self.track.stats()
        data = self.track.dataframe()
        #data['altitude'] = data['altitude'].map(lambda a: a + 10.0)
        print(data.info())
        print(data.head())

        gps_layer = pydeck.Layer(
           'ScatterplotLayer', # 'ColumnLayer',
           data=data,
           get_position= ['position_long', 'position_lat', 'altitude'],
           #get_elevation = 10,
           radius=5,
           #elevation_scale=1,
           #elevation_range=[0, stats.maximum_elevation - stats.minimum_elevation],
           pickable=False,
           #extruded=True,
           #coverage = 1,
           get_fill_color=[100, 100, 255, 220],
           radius_min_pixels = 5,
           radius_max_pixels = 5,
           stroked=False,
           filled=True,
           radius_scale=1,
           min_zoom=8, max_zoom=14
        )


        pos_lat, pos_lon = self.track.middle_point()
        view_state = pydeck.ViewState(
            latitude=pos_lat, longitude=pos_lon, zoom=11.5, bearing=0, pitch=60,
            min_zoom=8, max_zoom=14)
        r = pydeck.Deck(initial_view_state=view_state,
                        layers=[gps_layer, terrain_layer ])
        return r
        # 40.360472      -4.393036     616.2

    def create_map_3d_maplibre(self):
        
        # Load the MAPTILER first Token!
        #stats = self.track.stats()
        #data = self.track.dataframe()
        pos_lon, pos_lat, pos_altitude = self.track.middle_point().pos()
        #lat, long
        m = leafmap.Map(center=[pos_lon, pos_lat], 
                        zoom=14, 
                        pitch=45, 
                        bearing=0, 
                        exaggeration=1.5,
                        controls={},
                        style="3d-hybrid",
                        )

        m.add_basemap("Esri.WorldImagery", visible=False)
        m.add_3d_buildings(min_zoom=10)

        m.add_control("geolocate", position="top-left")
        m.add_control("fullscreen", position="top-right")
        m.add_control("navigation", position="top-left")
        #m.add_layer_control(bg_layers=True)

        def add_line(m, track, line_color = "#4040A0", line_width = 4):
            track_line = track.as_geojson_line()
            layer = {
                "id": "track",
                "type": "line",
                "source": "route",
                "layout": {"line-join": "round", "line-cap": "round"},
                "paint": {"line-color": line_color, "line-width": line_width},
            }
            m.add_source("route", track_line)
            m.add_layer(layer)
            
        def add_point(m, point, id, imageres="marker", imgsize=1):
            
            # watch out the names, because it breaks
            # if you doit wrong.

            if imageres != "marker":
                m.add_image("%s_img" % id, imageres)
            
            point_src = point.as_geojson_point()
            m.add_geojson(point_src["data"], name="point_src_%s_gjson" % id)

            point_layer = {
                
                "id": "%s_point_layer" % id,
                "type": "symbol",
                "source": "point_src_%s" % id,
                "layout": {
                    "icon-image": imageres if imageres == "marker" else "%s_img" % id,
                    "icon-size": imgsize
                },
            }
            m.add_source("point_src_%s" % id, point_src)
            m.add_layer(point_layer)       

        # def add_points(m, points_src, id, imageres="marker", imgsize=1.0):
            
        #     # watch out the names, because it breaks
        #     # if you doit wrong.
        #     if imageres != "marker":
        #         m.add_image("%s_img" % id, imageres)
        #     m.add_geojson(points_src["data"], name="points_src_%s_gjson" % id)

        #     points_layer = {
                
        #         "id": "%s_points_layer" % id,
        #         "type": "symbol",
        #         "source": "points_src_%s" % id,
        #         "layout": {
        #             "icon-image": imageres if imageres == "marker" else "%s_img" % id,
        #             "icon-size": imgsize
        #         },
        #     }
        #     m.add_source("points_src_%s" % id, points_src)
        #     m.add_layer(points_layer)      


        # this only shows the latest layer drawn. I don't know why (overlapping things)
        add_line(m, self.track, line_color="#ffff33")
        #add_point(m, self.track.start_point(), "start", "res/marker-start.png", 1.0)
        #add_point(m, self.track.end_point(), "end", "res/marker-end.png", 1.0)
        m.add_marker(lng_lat = self.track.start_point().pos(), popup={},  options= { "color": "#00AA00"} )
        m.add_marker(lng_lat = self.track.end_point().pos(), popup={}, options= { "color": "#FF0000"})
        #testing this.
        #add_points(m, 
        #           self.track.as_geojson_points([self.track.start_point(), self.track.end_point()]), 
        #           "col", "res/marker-start.png", 
        #           1.0)
      
    
        pos_lon, pos_lat, pos_altitude = self.track.middle_point().pos()
        # to avoid panning
        m.set_center(pos_lon, pos_lat)
        m.fit_bounds(self.track.bounds(lonlat=True))
        return m
        