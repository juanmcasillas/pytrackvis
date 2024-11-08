##!/usr/bin/env bash
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // test_maplibre.py 
# //
# // Only works with python 3.11 (packages install)
# // https://geog-312.gishub.org/book/geospatial/maplibre.html
# //
# // 07/11/2024 09:29:06  
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# /////////////////////////////////////////////////////////////////////////////

import leafmap.maplibregl as leafmap
from maplibre.plugins import MapboxDrawControls, MapboxDrawOptions

import os
import configparser
import sys
config = configparser.ConfigParser()
config.read('../data/tokens.ini')

if not 'MAPTILER_KEY' in config["TOKENS"]:
    print("can't get maptiler token")
    sys.exit(0)
os.environ["MAPTILER_KEY"] = config["TOKENS"]["MAPTILER_KEY"]

#lat, long
m = leafmap.Map(center=[-4.392448, 40.360986], 
                zoom=14, pitch=45, bearing=0, style="3d-hybrid",
                exaggeration=1.5,
                controls={})

m.add_basemap("Esri.WorldImagery", visible=False)
m.add_3d_buildings(min_zoom=10)


m.add_control("geolocate", position="top-left")
m.add_control("fullscreen", position="top-right")
m.add_control("navigation", position="top-left")
#m.add_layer_control(bg_layers=True)
m.to_html("leap.html", overwrite=True, title="Test MapLibre", replace_key=True)