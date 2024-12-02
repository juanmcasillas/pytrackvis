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

from pytrackvis.filemanager_map import *
from pytrackvis.appenv import *
from pytrackvis.mapper import OSMMapper
from pytrackvis.helpers import C, set_proxy,track_similarity, manhattan_point
from pytrackvis.helpers import same_track
import argparse
import os.path 
import json 
import gpxpy


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count", default=0)
    parser.add_argument("-g", "--geojson", help="Export the tracks to geojson files", action="store_true",default=False)
    parser.add_argument("-c", "--config-file", help="Configuration File", default="conf/pytrackvis.json")
    parser.add_argument("files", help="files to read. Can be .fit or .gpxfile", nargs='+')
    args = parser.parse_args()

    AppEnv.config(args.config_file)
    AppEnv.config_set("verbose",args.verbose)


    fm = FileManagerWithMaps(args.files)
    fm.load(optimize_points=True)
    # print(stats.dataframe().transpose().to_html(
    #     justify='center', header=False, index=True, index_names=False, 
    #     col_space=300, classes='table-condensed table-responsive table-success'
    # ))
    #m = fm.create_map()
    #m3d = fm.create_map_3d()
    #m.save("index.html")
    #m3d.to_html("index3D.html")
    if args.geojson:
        for id in fm.tracks.keys():
            track = fm.tracks[id]
            fname = track.fname
            gs = track.as_geojson_line()
            f,ex = os.path.splitext(os.path.basename(fname))
            tgt = "www/%s.gjson" % f
            f = open(tgt, "w")
            f.write(json.dumps(gs["data"]))
            f.close()
            print("Writting %s -> %s" % (fname, tgt))

    
    fm.load_tokens()
    
    
    track_id = list(fm.tracks.keys())[0]
    track = fm.tracks[track_id]
    
    track_id_02 = list(fm.tracks.keys())[1]
    track2 = fm.tracks[track_id_02]
    # check similarity

    print(same_track(track,track2))
    sys.exit(0)

    # create preview for testing 
    set_proxy("http://proxy.senado.es:8080")
    img_size = C(width=800,height=600)
    mapper = OSMMapper(img_size, cachedir="osm_cache")
    mapper.Debug(True)
    bounds = track.bounds()
    min_pos, max_pos = track.bounds()
    min_lat, min_lon = min_pos
    max_lat, max_lon = max_pos
    NW = gpxpy.geo.Location(max_lat or 0.0, min_lon or 0.0)
    NE = gpxpy.geo.Location(max_lat or 0.0, max_lon or 0.0)
    SE =  gpxpy.geo.Location(min_lat or 0.0, max_lon or 0.0)
    SW =  gpxpy.geo.Location(min_lat or 0.0, min_lon  or 0.0)
    map = mapper.GetMapBB((NW, NE, SE, SW), mapempty=False, bounding_box=False)
    
    if len(track.points) > 0:
        mapper.ProjectPoints(track.points, map, color=(255, 0, 0), width=3)
        
        direction_width = 2
        arrow_width = 6
        radius = 8
        if img_size.width > 400: 
            arrow_width = 8
            radius = 20
            direction_width = 3
            
            center = track.track_center(as_point=True)
            mapper.ProjectCircle(center, map, color=(100, 100, 200), radius=2)
        
        position = (10 + radius, img_size.height - 10 - radius) 
        
        # 0   -> not clockwise (default, stats)
        # 1   -> clockwise  (default, stats)
        # 2   -> not clockwise (WEB)
        # 3   -> clockwise (WEB)    
        
        cw = track.stats().is_clockwise
        #print "CW: %s, %d" % (cw, track.clockwise)
        
        mapper.ProjectDirection(position, map, cw, color=(255, 0, 0), 
                                radius=radius, width=direction_width)

        mapper.ProjectArrows(track.stats().length_2d, 
                             track.points, map, color=(240, 10, 10), 
                             width=arrow_width)

        mapper.ProjectCircle(track.points[0], map, color=(10, 180, 10), 
                             radius=3, outline=(10, 100, 10))
        mapper.ProjectCircle(track.points[-1], map, color=(50, 50, 220), 
                             radius=3, outline=(50, 50, 100))   
            
    map.imagemap.save("map.png", 'PNG')

    #b = io.BytesIO()
    #map.imagemap.save(b, 'PNG')
    #data = b.getvalue()
    #cm.Store(cache_data[0], data)
    #request.wfile.write(data)
               

    sys.exit(0)
    m3dml = fm.create_map_3d_maplibre()
    m3dml.to_html("index3DML.html", 
                  overwrite=True, 
                  title="Test MapLibre",
                  replace_key=True)

    
