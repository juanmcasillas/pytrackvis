##!/usr/bin/env python
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // track.py 
# //
# // Define the class to map abstract tracks (collection of points)
# //
# // 23/10/2024 10:00:14  
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# /////////////////////////////////////////////////////////////////////////////

import re
import gpxpy
import uuid
import datetime 

from .helpers import bearing, distancePoints
from .stats import Stats, get_fval
from .optimizer import GPXOptimizer


class UnitConverter:
    def __init__(self):
        pass

    def _same(data):
        return(data)
    
    def _semicircles(data):
        return( float(data) / 11930465.0 ) # "2^32/360"

    def _timezulu(data):
        """
        2018-08-15T09:17:26Z
        2011-09-25 16:31:49+00:00
        """

        data = re.sub(r'\dT\d',' ',data) # remove the T
        data = re.sub(r'\dZ$','+00:00',data) # remove the Z and add the trail
        return data


    def convert(value, conv, kind=float):
       
        ret = value
        if kind is not None:
            try:
                ret = kind(value)
            except TypeError as e:
                pass
        if ret is not None:
            ret = conv(ret)
        else:
            ret = None

        return ret

    def timestamp(value,  conv=_same ):
        return UnitConverter.convert(value, conv, kind=None)
        
    def position(value, conv=_semicircles):
        return UnitConverter.convert(value, conv, kind=None)

    def altitude(value, conv=_same):
        return UnitConverter.convert(value, conv)
    
    def speed(value, conv=_same):
        return UnitConverter.convert(value, conv)
    
    def power(value, conv=_same):
        return UnitConverter.convert(value, conv, int)
    
    def grade(value, conv=_same):
        return UnitConverter.convert(value, conv)

    def heart_rate(value, conv=_same):
        return UnitConverter.convert(value, conv, int)
    
    def cadence(value, conv=_same):
        return UnitConverter.convert(value, conv, int)
    
    def temperature(value, conv=_same):
        return UnitConverter.convert(value, conv)


class TrackPoint:
    def __init__(self,
                 timestamp     = None,
                 position_lat  = None,
                 position_long = None,
                 altitude      = None,
                 speed         = None,
                 power         = None,
                 grade         = None,
                 heart_rate    = None,
                 cadence       = None,
                 temperature   = None
    ):


        """
        Units for the datatypes
        timestamp           2011-09-25 16:31:49+00:00
        position_lat        521056079                   degrees
        position_long       -947375686                  degrees
        altitude            78.0                        m
        speed               0.0                         m/s
        power               None                        watts
        grade               None                        %
        heart_rate          156                         bpm
        cadence             None                        rpm
        temperature         27                          C
        """

        self.timestamp     = timestamp
        self.position_lat  = position_lat
        self.position_long = position_long
        self.altitude      = altitude
        self.speed         = speed
        self.power         = power
        self.grade         = grade
        self.heart_rate    = heart_rate
        self.cadence       = cadence
        self.temperature   = temperature

    def as_dict(self):
        d = {}
        d['timestamp']     =self.timestamp
        d['position_lat']  =self.position_lat
        d['position_long'] =self.position_long
        d['altitude']      =self.altitude
        d['speed']         =self.speed
        d['power']         =self.power
        d['grade']         =self.grade
        d['heart_rate']    =self.heart_rate
        d['cadence']       =self.cadence
        d['temperature']   =self.temperature
        return d

    def geojson_feature_collection(self):
        o = {
             "type": "geojson",
             "data": { 
                "type": "FeatureCollection",
                "features": [ ]
             }
        }
        return o
    
    def as_geojson_point(self):
        o = self.geojson_feature_collection()
        # add it to the geojson
        o["data"]["features"].append(self.as_geojson_point_feature())
        return o
    

    def as_geojson_point_feature(self):
        o = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                    "coordinates": [self.position_long, 
                                    self.position_lat, 
                                    self.altitude]
                },
                "properties": {
                    "timestamp": self.timestamp,
                    "speed": self.speed,
                    "power": self.power,
                    "grade": self.grade,
                    "heart_rate": self.heart_rate,
                    "cadence": self.cadence,
                    "temperature": self.temperature,
                }
        }
        return o

    def pos(self):
        return (self.position_long, self.position_lat, self.altitude)

    def pprint(self):
        print("{label:<20} {data} UTC".format(label="timestamp:",    data=self.timestamp))
        print("{label:<20} {data} deg".format(label="position_lat:", data=self.position_lat))
        print("{label:<20} {data} deg".format(label="position_long:",data=self.position_long))
        print("{label:<20} {data} m".format(label="altitude:",       data=self.altitude))
        print("{label:<20} {data} m/s".format(label="speed:",        data=self.speed))
        print("{label:<20} {data} w".format(label="power:",          data=self.power))
        print("{label:<20} {data} %".format(label="grade:",          data=self.grade))
        print("{label:<20} {data} bpm".format(label="heart_rate:",   data=self.heart_rate))
        print("{label:<20} {data} rpm".format(label="cadence:",      data=self.cadence))
        print("{label:<20} {data} ºC".format(label="temperature:",   data=self.temperature))

    def __repr__(self):
        s = "long: %f lat: %f altitude: %f timestamp: %s" % (
            self.position_long,
            self.position_lat,
            self.altitude,
            self.timestamp
        )
        return s
    

