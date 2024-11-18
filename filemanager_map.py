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


from filemanager import FileManager

import folium
import folium.plugins
import pydeck
import leafmap.maplibregl as leafmap
from maplibre.plugins import MapboxDrawControls, MapboxDrawOptions


from track import Track, TrackPointFit, TrackPointGPX
from appenv import AppEnv



class FileManagerWithMaps(FileManager):
    FIT_FILE = ".fit"
    GPX_FILE = ".gpx"
    FILE_EXT = [ FIT_FILE, GPX_FILE ]

    def __init__(self, fnames):
        super(FileManager, self).__init__(fnames)

    def load_tokens(self):
        tokens = configparser.ConfigParser()
        tokens.read(AppEnv.config().api_key_file)
        print(dir(tokens), AppEnv.config().api_key_file)
        if not 'TOKENS' in tokens.keys() or not 'MAPTILER_KEY' in tokens["TOKENS"]:
            print("can't get maptiler token")
            sys.exit(0)
        os.environ["MAPTILER_KEY"] = tokens["TOKENS"]["MAPTILER_KEY"]

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

        #pos_lon, pos_lat, pos_altitude = self.track.middle_point().pos()
        #lat, long
        m = leafmap.Map(#center=[pos_lon, pos_lat], 
                        zoom=14, 
                        pitch=45, 
                        bearing=0, 
                        exaggeration=1.5,
                        controls={},
                        style="3d-hybrid",
                        )

        m.add_basemap("Esri.WorldImagery", visible=True)
        m.add_3d_buildings(min_zoom=10)
        m.add_control("geolocate", position="top-left")
        m.add_control("fullscreen", position="top-right")
        m.add_control("navigation", position="top-left")
        m.add_control("scale", position="top-left")


        def add_line(m, track, line_color = "#4040A0", line_width = 4, id="track"):
            track_line = track.as_geojson_line()
            layer = {
                "id": id,
                "type": "line",
                "source": "route_%s" % id,
                "layout": {"line-join": "round", "line-cap": "round"},
                "paint": {"line-color": line_color, "line-width": line_width},
            }
            m.add_source("route_%s" % id, track_line)
            m.add_layer(layer)
            
        # def add_point(m, point, id, imageres="marker", imgsize=1):
            
        #     # watch out the names, because it breaks
        #     # if you doit wrong.

        #     if imageres != "marker":
        #         m.add_image("%s_img" % id, imageres)
            
        #     point_src = point.as_geojson_point()
        #     m.add_geojson(point_src["data"], name="point_src_%s_gjson" % id, visible=False)

        #     point_layer = {
        #         "id": "%s_point_layer" % id,
        #         "type": "symbol",
        #         "source": "point_src_%s" % id,
        #         "layout": {
        #             "icon-image": imageres if imageres == "marker" else "%s_img" % id,
        #             "icon-size": imgsize
        #         },
        #     }
        #     m.add_source("point_src_%s" % id, point_src)
        #     m.add_layer(point_layer)       

        # def add_points(m, points_src, id, imageres="marker", imgsize=1.0):
            
        #     # watch out the names, because it breaks
        #     # if you doit wrong.
        #     if imageres != "marker":
        #         m.add_image("%s_img" % id, imageres)
        #     m.add_geojson(points_src["data"], name="points_src_%s_gjson" % id,  visible=False)

        #     points_layer = {
                
        #         "id": "%s_points_layer" % id,
        #         "type": "symbol",
        #         "source": "points_src_%s" % id,
        #         "layout": {
        #              "icon-image": imageres if imageres == "marker" else "%s_img" % id,
        #              "icon-size": imgsize
        #         },
        #     }
        #     m.add_source("points_src_%s" % id, points_src)
        #     m.add_layer(points_layer,before_id='track')


        # this only shows the latest layer drawn. I don't know why (overlapping things)
      
        #add_point(m, self.track.start_point(), "start", "res/marker-start.png", 1.0)
        #add_point(m, self.track.end_point(), "end", "res/marker-end.png", 1.0)
        #testing this.
        #add_points(m, 
        #           self.track.as_geojson_points([self.track.start_point(), self.track.end_point()]), 
        #           "col", "res/marker-start.png", 
        #           1.0)

        min_lat = min_long = 99999.0
        max_lat = max_long = -99999.0

        COLORS = ["#ffff33", "#33ffff", "#ff33ff", "#DDDD44" ,"#44DDDD", "#DD44DD" ]

        for fname in self.file_names:
            
            track = self.tracks[fname]
            random_color = random.choice(COLORS)
            add_line(m, track, line_color=random_color, id=fname)
            m.add_marker(lng_lat = track.start_point().pos(), popup={},  options= { "color": "#00AA00"} )
            m.add_marker(lng_lat = track.end_point().pos(), popup={}, options= { "color": "#FF0000"})
        
            pos_lon, pos_lat, pos_altitude = track.middle_point().pos()
            tmin, tmax = track.bounds(lonlat=True)
            tmin_long, tmin_lat = tmin 
            tmax_long, tmax_lat = tmax
            
            if tmin_lat < min_lat:
                min_lat = tmin_lat
            if tmin_long < min_long:
                min_long = tmin_long

            if tmax_lat > max_lat:
                max_lat = tmax_lat
            if tmax_long > max_long:
                max_long = tmax_long

        # to avoid panning
        m.add_layer_control(bg_layers=False)
        m.set_center(pos_lon, pos_lat)
        print("bounds:", min_long, min_lat, max_long, max_lat)
        m.fit_bounds([[min_long, min_lat], [max_long, max_lat]]) # this must be the max.
        return m
        