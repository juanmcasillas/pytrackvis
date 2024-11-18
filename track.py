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
import pandas as pd
import gpxpy
import gpxpy.gpx
import datetime
import numpy as np
import os

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
    def __init__(self, name="Track"):
        self.name = name
        self.points = []
        self.data = None

    def clear(self): 
        self.points = []

    def add_point(self, point):
        self.points.append(point)

    def filter(self):
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

    def process(self):
        "filter the track, calculate the pandas dataframe"
        self.filter()
        self.dataframe()

    def dataframe(self):
        self.data = pd.DataFrame(self.as_dict())
        return (self.data)

    def track_center(self):
        lat = self.data['position_lat'].mean()
        lon = self.data['position_long'].mean()
        return(lat, lon)
    
    def start_point(self):
        return(self.points[0])

    def end_point(self):
        return(self.points[-1])
    
    def middle_point(self):
        return(self.points[int(len(self.points)/2)])




    def bounds(self, lonlat=False):
        
        min_lat = self.data['position_lat'].min()
        min_lon = self.data['position_long'].min()

        max_lat = self.data['position_lat'].max()
        max_lon = self.data['position_long'].max()

        if not lonlat:
            return [[min_lat, min_lon], [max_lat, max_lon]]
    
        return [[min_lon, min_lat], [max_lon, max_lat]]

    def stats(self):
        # calculate some things about gpx info using gpxpy module.
        s = Stats(self.points, self.data)
        return s