class TrackPointFit(TrackPoint):
    """
    timestamp           2011-09-25 16:31:49+00:00
    position_lat        521056079                   semicircles
    position_long       -947375686                  semicircles
    altitude            78.0                        m
    enhanced_altitude   78.0                        m
    enhanced_speed      0.0                         m/s
    speed               0.0                         m/s
    power               None                        watts
    grade               None                        %
    heart_rate          156                         bpm
    cadence             None                        rpm
    temperature         27                          C
    """

    def __init__(self,
                 timestamp         = None,
                 position_lat      = None,
                 position_long     = None,
                 altitude          = None,
                 speed             = None,
                 power             = None,
                 grade             = None,
                 heart_rate        = None,
                 cadence           = None,
                 temperature       = None,
                 enhanced_altitude = None,
                 enhanced_speed    = None
    ):
        super().__init__(self) 

        self.timestamp         = UnitConverter.timestamp(timestamp).isoformat()
        self.position_lat      = UnitConverter.position(position_lat)
        self.position_long     = UnitConverter.position(position_long)
        self.altitude          = UnitConverter.altitude(altitude)
        self.speed             = UnitConverter.speed(speed)
        self.power             = UnitConverter.power(power)
        self.grade             = UnitConverter.grade(grade)
        self.heart_rate        = UnitConverter.heart_rate(heart_rate)
        self.cadence           = UnitConverter.cadence(cadence)
        self.temperature       = UnitConverter.temperature(temperature)

        #extra data
        self.enhanced_altitude = UnitConverter.altitude(enhanced_altitude)
        self.enhanced_speed    = UnitConverter.speed(enhanced_speed)

        self.altitude = self.enhanced_altitude if self.enhanced_altitude else self.altitude
        self.speed = self.enhanced_speed if self.enhanced_speed else self.speed

class TrackPointGPX(TrackPoint):
    """
    timestamp (time)    2018-08-15T09:17:26Z
    lat                 40.253798961639404          degrees
    lon                -4.830367835238576          degrees
    ele                 512.79998779296875          m
    PowerInWatts        36                          watts
    hr                  133                         bpm
    cad                 32                          rpm
    atemp               27                          C
    Temperature         27                          C (enhanced)
    
    No speed.
    No grade.
    """

    def __init__(self,
                 timestamp    = None,
                 lat          = None,
                 lon          = None,
                 ele          = None,
                 PowerInWatts = None,
                 hr           = None,
                 cad          = None,
                 atemp        = None,
                 Temperature  = None,
                 power        = None,
 
    ):
        super().__init__(self) 

    

        self.timestamp         = UnitConverter.timestamp(timestamp, conv=UnitConverter._timezulu)
        self.position_lat      = UnitConverter.position(lat,conv=UnitConverter._same)
        self.position_long     = UnitConverter.position(lon,conv=UnitConverter._same)
        self.altitude          = UnitConverter.altitude(ele)
        self.power             = UnitConverter.power(PowerInWatts)
        self.heart_rate        = UnitConverter.heart_rate(hr)
        self.cadence           = UnitConverter.cadence(cad)
        self.temperature       = UnitConverter.temperature(atemp)

        # garmin 1000 
        # <power>0</power>
        if power is not None:
            p  = UnitConverter.power(PowerInWatts)
            self.power = p if p else self.power

        #extra data
        self.enhanced_temperature = UnitConverter.temperature(Temperature)
        self.temperature = self.enhanced_temperature if self.enhanced_temperature \
                            else self.temperature




