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


from .helpers import bearing, distancePoints, module
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
                 latitude      = None,
                 longitude     = None,
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
        latitude           521056079                   degrees
        longitude          -947375686                  degrees
        altitude            78.0                        m
        speed               0.0                         m/s
        power               None                        watts
        grade               None                        %
        heart_rate          156                         bpm
        cadence             None                        rpm
        temperature         27                          C
        """

        self.timestamp     = timestamp
        self.latitude      = latitude
        self.longitude     = longitude
        self.altitude      = altitude
        self.speed         = speed
        self.power         = power
        self.grade         = grade
        self.heart_rate    = heart_rate
        self.cadence       = cadence
        self.temperature   = temperature

    def as_vector(self):
        return [self.latitude, self.longitude, self.altitude]

    def as_dict(self):
        d = {}
        d['timestamp']     =self.timestamp
        d['latitude']      =self.latitude
        d['longitude']     =self.longitude
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
                    "coordinates": [self.latitude,
                                    self.longitude,
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
        return (self.longitude, self.latitude, self.altitude)

    def pprint(self):
        print("{label:<20} {data} UTC".format(label="timestamp:",    data=self.timestamp))
        print("{label:<20} {data} deg".format(label="latitude:",     data=self.latitude))
        print("{label:<20} {data} deg".format(label="longitude:",    data=self.longitude))
        print("{label:<20} {data} m".format(label="altitude:",       data=self.altitude))
        print("{label:<20} {data} m/s".format(label="speed:",        data=self.speed))
        print("{label:<20} {data} w".format(label="power:",          data=self.power))
        print("{label:<20} {data} %".format(label="grade:",          data=self.grade))
        print("{label:<20} {data} bpm".format(label="heart_rate:",   data=self.heart_rate))
        print("{label:<20} {data} rpm".format(label="cadence:",      data=self.cadence))
        print("{label:<20} {data} ºC".format(label="temperature:",   data=self.temperature))

    def __repr__(self):
        s = "long: %f lat: %f altitude: %f timestamp: %s" % (
            self.longitude,
            self.latitude,
            self.altitude,
            self.timestamp
        )
        return s


class TrackPointFit(TrackPoint):
    """
    timestamp           2011-09-25 16:31:49+00:00
    latitude        521056079                   semicircles
    longitude       -947375686                  semicircles
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
        self.latitude          = UnitConverter.position(position_lat)
        self.longitude         = UnitConverter.position(position_long)
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
        self.latitude          = UnitConverter.position(lat,conv=UnitConverter._same)
        self.longitude         = UnitConverter.position(lon,conv=UnitConverter._same)
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
        self.fname = None #see set_internal_data() for details
        self.name = name
        self.points = []
        self.hash = None #see set_internal_data() for details
        self.id = id if id is not None else str(uuid.uuid4())
        self._gpx = None
        self._gpx_points = None
        self._stats = None
        self._optimizer = None
        self.kind = "kind_ph"
        self.device = "device_ph"
        self.equipment = "equipment_ph"
        self.description = "description_ph"

    def from_dict(self, d):
        for i in d:
            self.__setattr__(i, d[i])
        return self

    def clear(self):
        self.points = []

    def add_point(self, point):
        self.points.append(point)

    def clear_empty_points(self):
        "remove invalid points (no lat, lon or time)"
        l = []
        c = 0
        for p in self.points:
            if p.latitude is not None and \
               p.longitude is not None and \
               p.timestamp is not None:
                l.append(p)
            else:
                c += 1
        self.points = l
        return c

    def set_internal_data(self, fname, optimize_points=False, filter_points=False, do_stats=True):
        #prepare a gpxpy object to build all the required things, bounds, means, etc
        #calculate the stats,
        #optimize the track,
        #calculate the "hash"
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

        hash_array = []

        # Create points:
        for p in self.points:

            if p.latitude is not None and \
               p.longitude is not None and \
               p.timestamp is not None:

                p_gpx = gpxpy.gpx.GPXTrackPoint(
                            latitude=p.latitude,
                            longitude=p.longitude,
                            elevation=p.altitude,
                            time=datetime.datetime.fromisoformat(p.timestamp))

                self._gpx_extensions['heart_rate'].append(get_fval(p.heart_rate))
                self._gpx_extensions['power'].append(get_fval(p.power))
                self._gpx_extensions['cadence'].append(get_fval(p.cadence))
                self._gpx_extensions['temperature'].append(get_fval(p.temperature))

                gpx_segment.points.append(p_gpx)
                hash_array.append(module(p.as_vector()))

        self.hash = hash(tuple(hash_array))


        if optimize_points:
            self._optimizer = GPXOptimizer()
            gpx_points = self._optimizer.Optimize(self._gpx.tracks[0].segments[0].points)
            self._gpx.tracks[0].segments[0].points = gpx_points


        self._gpx_points = gpx_segment.points
        # precalc stats
        if do_stats:
            self.stats(filter_points=filter_points)

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
            if p.latitude is not None and \
               p.longitude is not None:
                l.append((p.latitude, p.longitude))
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
                p.longitude,
                p.latitude,
                p.altitude]
            )
        return o

    def as_geojson_points(self, points):
        col = TrackPoint().geojson_feature_collection()
        for p in points:
            col["data"]["features"].append(p.as_geojson_point_feature())
        return col

    def track_center(self, as_point=False):
        ## FIX_ME WITH GPXPY.
        l = self._gpx.tracks[0].get_center()
        if not as_point:
            return(l.latitude, l.longitude, l.elevation)
        return l

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

    def stats(self, filter_points=False):
        # calculate some things about gpx info using gpxpy module.
        # cache the stats, due they are expensive.
        if self._stats is None:
             self._stats = Stats(self, filter_points=filter_points)

        return self._stats


    def as_tuple(self, db=False):


        if not db:
            # return the current object
            # else, return also the stats in db format
            pass
        # id not passed
        return (self.fname, self.hash, self.preview, self._stats.number_of_points,
                self._stats.duration, self._stats.length_2d,self._stats.length_3d,
                self._stats.start_time, self._stats.end_time, self._stats.moving_time,

                self._stats.stopped_time, self._stats.moving_distance,
                self._stats.stopped_distance,

                self._stats.max_speed_ms, self._stats.max_speed_kmh,
                self._stats.avg_speed_ms, self._stats.avg_speed_kmh,
                self._stats.uphill_climb,self._stats.downhill_climb,
                self._stats.minimum_elevation,self._stats.maximum_elevation,

                self.name, self.kind, self.device, self.equipment,
                self.description, self._stats.rating,
                self._stats.is_circular, self._stats.quality,
                self._stats.is_clockwise, self._stats.score,
                self._stats.is_cloned,

                self._stats.bounds.min_latitude,
                self._stats.bounds.min_longitude,
                self._stats.bounds.max_latitude,
                self._stats.bounds.max_longitude,

                self._stats.middle_point.lat,
                self._stats.middle_point.long,
                self._stats.middle_point.elev,

                self._stats.begin_point.lat,
                self._stats.begin_point.long,
                self._stats.begin_point.elev,

                self._stats.end_point.lat,
                self._stats.end_point.long,
                self._stats.end_point.elev,

                self._stats.up_slope.distance,
                self._stats.level_slope.distance,
                self._stats.down_slope.distance,

                self._stats.up_slope.elevation,
                self._stats.level_slope.elevation,
                self._stats.down_slope.elevation,

                self._stats.up_slope.avg,
                self._stats.level_slope.avg,
                self._stats.down_slope.avg,

                self._stats.up_slope.p_distance,
                self._stats.level_slope.p_distance,
                self._stats.down_slope.p_distance,

                self._stats.up_slope.speed,
                self._stats.level_slope.speed,
                self._stats.down_slope.speed,

                self._stats.up_slope.time,
                self._stats.level_slope.time,
                self._stats.down_slope.time,

                self._stats.up_slope.p_time,
                self._stats.level_slope.p_time,
                self._stats.down_slope.p_time,

                self._stats.up_slope.range_distance[0],
                self._stats.up_slope.range_distance[1],
                self._stats.up_slope.range_distance[2],
                self._stats.up_slope.range_distance[3],
                self._stats.up_slope.range_distance[4],
                self._stats.up_slope.range_distance[5],
                self._stats.up_slope.range_distance[6],

                self._stats.down_slope.range_distance[0],
                self._stats.down_slope.range_distance[1],
                self._stats.down_slope.range_distance[2],
                self._stats.down_slope.range_distance[3],
                self._stats.down_slope.range_distance[4],
                self._stats.down_slope.range_distance[5],
                self._stats.down_slope.range_distance[6],

                self._stats.up_slope.range_time[0],
                self._stats.up_slope.range_time[1],
                self._stats.up_slope.range_time[2],
                self._stats.up_slope.range_time[3],
                self._stats.up_slope.range_time[4],
                self._stats.up_slope.range_time[5],
                self._stats.up_slope.range_time[6],

                self._stats.down_slope.range_time[0],
                self._stats.down_slope.range_time[1],
                self._stats.down_slope.range_time[2],
                self._stats.down_slope.range_time[3],
                self._stats.down_slope.range_time[4],
                self._stats.down_slope.range_time[5],
                self._stats.down_slope.range_time[6],

                self._stats.max_heart_rate,
                self._stats.min_heart_rate,
                self._stats.avg_heart_rate,
                
                self._stats.max_power,
                self._stats.min_power,
                self._stats.avg_power,
                
                self._stats.max_cadence,
                self._stats.min_cadence,
                self._stats.avg_cadence,
                
                self._stats.max_temperature,
                self._stats.min_temperature,
                self._stats.avg_temperature
        )