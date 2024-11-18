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

from filemanager import *
from appenv import *
import os.path 
import json 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count", default=0)
    parser.add_argument("-g", "--geojson", help="Export the tracks to geojson files", action="store_true",default=False)
    parser.add_argument("-c", "--config-file", help="Configuration File", default="conf/pytrackvis.json")
    parser.add_argument("files", help="files to read. Can be .fit or .gpxfile", nargs='+')
    args = parser.parse_args()

    AppEnv.config(args.config_file)
    AppEnv.config_set("verbose",args.verbose)

    fm = FileManager(args.files)
    fm.load()
    # print(stats.dataframe().transpose().to_html(
    #     justify='center', header=False, index=True, index_names=False, 
    #     col_space=300, classes='table-condensed table-responsive table-success'
    # ))
    #m = fm.create_map()
    #m3d = fm.create_map_3d()
    #m.save("index.html")
    #m3d.to_html("index3D.html")
    if args.geojson:
        for fname in fm.file_names:
            track = fm.tracks[fname]
            gs = track.as_geojson_line()
            f,ex = os.path.splitext(os.path.basename(fname))
            tgt = "www/%s.gjson" % f
            f = open(tgt, "w")
            f.write(json.dumps(gs["data"]))
            f.close()
            print("Writting %s -> %s" % (fname, tgt))

    
    fm.load_tokens()
    m3dml = fm.create_map_3d_maplibre()
    m3dml.to_html("index3DML.html", 
                  overwrite=True, 
                  title="Test MapLibre",
                  replace_key=True)

    
