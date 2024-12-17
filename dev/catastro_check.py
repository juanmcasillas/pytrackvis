#!/usr/bin/env python
# coding=latin-1
#
# ^^^ Put this in order to suppor the Latin-1 encoding of the Catastro XML data

import os.path
import argparse
import glob
import sys
import os
import copy

sys.path.append('E:\\Dropbox\\ArPyRo\\hrm')
sys.path.append('/Volumes/Depot/Dropbox/ArPyRo/hrm')
sys.path.append('/users/jmc/Dropbox/ArPyRo/hrm')


from polar.gpxpy.utils import point_inside_polygon
from polar.gpxpy.optimizer import *
from polar.gpxtoolbox import *
from polar.mapper import *
from  catastro import *
from decimal import *


if __name__ == "__main__":

    #CHECK_LINE()
    #CHECK_POLY()

    parser = argparse.ArgumentParser()
    parser.add_argument("gpx_file", help="GPX File to be processed")
    parser.add_argument("output_file", help="KML output file")
    parser.add_argument("gpx_waypoint_db", help="GPX Waypoint DB File (Doors, etc)")
    
    args = parser.parse_args()

    gpx = GPXItem()
    gpx.Load(args.gpx_file)
    gpx.MergeAll()

    gpx_wp = GPXItem()
    gpx_wp.Load(args.gpx_waypoint_db)
    print gpx.Print()


    # copy all
    #all_points = list(gpx.gpx.tracks[0].segments[0].points)

    # you should adjust resolution to AVOID false negatives
    # and too MUCH querying the catastro WS.
    # Using a simplify(5) should work

    # use the IN_Poly function to save data and get acurrate results

    #gpx.gpx.reduce_points(min_distance=5)
    #gpx.gpx.simplify(5) #default is 10

    #gpx_optmizer = GPXOptimizer()
    #opt_points = gpx_optmizer.Optimize(gpx.gpx.tracks[0].segments[0].points)
    #gpx_optmizer.Print_stats()
    #gpx.gpx.tracks[0].segments[0].points = opt_points

    #fd = open("xxx.gpx","w+")
    #fd.write(gpx.to_xml())
    #fd.close()
    #sys.exit(0)
    ## end of dev code

    catastro = CatastroManager()
    polygons = {}
    polygons_ordered = []

    last_polygon = None

    kml_segments = []
    kml_segment = []
    debug_segments = False
    segstate = "out"
    segkind = False
    segment = []

    #for point in
    for pindex in range(len(gpx.gpx.tracks[0].segments[0].points)):

        point = gpx.gpx.tracks[0].segments[0].points[pindex]

        # check if the point is inside the poly, or what
        # if we have stored polys, try if we are inside. If not, work on

        rc = None
        cached = False

        if last_polygon:

            pcoords = last_polygon[1] # coords

            #msg, coords, ccc, cdc, info, point, rc = last_poly


            if point_inside_polygon(point, pcoords):

                msg, coords, ccc, cdc, info, point, rc = last_polygon
                msg = msg + "[POLY]"
                cached = True

        # if data is not cached by previous polygon,
        # then ask for things.

        if not cached:

            rc = catastro.GetRC((point.longitude, point.latitude))
            ccc = None      # code of land
            cdc = None      # description

            if not rc:
                msg =  "%f,%f DOMINIO PUBLICO (carretera, calle, etc.)" % (point.latitude, point.longitude)
                ccc = "DPU" # Dominio Public Use
                cdc = "DOMINIO PUBLICO"
            else:

                # ask for RC data. Note about agregates, and so on.

                info = catastro.GetInfo(rc)

                ccc = info.calificacion_catastral or None # desconocido
                cdc = info.denominacion_clase or None

                if info.calificacion_catastral and info.denominacion_clase:
                    #e.g VT, vias publicas
                    ccc = info.calificacion_catastral
                    cdc = info.denominacion_clase

                if info.domicilio_tributario:
                    ccc = ccc or "PRI"
                    cdc = info.domicilio_tributario

                if not info.domicilio_tributario and info.nombre_via:
                    ccc = info.codigo_via
                    cdc = info.nombre_via

                if not cdc and info.nombre_paraje: cdc = info.nombre_paraje

                if not ccc: ccc = "DES"
                if not cdc: cdc = "DESCONOCIDO"

                msg =  "[%s] %f,%f %s(%s) {%s} %s" % (rc, point.latitude, point.longitude,  info.nombre_provincia, info.nombre_municipio, ccc, cdc)

                coords = catastro.getRCCoords(rc)
                if coords:
                    if not rc in polygons.keys():
                        polygons[rc] = msg
                        polygons_ordered.append([msg, coords, ccc, cdc, info, point, rc])

                    last_polygon = [msg, coords, ccc, cdc, info, point, rc]

        # ANALIZE BY CATEGORY and STATE.
        if not debug_segments:
            print "N] ",msg.encode('ASCII','xmlcharrefreplace')

        # add fields

        gpx.gpx.tracks[0].segments[0].points[pindex].catastro = EmptyClass()
        gpx.gpx.tracks[0].segments[0].points[pindex].catastro.isPrivate = False
        gpx.gpx.tracks[0].segments[0].points[pindex].catastro.rc = rc
        gpx.gpx.tracks[0].segments[0].points[pindex].catastro.ccc = ccc
        gpx.gpx.tracks[0].segments[0].points[pindex].catastro.cdc = cdc

        if not catastro.isPublic(rc):
             gpx.gpx.tracks[0].segments[0].points[pindex].catastro.isPrivate = True

        # process segments
        # if same state
        
        p = gpx.gpx.tracks[0].segments[0].points[pindex]
        
        if segstate == "out":
            segstate = "in"
            segkind = p.catastro.isPrivate
            segment.append(p)
            if debug_segments: print "IN ", p.catastro.rc, p.catastro.ccc, p.catastro.cdc, segkind
            continue

        if segstate == "in" and p.catastro.isPrivate != segkind:
            segstate = "out"
            
            p2 = copy.copy(p)
            p2.catastro.isPrivate = segkind
            
            segkind = p.catastro.isPrivate
            
            # copy the point avoid skip gaps.
            segment.append(p2)
            kml_segments.append(( segment[-1].catastro.rc, segment[-1].catastro.ccc, segment[-1].catastro.cdc, segment[-1].catastro.isPrivate, segment ))
            segment = []
            segment.append(p)
            if debug_segments: print "OUT", p.catastro.rc, p.catastro.ccc, p.catastro.cdc, segkind
            continue

        if segstate == "in" and p.catastro.isPrivate == segkind:
            segment.append(p)
            if debug_segments: print "---", p.catastro.rc, p.catastro.ccc, p.catastro.cdc, segkind
            continue

    # if there is something in the segment add it
    if segstate == "in" and len(segment) > 0:
        kml_segments.append(( segment[-1].catastro.rc, segment[-1].catastro.ccc, segment[-1].catastro.cdc, segment[-1].catastro.isPrivate, segment ))
        if debug_segments: print "OUT", segment[-1].catastro.rc, segment[-1].catastro.ccc, segment[-1].catastro.cdc, segkind
    

    ###
    ### create a valid KML file here.
    ###

    kmlfile = KMLFile(os.path.basename(args.gpx_file), gpx.gpx.tracks[0].segments[0].points[0],  args.output_file)

    # full track
    kml = kmlfile.GPX2KMLPlacemark(gpx.gpx.tracks[0].segments[0].points,
                                       gname=os.path.basename(args.gpx_file),
                                       gdesc="Ruta GPX Recorrida", style="gpxtrack")



    
    count_public = 1
    count_private = 1
    kml_public = ""
    kml_private = ""

    for sitem in kml_segments:
        rc, ccc, cdc, isprivate, segment = sitem

        style = "gpxtrackpublic"
        count = count_public

        if isprivate:
            style = "gpxtrackprivate"
            count = count_private

        gpx2kml = kmlfile.GPX2KMLPlacemark(segment,
                                           gname="#%d[%s]" % (count, rc or "DOMINIO PUBLICO"),
                                           gdesc="%s: %s" % (ccc, cdc), style=style)
        count_public += 1
        count_private += 1

        if isprivate:
            kml_private += gpx2kml
        else:
            kml_public += gpx2kml


    kml += "<Folder><name>Segmentos GPX Publicos</name>"
    kml += kml_public
    kml += "</Folder>"

    kml += "<Folder><name>Segmentos GPX Privados</name>"
    kml += kml_private
    kml += "</Folder>"

    # add waypoint info

    kml += kmlfile.GPXWP2Kml(gpx_wp.gpx.waypoints)



    ##kmlfile.Create(sorted(polygons_ordered.values(), key=lambda s: s[7]), kml)
    kmlfile.Create(polygons_ordered, kml)

    #fout = open("output.kml","w")
    #fout.write(os.linesep.join(polygons.values()))
    #fout.close()

    catastro.cache.PrintStats()
