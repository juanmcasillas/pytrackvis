import sys
sys.path.append('..')
import pytrackvis.catastro as catastro 
import argparse
import pprint 
import json

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("lat", help="Latitude")
    parser.add_argument("lon", help="Longitude")
    parser.add_argument("output_file", help="Output file")
    
    args = parser.parse_args()

    cm = catastro.CatastroManager("../cache/catastro", unsafe_ssl=True)

    point, polys = cm.check_point(args.lat, args.lon)
    print(point)
    for  poly in polys:
        print("---")
        for i in poly.keys():
            print("%s: %s" % (i, poly[i]))
    ###
    ### create a valid KML file here.1
    ###

    print("-" * 80 )
    point, geojson = cm.check_point_as_geojson(args.lat, args.lon)
    print(point)
    print(json.dumps(geojson))