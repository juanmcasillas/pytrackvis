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
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count", default=0)
    parser.add_argument("input_file", help="file to read. Can be .fit or .gpxfile")
    args = parser.parse_args()

    fm = FileManager(args.input_file, args.verbose)
    fm.load()
    #fm.track.pprint()
    #print(fm.track.dict())

    data = pd.DataFrame(fm.as_dict())
    print(data.info())
    print(data.head())
    sys.exit(0)

