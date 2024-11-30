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

from pytrackvis.appenv import *
from pytrackvis.manager import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count", default=0)
    parser.add_argument("-c", "--config-file", help="Configuration File", default="conf/pytrackvis.json")

    subparsers = parser.add_subparsers(title="commands", dest="command")
    create_db_parser = subparsers.add_parser("create_db",help="creates the database")
    create_db_parser.set_defaults(command="create_db")

    import_files_parser = subparsers.add_parser("import_files",
                                               help="Import files from different locations", 
                                               )
    import_files_parser.set_defaults(command="import_files")
    import_files_parser.add_argument("files",help="fit or gpx files", nargs='+')


    similarity_parser = subparsers.add_parser("check_similarity",help="Computes similarity on the DB")
    similarity_parser.set_defaults(command="check_similarity")

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

    if args.command == "import_files":
        subargs = import_files_parser.parse_args()
        manager.import_files(subargs.files)
        sys.exit(0)

    if args.command == "check_similarity":
        manager.check_similarity()
        sys.exit(0)

    manager.shutdown()