class Track:
    def __init__(self, name="Track", id=None):
        self.fname = "-"
        self.name = name
        self.points = []
        self.id = id if id is not None else str(uuid.uuid4())
        self._gpx = None

    def clear(self): 
        self.points = []

    def add_point(self, point):
        self.points.append(point)

    def clear_empty_points(self):
        "remove invalid points (no lat, lon or time)"
        l = []
        c = 0
        for p in self.points:
            if p.position_lat is not None and \
               p.position_long is not None and \
               p.timestamp is not None:
                l.append(p)
            else:
                c += 1
        self.points = l
        return c     

    def set_internal_data(self, fname, optimize_points=False):
        #prepare a gpxpy object to build all the required things, bounds, means, etc
        self.fname = fname

   
        self._gpx = gpxpy.gpx.GPX()
        self._gpx.name = "internal gpx data"
        self._gpx.description = "internal  gpx file"
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        self._gpx.tracks.append(gpx_track)
         
        self._gpx_extensions = {
            "heart_rate":  [],
            "power":       [],
            "cadence":     [],
            "temperature": []
        }

        # Create points:
        for p in self.points:

            if p.position_lat is not None and \
               p.position_long is not None and \
               p.timestamp is not None:

                p_gpx = gpxpy.gpx.GPXTrackPoint(
                            latitude=p.position_lat,
                            longitude=p.position_long,
                            elevation=p.altitude,
                            time=datetime.datetime.fromisoformat(p.timestamp))

                self._gpx_extensions['heart_rate'].append(get_fval(p.heart_rate))
                self._gpx_extensions['power'].append(get_fval(p.power))
                self._gpx_extensions['cadence'].append(get_fval(p.cadence))
                self._gpx_extensions['temperature'].append(get_fval(p.temperature))

                gpx_segment.points.append(p_gpx)

        if optimize_points:
            optmizer = GPXOptimizer()  
            gpx_points = optmizer.Optimize(self._gpx.tracks[0].segments[0].points)
            self._gpx.tracks[0].segments[0].points = gpx_points
            optmizer.Print_stats()
    

    def pprint(self):
        print("Number of points: %d" % len(self.points))
        for p in self.points:
            p.pprint()
            print("")

    def as_dict(self):
        l = []
        for p in self.points:
            l.append(p.as_dict())
        return l

    def as_poly(self):
        l = []
        for p in self.points:
            if p.position_lat is not None and \
               p.position_long is not None:
                l.append((p.position_lat, p.position_long))
        return l

    def as_geojson_line(self):
       
        o = {}
        o["type"] = "geojson"
        o["data"] = { 
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [ ]
                }
        }
        for p in self.points:
            o["data"]["geometry"]["coordinates"].append([
                p.position_long, 
                p.position_lat, 
                p.altitude]
            )
        return o
    
    def as_geojson_points(self, points):
        col = TrackPoint().geojson_feature_collection()
        for p in points:
            col["data"]["features"].append(p.as_geojson_point_feature())
        return col

    def track_center(self):
        ## FIX_ME WITH GPXPY.
        l = self._gpx.tracks[0].get_center()
        print(dir(l))
        return(l.latitude, l.longitude, l.elevation)
    
    def start_point(self):
        return(self.points[0])

    def end_point(self):
        return(self.points[-1])
    
    def middle_point(self):
        return(self.points[int(len(self.points)/2)])

    def bounds(self, lonlat=False):
        min_lat, max_lat, min_lon, max_lon = self._gpx.tracks[0].segments[0].get_bounds()
        if not lonlat:
            return [[min_lat, min_lon], [max_lat, max_lon]]
    
        return [[min_lon, min_lat], [max_lon, max_lat]]

    def stats(self):
        # calculate some things about gpx info using gpxpy module.
        s = Stats(self)
        return s

