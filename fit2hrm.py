#!/usr/bin/env python3.10
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // app.py 
# //
# // manage the command line app (ingest)
# //
# // 26/11/2024 11:40:36  
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# /////////////////////////////////////////////////////////////////////////////

# creates a quick fix to allow fit2all works (python3 / python2 version)
import argparse
import sys
import traceback
import os.path

from pytrackvis.trackmanager import *
from pytrackvis.helpers import glob_filelist
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count", default=0)
    parser.add_argument("input_file", help="input fit file")
    parser.add_argument("output_dir", help="output dir file (~/Public)")

    args = parser.parse_args()
    tm = TrackManager([args.input_file])

    if not os.path.isdir(args.output_dir):
        print("%s must be a directory. Bailing out" % args.output_dir)
        sys.exit(1)

    try:
        ret = tm.load(optimize_points=False,filter_points=False, only_load=True)
    except Exception as e:
        s = traceback.format_exc()
        print("import_tracks: Can't load %s: %s" % (args.input_file, e))
        sys.exit(0)

    track = tm.track()
    track.convert_to_hrm(args.output_dir)

    