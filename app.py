##!/usr/bin/env bash
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

import argparse
import sys

import pytrackvis.timing
from pytrackvis.appenv import *
from pytrackvis.manager import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count", default=0)
    parser.add_argument("-c", "--config-file", help="Configuration File", default="conf/pytrackvis.json")


    subparsers = parser.add_subparsers(title="commands", dest="command")
    
    create_db_parser = subparsers.add_parser("create_db",help="creates the database")
    create_db_parser.set_defaults(command="create_db")

    import_tracks_parser = subparsers.add_parser("import_tracks",
                                               help="Import files from different locations", 
                                               )
    import_tracks_parser.set_defaults(command="import_tracks")
    import_tracks_parser.add_argument("files",help="fit or gpx files", nargs='+')

    similarity_parser = subparsers.add_parser("check_similarity",help="Computes similarity on the DB")
    similarity_parser.set_defaults(command="check_similarity")

    list_parser = subparsers.add_parser("list_tracks",help="Show imported tracks")
    list_parser.set_defaults(command="list_tracks")

    fix_time_parser = subparsers.add_parser("fix_time",
                                               help="Fix the time adding 1s on each point. Dump the same as gpx, fixed"
                                               )
    fix_time_parser.set_defaults(command="fix_time")
    fix_time_parser.add_argument("file",help="fit or gpx files", nargs=1)

    import_places_parser = subparsers.add_parser("import_places",
                                               help="Import places from different locations"
                                               )
    import_places_parser.set_defaults(command="import_places")
    import_places_parser.add_argument("category",help="string with category")
    import_places_parser.add_argument("files",help="kml or gpx files", nargs='+')


    check_catastro_parser = subparsers.add_parser("check_catastro", 
                                                  help="Check the track with the catastro, get all the polys")
    check_catastro_parser.set_defaults(command="check_catastro")
    check_catastro_parser.add_argument("trackid", help="id of the track being processed")
    

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()            
        sys.exit(0)

    AppEnv.config(args.config_file)
    AppEnv.config_set("verbose",args.verbose)


    manager = Manager(AppEnv.config())
    manager.startup()
    if args.command == "create_db":
        manager.create_database()
        sys.exit(0)

    if args.command == "import_tracks":
        subargs = import_tracks_parser.parse_args()
        # remove the current command in the args.
        manager.import_tracks(subargs.files[1:])
        sys.exit(0)

    if args.command == "check_similarity":
        manager.check_similarity()
        sys.exit(0)

    if args.command == "list_tracks":
        manager.list_tracks()
        sys.exit(0)

    if args.command == "fix_time":
        subargs = import_tracks_parser.parse_args()
        manager.fix_time(subargs.files[1:])
        sys.exit(0)

    if args.command == "import_places":
        subargs = import_tracks_parser.parse_args()
        category = subargs.files[1]
        files = subargs.files[2:]
       
        # remove the current command in the args.
        manager.import_places(category, files)
        sys.exit(0)

    if args.command == "check_catastro":
        ##subargs = check_catastro_parser.parse_args()
        manager.check_track_in_catastro(args.trackid)
        sys.exit(0)

    manager.shutdown()
