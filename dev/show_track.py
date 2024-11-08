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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count", default=0)
    parser.add_argument("input_file", help="file to read. Can be .fit or .gpxfile")
    args = parser.parse_args()

    fm = FileManager(args.input_file, args.verbose)
    fm.load()
    # print(stats.dataframe().transpose().to_html(
    #     justify='center', header=False, index=True, index_names=False, 
    #     col_space=300, classes='table-condensed table-responsive table-success'
    # ))
    #m = fm.create_map()
    #m3d = fm.create_map_3d()
    #m.save("index.html")
    #m3d.to_html("index3D.html")
    fm.load_tokens()
    m3dml = fm.create_map_3d_maplibre()
    m3dml.to_html("index3DML.html", 
                  overwrite=True, 
                  title="Test MapLibre",
                  replace_key=True)