class Stats:
    def __init__(self, points, data):
        gpx = gpxpy.gpx.GPX()
        gpx.name = "stats"
        gpx.description = "stats gpx file"
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        gpx.tracks.append(gpx_track)        

        # Create points:
        for p in points:

            p_gpx = gpxpy.gpx.GPXTrackPoint(
                        latitude=p.position_lat,
                        longitude=p.position_long,
                        elevation=p.altitude,
                        time=datetime.datetime.fromisoformat(p.timestamp))
            
            #p_gpx.extensions.append(('heart_rate', p.heart_rate))
            #p_gpx.extensions.append(('power', p.power))
            #p_gpx.extensions.append(('cadence', p.cadence))
            #p_gpx.extensions.append(('temperature', p.temperature))
            gpx_segment.points.append(p_gpx)

        # stats
        self.start_time, self.end_time = gpx.get_time_bounds()
        #b = gpx.get_bounds() use the dataFrame method if needed
        self.number_of_points = gpx.get_track_points_no()
        
        self.moving_time, self.stopped_time, self.moving_distance, \
            self.stopped_distance, self.max_speed_ms = gpx.get_moving_data()
        self.max_speed_kmh = self.max_speed_ms * 60. ** 2 / 1000.

        

        self.length_2d = gpx.length_2d()
        self.length_3d = gpx.length_3d()
        self.duration = gpx.get_duration()
        self.uphill_climb, self.downhill_climb =gpx.get_uphill_downhill()
        self.minimum_elevation, self.maximum_elevation =gpx.get_elevation_extremes()
        ##gpx.smooth()
        self.avg_speed_ms = self.length_3d / self.duration
        self.avg_speed_kmh = self.avg_speed_ms * 60. ** 2 / 1000.

        def is_nan(x):
            return (x != x)
        
        def get_fval(x, v=0.0):
            return x if not is_nan(x) else v

        # what about extensions ?
        self.max_heart_rate    = get_fval(data['heart_rate'].max())
        self.min_heart_rate    = get_fval(data['heart_rate'].min())
        self.avg_heart_rate    = get_fval(data['heart_rate'].mean())
        
        self.max_power    =  get_fval(data['power'].max())
        self.min_power    =  get_fval(data['power'].min())
        self.avg_power    =  get_fval(data['power'].mean())
        
        self.max_cadence    = get_fval(data['cadence'].max())
        self.min_cadence    = get_fval(data['cadence'].min())
        self.avg_cadence    = get_fval(data['cadence'].mean())
        
        self.max_temperature    = get_fval(data['temperature'].max())
        self.min_temperature    = get_fval(data['temperature'].min())
        self.avg_temperature    = get_fval(data['temperature'].mean())

    def dataframe(self):
        #columns=["A", "B"], data=[[5,np.nan]]),
        columns = [ 
            "number_of_points",
            "start_time",
            "end_time",
            "duration",
            "moving_time",
            "stopped_time",
            "max_speed",
            "avg_speed",
            "length_2d",
            "length_3d",
            "moving_distance",
            "stopped_distance",
            "uphill_climb",
            "downhill_climb",
            "minimum_elevation",
            "maximum_elevation",
            "max heart_rate",
            "min heart_rate",
            "avg heart_rate",
            "max power",
            "min power",
            "avg power",
            "max cadence",
            "min cadence",
            "avg cadence",
            "max temperature",
            "min temperature",
            "avg temperature",
        ]
        data = [[
            self.number_of_points,
            self.start_time,
            self.end_time,
            self.duration,
            self.moving_time,
            self.stopped_time,
            self.max_speed_kmh,
            self.avg_speed_kmh,
            self.length_2d,
            self.length_3d,
            self.moving_distance,
            self.stopped_distance,
            self.uphill_climb,
            self.downhill_climb,
            self.minimum_elevation,
            self.maximum_elevation,
            self.max_heart_rate,
            self.min_heart_rate,
            self.avg_heart_rate,
            self.max_power,
            self.min_power,
            self.avg_power,
            self.max_cadence,
            self.min_cadence,
            self.avg_cadence,
            self.max_temperature,
            self.min_temperature,
            self.avg_temperature
        ]]
        df = pd.DataFrame(columns = columns, data = data )
        return df 
    
    def pprint(self):
        print("Points:\t{:>38}".format(self.number_of_points))
        print("start_time:\t{:>30}".format(str(self.start_time)))
        print("end_time:\t{:>30}".format(str(self.end_time)))
        print("duration:\t{:>30}".format(str(datetime.timedelta(seconds=self.duration))))
        print("moving_time:\t{:>30}".format(str(datetime.timedelta(seconds=self.moving_time))))
        print("stopped_time:\t{:>30}".format(str(datetime.timedelta(seconds=self.stopped_time))))
        
        print("Max Speed:\t{:30.3f} km/h".format(self.max_speed_kmh))
        print("Avg Speed:\t{:30.3f} km/h".format(self.avg_speed_kmh))
        
        print("length_2d:\t{:30.3f} m".format(self.length_2d))
        print("length_3d:\t{:30.3f} m".format(self.length_3d))
        print("moving_distance:\t{:22.3f} m".format(self.moving_distance))
        print("stopped_distance:\t{:22.3f} m".format(self.stopped_distance))

        print("uphill_climb:\t{:30.3f} m".format(self.uphill_climb))
        print("downhill_climb:\t{:30.3f} m".format(self.downhill_climb))
        print("minimum_elevation:\t{:22.3f} m".format(self.minimum_elevation))
        print("maximum_elevation:\t{:22.3f} m".format(self.maximum_elevation))

        # extra parameters:
        print("max heart_rate:\t{:30.3f} bpm".format(self.max_heart_rate))
        print("min heart_rate:\t{:30.3f} bpm".format(self.min_heart_rate))
        print("avg heart_rate:\t{:30.3f} bpm".format(self.avg_heart_rate))

        print("max power:\t{:30.3f} watt".format(self.max_power))
        print("min power:\t{:30.3f} watt".format(self.min_power))
        print("avg power:\t{:30.3f} watt".format(self.avg_power))

        print("max cadence:\t{:30.3f} rpm".format(self.max_cadence))
        print("min cadence:\t{:30.3f} rpm".format(self.min_cadence))
        print("avg cadence:\t{:30.3f} rpm".format(self.avg_cadence))

        print("max temperature:\t{:22.3f} ºC".format(self.max_temperature))
        print("min temperature:\t{:22.3f} ºC".format(self.min_temperature))
        print("avg temperature:\t{:22.3f} ºC".format(self.avg_temperature))

    def to_html(self):
        tT = """
        <table border='1' class='dataframe table-condensed table-responsive table-success'>
        <tbody>
        __D
        </tbody>
        </table>
        """
        
        tI = """
            <tr>
            <th align='left'>__N</th>
            <td align='right'>__V</td>
            </tr>
        """

        i = []
        def _ai(tpl, data):
            r = tpl
            for k in data.keys():
                name = k
                value = data[k]
                r = re.sub(f"{name}",f"{value}", r)
            return r

        i.append(_ai(tI, {'__N': 'Points','__V'      : self.number_of_points }))
        i.append(_ai(tI, {'__N': 'Start Time','__V'  : self.start_time }))
        i.append(_ai(tI, {'__N': 'End Time','__V'    : self.end_time }))
        i.append(_ai(tI, {'__N': 'Duration','__V'    : str(datetime.timedelta(seconds=self.duration)) }))
        i.append(_ai(tI, {'__N': 'Moving Time','__V' : str(datetime.timedelta(seconds=self.moving_time)) }))
        i.append(_ai(tI, {'__N': 'Stopped Time','__V': str(datetime.timedelta(seconds=self.stopped_time)) }))
        i.append(_ai(tI, {'__N': 'Max Speed','__V'   : "%.3f Km/h" % self.max_speed_kmh }))
        i.append(_ai(tI, {'__N': 'Avg Speed','__V'   : "%.3f Km/h" %self.avg_speed_kmh }))
        i.append(_ai(tI, {'__N': 'Length 2D','__V'   : "%.3f m" %self.length_2d }))
        i.append(_ai(tI, {'__N': 'Length 3D','__V'   : "%.3f m" %self.length_3d }))
        i.append(_ai(tI, {'__N': 'Distance (Moving)','__V' : "%.3f m" %self.moving_distance }))
        i.append(_ai(tI, {'__N': 'Distance (Stopped)','__V': "%.3f m" %self.stopped_distance }))
        
        i.append(_ai(tI, {'__N': 'Climb (Uphill)', '__V' : "%.3f m" %self.uphill_climb }))
        i.append(_ai(tI, {'__N': 'Climb (Downhill)','__V': "%.3f m" %self.downhill_climb }))
        i.append(_ai(tI, {'__N': 'Min Elevation', '__V' : "%.3f m" %self.minimum_elevation }))
        i.append(_ai(tI, {'__N': 'Max Elevation','__V': "%.3f m" %self.maximum_elevation }))

        i.append(_ai(tI, {'__N': 'Max Heart Rate','__V' : "%d bpm" %self.max_heart_rate }))
        i.append(_ai(tI, {'__N': 'Min Heart Rate', '__V': "%d bpm" %self.min_heart_rate }))
        i.append(_ai(tI, {'__N': 'Avg Heart Rate','__V' : "%d bpm" %self.avg_heart_rate }))

        i.append(_ai(tI, {'__N': 'Max Power','__V' : "%d watt" %self.max_power }))
        i.append(_ai(tI, {'__N': 'Min Power', '__V': "%d watt" %self.min_power }))
        i.append(_ai(tI, {'__N': 'Avg Power','__V' : "%d watt" %self.avg_power}))
        
        i.append(_ai(tI, {'__N': 'Max Cadence','__V' : "%d rpm" %self.max_cadence }))
        i.append(_ai(tI, {'__N': 'Min Cadence', '__V': "%d rpm" %self.min_cadence }))
        i.append(_ai(tI, {'__N': 'Avg Cadence','__V' : "%d rpm" %self.avg_cadence }))

        i.append(_ai(tI, {'__N': 'Max Temperature','__V' : "%d &ordm;C" %self.max_temperature }))
        i.append(_ai(tI, {'__N': 'Min Temperature', '__V': "%d &ordm;C" %self.min_temperature }))
        i.append(_ai(tI, {'__N': 'Avg Temperature','__V' : "%d &ordm;C" %self.avg_temperature }))

        tbl = _ai(tT, {'__D': os.linesep.join(i)})
        return(tbl)

