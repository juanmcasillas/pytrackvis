# coding=utf-8

import sys

sys.path.append('E:\\Dropbox\\ArPyRo\\hrm')
sys.path.append('/Volumes/Depot/Dropbox/ArPyRo/hrm')

from polar.gpxpy import geo
from polar.gpxpy.optimizer import *
from polar.gpxtoolbox import *
import rainbowvis
import slopes

class KML:
    def __init__(self, route_name, outputname=None):
        self.route_name = route_name
        self.outputname = outputname
        self.colors = []

    def Create(self, gpx="", polygons=None):

        header = self._genHeader(self.route_name, polygons)

        data = ""

        if polygons:
            for item in polygons:

                (msg, coords, ccc, cdc, info, point, rc) = item

                #
                # build a well formed message and description
                #

                curl = "https://www1.sedecatastro.gob.es/OVCFrames.aspx?TIPO=CONSULTA"

                pname = "<![CDATA[<b>RC[%s]</b></br>%s(%s)</br>CC: %s</br>]]>" %\
                 (rc, info.nombre_provincia, info.nombre_municipio,ccc)

                pdesc = "<![CDATA[%s</br>Paraje: %s</br></br><a href='%s'>Web Catastro</a>]]>" %(cdc, info.nombre_paraje or "-", curl)

                pdata = self._genKMLPolygon(rc, coords, pname, pdesc, ccc)
                data += pdata


        data += gpx

        data = header + data + self._genFooter()

        if self.outputname:
            fout = open(self.outputname,"w")
            fout.write(data)
            fout.close()

        return data



    def GPXWP2Kml(self, waypoints, style="gpxwaypoint", extdata=None, extdesc=True):

            wpkml = """
              <Placemark>
                <name>{name}</name>
                <description>{description}</description>
                <styleUrl>#{style}</styleUrl>
                <Point>
                  <extrude>0</extrude>
                  <altitudeMode>clampToGround</altitudeMode>
                  <coordinates>{longitude},{latitude}</coordinates>
                </Point>
                {extendeddata}
              </Placemark>
              """
            
            extkml = """
                <ExtendedData>
                    <Data name=\"placeid\"><value>{placeid}</value></Data>
                    <Data name=\"{name}\"><value>{value}</value></Data>
                </ExtendedData>
            """

            if len(waypoints) == 0:
                return ""

            ## no folder
            ## r_kml = "<Folder><name>Puertas - Candados - Vallas</name>"
            r_kml = ""
            for wp in waypoints:
                
                r_extkml = ""
                if extdata != None:
                    r_extkml = extkml.format(name=extdata, value=wp.__dict__[extdata], placeid=wp.id)
                    # special points (with extended info)
                    if extdesc:
                        d = "<![CDATA[<i>(%d tracks)</i></br>%s</br></br><a href='/place/view?id=%d'>More Details</a> | <a href='#' onclick='AddPlaceToTrack(*TRACK_ID*,%d)'>Add to Track</a></br></br>]]>" % (wp.ntracks, wp.description, wp.id,wp.id) 
                    else:
                        d = "<![CDATA[<i>(%d tracks)</i></br>%s</br></br><a href='/place/view?id=%d'>More Details</a></br></br>]]>" % (wp.ntracks, wp.description, wp.id)
                        
                else:
                    # normal waypoints gpx
                    d = "<![CDATA[%s</br></br></br>]]>" % (wp.description) 
                
                
                r_kml += wpkml.format(style=style,
                                      name=wp.name.encode('ASCII','xmlcharrefreplace'),
                                      description=d.encode('ASCII','xmlcharrefreplace'),
                                      longitude=wp.longitude, latitude=wp.latitude,
                                      extendeddata=r_extkml)

            ##r_kml += "</Folder>"
            return r_kml

    def AddColor(self,color):
        if color not in self.colors:
            self.colors.append(color)
            
        
        
    def GPX2KMLPlacemark(self, points, style="gpxtrack", gname="GPX track name", gdesc="GPX Track description"):
        """
        create a Placemark KML compliant value.
        """

        placemark = """
                    <Placemark>
                    <visibility>1</visibility>
                    <open>0</open>
                    <styleUrl>#{style}</styleUrl>
                    <name>{gname}</name>
                    <description>{gdesc}</description>
                    <LineString>
                        <extrude>true</extrude>
                        <tessellate>true</tessellate>
                        <altitudeMode>clampToGround</altitudeMode>
                        <coordinates>
                            {coordinates}
                        </coordinates>
                    </LineString>
                </Placemark>
        """

        coordinates = []
        for p in points:

            # skip bad-ass points (lat=0, lon=0, and this piece o shits)

            if p.longitude != 0.0 and p.latitude != 0.0:
                coordinates.append( ",".join([ str(p.longitude), str(p.latitude), str(p.elevation)]))

        coordinates = " ".join(coordinates)

        return placemark.format(style=style,
                                gname=gname.encode('ASCII','xmlcharrefreplace'),
                                gdesc=gdesc.encode('ASCII','xmlcharrefreplace'),
                                coordinates=coordinates)



    def _genStyles(self):

        # add special styles.

        s = """<Style id="gpxtrack">
            <LineStyle>
                <color>FFFF0000</color>
                <width>3</width>
            </LineStyle>
            </Style>

            <Style id="gpxwaypoint">
              <IconStyle>
                <scale>0.7</scale>
                <Icon>
                  <href>http://maps.google.com/mapfiles/kml/pal3/icon45.png</href>
                </Icon>
              </IconStyle>
            </Style>

            <Style id="trackplace">
              <IconStyle>
                <scale>0.7</scale>
                <Icon>
                  <href>http://maps.google.com/mapfiles/kml/pal3/icon29.png</href>
                </Icon>
              </IconStyle>
            </Style>

        """
        #<href>http://maps.google.com/mapfiles/kml/pal3/icon34.png</href>

        ctpl = """<Style id="%s">
            <LineStyle>
                <color>FF%s</color>
                <width>3</width>
            </LineStyle>
            </Style>
            """
        
        colors = ""
        for c in self.colors:
            colors += ctpl % (c, c)
        
        return s + colors

    def _genStyles_poly(self):
        styles = {}
        # colors: #AAbbggrr

        styles['C-']      = "7033cccc" #LABOR O LABRADO SECANO
        styles['E-']      = "7066ffff" #PASTOS
        styles['O-']      = "7066AAAA" #OLIVOS DE SECANO
        styles['FE']      = "70336600" #ENCINAR
        styles['FC']      = "60448000" #ENCINAR
        styles['HC']      = "70900010" #HIDROGRAFA CONSTRUIDA
        styles['HG']      = "70A00010" #HIDROGRAFA NATURAL
        styles['I-']      = "70303080" #IMPRODUCTIVO
        styles['MB']      = "7033cc66" #MONTE BAJO
        styles['PD']      = "7000cc66" #PRADOS O PRADERAS
        styles['CR']      = "7000EE90" #LABOR O REGADIO
        styles['FR']      = "7000FFA0" #FRUTALES REGADIO
        styles['V-']      = "70006699" #VID SECANO
        styles['VT']      = "70406020" #VIA DE COMUNICACION DE DOMINIO PUBLICO
        styles['VO']      = "7000AA99" #VIÑA OLIVAR SECANO
        styles['MM']      = "7030AA90" #PINAR MADERABLE
        styles['MP']      = "7030AAAA" #PINAR PINEA O DE FRUTO
        styles['NC']      = "7066f090" #PARAJE
        styles['MR']      = "7066f040" #PARAJE
        styles['CE']      = "7044f020" #PARAJE

        styles['123']     = "70907060" # RECOLETOS
        styles['127']     = "70907060" # RECOLETOS
        styles['270']     = "70557580" # DELESPINO
        styles['10']      = "70407080" # CORREDERA
        styles['12']      = "70506070" # HOSPITAL
        styles['36']      = "70506070" # HOSPITAL
        styles['50']      = "70407080" # MARTIRES DE EL TIEMBLO
        styles['35']      = "70407080" # GENERALISIMO FRANCO
        styles['RI']      = "70805070" #
        styles['PR']      = "70807080" #
        styles['HR']      = "7040BBCC" #UMBRIA - SEVILLA
        styles['EU']      = "7040A0D0" #REHOYO - SEVILLA
        styles['FS']      = "7040A0D0" #REHOYO - SEVILLA

        styles['11']      = "60337070" # EXTRARRADIO
        styles['9']      = "70902070" #FUENTE NUEVA
        styles['2']      = "70902070" #CONCEPCION
        styles['13']      = "70902070" #IGLESIA
        styles['20']      = "70667070" #TENERIA
        styles['47']      = "70667070" #EXTRARRADIO
        styles['F-']      = "70667070" #EXTRARRADIO
        styles['MT']      = "70667070" #EXTRARRADIO
        styles['PR']      = "70667070" #EXTRARRADIO
        styles['80']      = "70667070" #EXTRARRADIO
        styles['EE']      = "70669090" #PASTOS CON ENCINAS
        styles['MF']      = "7022AA55" #ESPECIES MEZCLADAS
        styles['FF']      = "70404040" #VIA FERREA
        styles['EO']      = "70009988" #PASTOS CON OLIVOS

        styles['84']      = "70405070" #DISEMINADO
        styles['85']      = "70306090" #VIÑUELAS

        styles['GE']      = "7050AA66" #generico # not used ?
        styles['DES']     = "708000AA" #desconocido
        styles['PRI']     = "70700020" #privado

        styles['AM']     = "60500010" #PARAJE
        styles['560']     = "60500010" #CASTILLO
        styles['78']     = "60500010" #RONCESVALLES
        styles['90024']     = "60500010" #SECTOR-5


        style ="""
        <Style id="{id}">
            <LineStyle>
                <color>ff000000</color>
                <width>1</width>
            </LineStyle>
            <PolyStyle>
                <color>{color}</color>
                <fill>1</fill>
            </PolyStyle>
        </Style>
        """

        s = ""
        for k in styles.keys():
            s += style.format(id=k, color=styles[k])

            

        # add special styles.

        s += """<Style id="gpxtrack">
            <LineStyle>
                <color>FFFF0000</color>
                <width>3</width>
            </LineStyle>
            </Style>

            <Style id="gpxwaypoint">
              <IconStyle>
                <scale>0.7</scale>
                <Icon>
                  <href>http://maps.google.com/mapfiles/kml/pal3/icon45.png</href>
                </Icon>
              </IconStyle>
            </Style>

            <Style id="trackplace">
              <IconStyle>
                <scale>0.7</scale>
                <Icon>
                  <href>http://maps.google.com/mapfiles/kml/pal3/icon46.png</href>
                </Icon>
              </IconStyle>
            </Style>
        """

        ctpl = """<Style id="%s">
            <LineStyle>
                <color>FF%s</color>
                <width>3</width>
            </LineStyle>
            </Style>
            """
        
        colors = ""
        for c in self.colors:
            colors += ctpl % (c, c)
        
        return s + colors

    def _genHeader(self, rname, polygons=False):


        head = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
            <name>{route_name}</name>
            {styles}
        """

        head = unicode(head)

        ## if polygons
        if polygons:
            style = self._genStyles_poly()
        else:
            style = self._genStyles()

        return head.format(route_name=rname, styles=style)

    def _genFooter(self):
        footer ="""
        </Document>
        </kml>
        """
        return footer

    def _genKMLPolygon(self, rc, coords, pname, desc, ccc):

        poly="""
             <Placemark>
                <name>{pname}</name>
                <description>{desc}</description>
                <styleUrl>#{ccc}</styleUrl>
                <Polygon>
                    <tessellate>1</tessellate>
                    <outerBoundaryIs>
                        <LinearRing>
                        <coordinates>
                        {coords}
                        </coordinates>
                    </LinearRing>
                </outerBoundaryIs>
            </Polygon>
            </Placemark>
            """

        lines = []
        for l in coords:
            d = ','.join(l)
            lines.append(d)

        return poly.format(pname=pname.encode('ASCII','xmlcharrefreplace'),
                           desc=desc.encode('ASCII','xmlcharrefreplace'),
                           rc=rc, ccc=ccc, coords=' '.join(lines))


def GPXString2KMLString(fname, gpxstr, optimize=False, desc=None):
        "gpx string (from DB) to KML string"

        gpx = GPXItem()
        gpx.LoadFromString(gpxstr)
        gpx.MergeAll()
        return GPX2KMLString(fname, gpx, optimize, desc)
    
def GPXString2KMLSlopeString(fname, gpxstr, optimize=False, desc=None):
        "gpx string (from DB) to KML string"

        gpx = GPXItem()
        gpx.LoadFromString(gpxstr)
        gpx.MergeAll()
        return GPX2KMLSlopeString(fname, gpx, optimize, desc)    

def GPXWPT2KMLString(fid, gpx_wp):
        "WPT Objects to KML string (e.g. Parsed from GPX file)"
        kmlfile = KML(fid,  None)
        kml = kmlfile.GPXWP2Kml(gpx_wp.gpx.waypoints)
        return kmlfile.Create(kml)

def Places2KMLString(place_list, title="Places", extended_desc=True):
        "Place list to KML string (e.g. from the DB)"
        kmlfile = KML(title,  None)
        kml = kmlfile.GPXWP2Kml(place_list, style="trackplace", extdata="ntracks", extdesc=extended_desc)
        return kmlfile.Create(kml)


def GPX2KMLString(fname, gpx, optimize=False, desc=None):
        "GPX Data Object to KML String (e.g. Parsed from GPX File)"

        #gsize = 5
        #if len(gpx.gpx.tracks[0].segments[0].points) > 1000:
        #    gsize = 10
        #opt_points = gpx.gpx.tracks[0].segments[0].points[::gsize]
        gpx.gpx.tracks[0].segments[0].points = filter(lambda x: x.latitude!=0.0 and x.longitude!=0.0, gpx.gpx.tracks[0].segments[0].points)

        if optimize:
            gpx_optmizer = GPXOptimizer()
            opt_points = gpx_optmizer.Optimize(gpx.gpx.tracks[0].segments[0].points)
            #opt_points = gpx_optmizer.Optimize(opt_points)
            #gpx_optmizer.Print_stats()
            gpx.gpx.tracks[0].segments[0].points = opt_points

        kmlfile = KML(fname,  None)

        # full track
        kml = kmlfile.GPX2KMLPlacemark(gpx.gpx.tracks[0].segments[0].points,
                                       gname=fname,
                                       gdesc=desc,
                                       style="gpxtrack")

        return kmlfile.Create(kml)


    
    
def GPX2KMLSlopeString(fname, gpx, optimize=False, desc=None):
        "GPX Data Object to KML String (e.g. Parsed from GPX File)"

        #gsize = 5
        #if len(gpx.gpx.tracks[0].segments[0].points) > 1000:
        #    gsize = 10
        #opt_points = gpx.gpx.tracks[0].segments[0].points[::gsize]
        gpx.gpx.tracks[0].segments[0].points = filter(lambda x: x.latitude!=0.0 and x.longitude!=0.0, gpx.gpx.tracks[0].segments[0].points)

        if optimize:
            gpx_optmizer = GPXOptimizer()
            opt_points = gpx_optmizer.Optimize(gpx.gpx.tracks[0].segments[0].points)
            #opt_points = gpx_optmizer.Optimize(opt_points)
            #gpx_optmizer.Print_stats()
            gpx.gpx.tracks[0].segments[0].points = opt_points

        # set the points, calculate (after optimized version)        
        slopemanager = slopes.SlopeManager(distance_gap=10.0)
        slopemanager.SetGPX(gpx.gpx)
        slopemanager.ComputeSlope()

        kmlfile = KML(fname,  None)

        # for each pair of points, create a kml placemark, and then join then.

        rainbow = rainbowvis.SlopeGradient()

        kml = ""
        pcontainer = [ slopemanager[0] ]
        i = 1
        while i < slopemanager.len():
     
            p = slopemanager[i-1]       
            q = slopemanager[i]
       
            onlyOne = False
            if p.slope_avg != q.slope_avg:
       
                # create a new segment.
                if len(pcontainer) == 1:
                    pcontainer.append(q) #
                    onlyOne = True 
                     
                color = rainbow.colourAt(-float(p.slope_avg))
                kmlfile.AddColor(color)
                kml += kmlfile.GPX2KMLPlacemark(pcontainer,
                                                gname="%3.2f" % p.slope_avg,
                                                gdesc=desc,
                                                style=color)
                if onlyOne:
                    pcontainer = [ q ]
                    i += 1
                else:
                    pcontainer = [ p ]
                
            else:
                pcontainer.append(q)
                i += 1
                
        if len(pcontainer) > 1:
                color = rainbow.colourAt(-float(pcontainer[-1].slope_avg))
                kmlfile.AddColor(color)
                kml += kmlfile.GPX2KMLPlacemark(pcontainer,
                                                gname="%3.2f" % pcontainer[-1].slope_avg,
                                                gdesc=desc,
                                                style=color)
            
                
        return kmlfile.Create(kml)
    
    




