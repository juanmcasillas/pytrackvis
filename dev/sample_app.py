##!/usr/bin/env python
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // test_fitdecode.py 
# //
# // run some test on teest_fitdecode library
# //
# // 23/10/2024 08:46:32  
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
    m = fm.create_map()
    m3d = fm.create_map_3d()
    m.save("index.html")
    m3d.to_html("index3D.html")
