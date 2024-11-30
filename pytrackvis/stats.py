
##!/usr/bin/env bash
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // stats.py 
# //
# // 
# //
# // 20/11/2024 10:45:31  
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# /////////////////////////////////////////////////////////////////////////////

import gpxpy
import datetime
import copy 
import time
import math

from .slopes import SlopeManager
from .helpers import C, guess_clockwise, distancePoints
from .helpers import distancePoints3D, next_odd_floor
from .helpers import savitzky_golay, gradeslope, time_str
from .helpers import is_nan, get_fval, max_min_avg_from_list
import numpy as np 

class Stats:
    def __init__(self, track, filter_points=False):
        
        self.track = track
        self.filter_points=filter_points
        self.calculate_stats()
    


    # "new" function to calculate a ton of new stats
    def calculate_stats(self, 
                        distance=100.0, 
                        limits={ 'low': -0.5, 'high': 0.5 }, 
                        hint=None,
                        filter_points=True):

        gpx_points = self.track._gpx.tracks[0].segments[0].points
       
        # min_latitude, max_latitude, min_longitude, max_longitude


        self.distance_gap = distance
        self.number_of_points = 0.0
        self.duration = 0
        self.length_2d = 0.0
        self.length_3d = 0.0
        
        self.start_time = 0
        self.end_time   = 0
        self.moving_time  = 0
        self.stopped_time  = 0
        self.moving_distance = 0.0
        self.stopped_distance = 0.0

        self.max_speed_ms = 0.0
        self.max_speed_kmh = 0.0
        self.avg_speed_ms = 0.0
        self.avg_speed_kmh = 0.0

        self.uphill_climb = 0.0
        self.downhill_climb = 0  #(False means ACW)
        self.minimum_elevation = 9999999999.9
        self.maximum_elevation = -1.0
        
        self.rating = 0
        self.is_circular = False
        self.quality = 0.0
        self.is_clockwise = False
        self.score = 0.0
        self.is_cloned = False

        #self.middle_point = C(lat=0.0, long=0.0, altitude=0.0)
        #self.begin_point = C(lat=0.0, long=0.0, altitude=0.0)
        #self.end_point = C(lat=0.0, long=0.0, altitude=0.0)

        
        self.up_slope = C(count=0, avg=0.0, distance=0.0, elevation=0.0,
                          speed=0.0, time=0, time_str=  "00:00:00",
                          p_time = 0,
                          p_distance = 0.0,
                          score = 0.0,
                          range_distance = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0  ],  # 0-5, 5-10, 10-15, 15-20, 20-25, >30
                          range_time = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0  ]
                          )
        

        self.level_slope = C(count=0, avg=0.0, distance=0.0, elevation=0.0,
                          speed=0.0, time=0, time_str=  "00:00:00",
                          p_time = 0,
                          p_distance = 0.0,
                          score = 0.0,
                          range_distance = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0  ],  # 0-5, 5-10, 10-15, 15-20, 20-25, >30
                          range_time = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0  ]
                          )

        self.down_slope = C(count=0, avg=0.0, distance=0.0, elevation=0.0,
                          speed=0.0, time=0, time_str=  "00:00:00",
                          p_time = 0,
                          p_distance = 0.0,
                          score = 0.0,
                          range_distance = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0  ],  # 0-5, 5-10, 10-15, 15-20, 20-25, >30
                          range_time = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0  ]
                          )


        
        self.hint = "UNKNOWN"
        self.hint_value = 1.0
        self.errors = None


        if self.track._gpx.get_points_no() == 0:
            raise ValueError("[W] No gpx_points to work with (len=0). Returning empty stats")

        center = self.track._gpx.tracks[0].get_center()
        # get_center() doesn't compute the average value for center elevation.
        center.elevation = self.track._gpx_points[int(len(self.track._gpx_points)/2)].elevation
        self.middle_point = C(
                        lat=center.latitude,
                        long=center.longitude,
                        elev=center.elevation
                    )
    
        self.begin_point = C(
                        lat=gpx_points[0].latitude,
                        long=gpx_points[0].longitude,
                        elev=gpx_points[0].elevation
                    )
        
        self.end_point = C(
                        lat=gpx_points[-1].latitude,
                        long=gpx_points[-1].longitude,
                        elev=gpx_points[-1].elevation
                    )
        


        self.is_clockwise = guess_clockwise(gpx_points, center)
        self.number_of_points = len(gpx_points)

        slopemanager = SlopeManager(self.distance_gap)
        slopemanager.SetGPXPoints(gpx_points)
        slopemanager.ComputeSlope()
        slopemanager.Analyze()        

        num_points = slopemanager.len()
        self.errors = copy.copy(slopemanager.errors)

        self.quality = 0.0
        for i in self.errors.keys():
            self.errors[i]['counter'] = ((100.0 * self.errors[i]['counter']) / num_points) * self.errors[i]['weight']
            self.quality += self.errors[i]['counter']
        self.quality = 100.0 - self.quality

        d = 0.0
        xs = []
        ys = []
        ts = []
    
        for i in range(len(gpx_points)):

            if gpx_points[i].elevation > self.maximum_elevation: 
                self.maximum_elevation = gpx_points[i].elevation 
            
            if gpx_points[i].elevation < self.minimum_elevation: 
                self.minimum_elevation = gpx_points[i].elevation 

            if i == 0:
                xs.append(0.0)
                ys.append(gpx_points[i].elevation or 0.0)
                tt = 0.0
                if gpx_points[i].time:
                    tt = time.mktime(gpx_points[i].time.timetuple())
                ts.append(tt)
                i += 1
                continue
                        
            d += distancePoints(gpx_points[i-1], gpx_points[i])
            xs.append(d)
            ys.append(gpx_points[i].elevation or 0.0)
            tt = 0.0
            if gpx_points[i].time:
                tt = time.mktime(gpx_points[i].time.timetuple())
            ts.append(tt)
            
            elevation_delta = math.fabs(gpx_points[i].elevation - gpx_points[i-1].elevation)
            
            if gpx_points[i].elevation > gpx_points[i-1].elevation:
                self.uphill_climb += elevation_delta
            if gpx_points[i].elevation < gpx_points[i-1].elevation:
                self.downhill_climb += elevation_delta
            
            i += 1

        try:
            if filter_points:
                if len(ys) < 135:
                    sg_index = next_odd_floor(len(ys))
                    #print("[W] Using %d as savitzky_golay index" % sg_index)
                    ys = savitzky_golay(np.array(ys), sg_index, 5)    
                else:    
                    ys = savitzky_golay(np.array(ys), 135, 5)    
        except TypeError as e:
            #raise TypeError("window_size is too small for the polynomials order")
            pass

        values = range(0, int(math.ceil(d)), int(distance))
        ret = np.interp( values, xs, ys)
        tret = np.interp( values, xs, ts)
        
        
        slope = 0.0
        distance_delta = 0.0
        elevation_delta = 0.0
        time_delta = 0.0

        for i in range(1, len(values)):
            
            elevation_delta = (ret[i]-ret[i-1])
            distance_delta = (values[i]-values[i-1])
            
            # points can be in reverse order, so check that this is absolute.
            time_delta = math.fabs(tret[i]-tret[i-1])
            
            # use the new hypotenuse calc
            #slope = 100.0 * (float(elevation_delta)/distance_delta)
            slope = gradeslope(distance_delta, elevation_delta)
    
            #if time_delta > 0.0:
            #    speed = float(distance_delta) / float(time_delta) 

            if slope > limits['high']:
                self.up_slope.count += 1
                self.up_slope.avg += slope
                self.up_slope.distance += distance_delta
                self.up_slope.elevation += elevation_delta
                self.up_slope.time += time_delta
                
                #stats.uphill += elevation_delta
        
                if slope >= limits['high'] and slope < 3.0: 
                    self.up_slope.range_distance[0] += distance_delta
                    self.up_slope.range_time[0] += time_delta
                if slope >= 3.0 and slope < 5.0: 
                    self.up_slope.range_distance[1] += distance_delta
                    self.up_slope.range_time[1] += time_delta
                if slope >= 5.0 and slope < 7.0: 
                    self.up_slope.range_distance[2] += distance_delta
                    self.up_slope.range_time[2] += time_delta
                if slope >= 7.0 and slope < 10.0: 
                    self.up_slope.range_distance[3] += distance_delta
                    self.up_slope.range_time[3] += time_delta
                if slope >= 10.0 and slope < 14.0: 
                    self.up_slope.range_distance[4] += distance_delta
                    self.up_slope.range_time[4] += time_delta
                if slope >= 14.0 and slope < 20.0: 
                    self.up_slope.range_distance[5] += distance_delta
                    self.up_slope.range_time[5] += time_delta
                if slope >= 20.0: 
                    self.up_slope.range_distance[6] += distance_delta
                    self.up_slope.range_time[6] += time_delta
                
        
            if slope > limits['low'] and slope < limits['high']:
                self.level_slope.count += 1
                self.level_slope.avg += slope
                self.level_slope.distance += distance_delta
                self.level_slope.elevation += elevation_delta
                self.level_slope.time += time_delta
    
            if slope < limits['low']:
                self.down_slope.count += 1
                self.down_slope.avg += slope
                self.down_slope.distance += distance_delta
                self.down_slope.elevation += elevation_delta
                self.down_slope.time += time_delta
    
                if slope >= -3.0 and slope < limits['low']: 
                    self.down_slope.range_distance[0] += distance_delta
                    self.down_slope.range_time[0] += time_delta
                if slope >= -5.0 and  slope < -3.0: 
                    self.down_slope.range_distance[1] += distance_delta
                    self.down_slope.range_time[1] += time_delta
                if slope >= -7.0 and slope < -5.0: 
                    self.down_slope.range_distance[2] += distance_delta
                    self.down_slope.range_time[2] += time_delta
                if slope >= -10.0 and slope < -7.0: 
                    self.down_slope.range_distance[3] += distance_delta
                    self.down_slope.range_time[3] += time_delta
                if slope >= -14.0 and slope < -10.0: 
                    self.down_slope.range_distance[4] += distance_delta
                    self.down_slope.range_time[4] += time_delta
                if slope >= -20.0 and slope < -14.0: 
                    self.down_slope.range_distance[5] += distance_delta
                    self.down_slope.range_time[5] += time_delta
                if slope <= -20.0: 
                    self.down_slope.range_distance[6] += distance_delta
                    self.down_slope.range_time[6] += time_delta
    
            self.duration += time_delta
            self.length_2d += distance_delta
            
            #if values[i] > self.maximum_elevation:  self.maximum_elevation = values[i]
            #if values[i] < self.minimum_elevation:  self.minimum_elevation = values[i]
            
        self.level_slope.elevation = math.fabs(self.level_slope.elevation)
        self.down_slope.elevation = math.fabs(self.down_slope.elevation)

        # compute slope average
    
        if self.up_slope.count != 0:
            self.up_slope.avg = self.up_slope.avg / self.up_slope.count
        else:
            self.up_slope.avg = 0
    
        if self.level_slope.count != 0:
            self.level_slope.avg = self.level_slope.avg / self.level_slope.count
        else:
            self.level_slope.avg = 0
        
        if self.down_slope.count != 0:
            self.down_slope.avg = self.down_slope.avg / self.down_slope.count
        else:
            self.down_slope.avg = 0

        # compute speed average
        
        if self.up_slope.time != 0:
            self.up_slope.speed = self.up_slope.distance / self.up_slope.time 
        else:
            self.up_slope.speed = 0
                
        if self.level_slope.time != 0:
            self.level_slope.speed = self.level_slope.distance / self.level_slope.time
            
        else:
            self.level_slope.speed = 0
        
        if self.down_slope.time != 0:
            self.down_slope.speed = self.down_slope.distance / self.down_slope.time
        else:
            self.down_slope.speed = 0

        # compute length percentages
        if self.length_2d > 0:
            self.up_slope.p_distance    = self.up_slope.distance* 100.0 / self.length_2d           
            self.level_slope.p_distance = self.level_slope.distance* 100.0 / self.length_2d
            self.down_slope.p_distance  = self.down_slope.distance* 100.0 / self.length_2d
        
        if self.duration > 0:
            
            self.up_slope.time_str    = time_str(self.up_slope.time)
            self.level_slope.time_str = time_str(self.level_slope.time)
            self.down_slope.time_str  = time_str(self.down_slope.time)
            
            self.up_slope.p_time    = (self.up_slope.time * 100.0) / self.duration
            self.level_slope.p_time = (self.level_slope.time * 100.0) / self.duration
            self.down_slope.p_time  = (self.down_slope.time * 100.0) / self.duration   
                                                    
            self.duration_str = time_str(self.duration)
        
        # m/s average of each part
        self.speed_avg =    (self.up_slope.speed * self.up_slope.p_distance/100.0)  +\
                            (self.level_slope.speed * self.level_slope.p_distance/100.0) +\
                            (self.down_slope.speed * self.down_slope.p_distance/100.0) 


    
        if self.duration == 0 or self.length_2d == 0.0:
            self.score = 0
            self.up_slope.score = 0
            self.level_slope.score = 0
            self.down_slope.score = 0
            return
        
        # give a point for each Km, based on hint.
        
        # TBD
        # scale "Km with this table"
        hintTable = { 'DEFAULT': 0.8, 'MTB': 0.8, 'ROAD': 0.7, 'RUN': 1.8, 'TREKKING': 1.6, 'TRAV': 2.0 }
        hintSpecial = { 'RUN': 0.8, 'TREKKING': 0.2, 'TRAV': 0.2 }
        
        if hint == None or not hint in hintTable.keys():
            hint = 'DEFAULT'
                
        hintValue = hintTable[hint]
        #print("Using HINT=%s (%3.2f)" % (hint, hintValue)
        
        self.hint = hint
        self.hint_value = hintValue
            
        
        ## I don't know how to manage this crap.
                    #   HI_5  5_10  10_15  15_20  20_25  25_30  30>
                    #  -5-LO -10-5 -15-10 -20-15 -25-20 -25-30  <30
        up_factor   = [  0.3,  0.4,   0.5,   0.6,   0.8,   1.0, 1.1 ]
        down_factor = [  0.1,  0.2,   0.3,   0.4,   0.8,   1.0, 1.1 ]
        
        if self.level_slope.avg == 0:
            level_factor = 0.05
        else:
            level_factor = self.level_slope.avg 
        
        up_score = 0.0
        down_score = 0.0
        
        for i in range(len(self.up_slope.range_distance)):
            
            # get the distance, each 100m, asign the hint value plus the upfactor based on the slope.
            up_score += (self.up_slope.range_distance[i] / 100.0) * hintValue * up_factor[i]
            down_score += (self.down_slope.range_distance[i] / 100.0) * hintValue * down_factor[i]
                    
        level_score = math.fabs(self.level_slope.distance / 100.0 * hintValue * level_factor)
        
        self.up_slope.score = up_score
        self.level_slope.score = level_score
        self.down_slope.score = down_score
        
        hint_special = 0.0
        if hint in [ 'RUN', 'TREKKING', 'TRAV' ]:
            hint_special = hintSpecial[hint]
        
        # add a bonus for each 100m climbed.
        # trav add less, because it has data from slopes
        
        hint_special = (self.uphill_climb / 100.0) * hint_special 
        correction = 2.0
        self.score =  (up_score + level_score + down_score + hint_special)  / correction

        ## geo stats

        self.start_time, self.end_time = self.track._gpx.get_time_bounds()
        
        self.moving_time, self.stopped_time, self.moving_distance, \
            self.stopped_distance, self.max_speed_ms = self.track._gpx.get_moving_data()
        self.max_speed_kmh = self.max_speed_ms * 60. ** 2 / 1000.

        self.length_3d = self.track._gpx.length_3d()
        self.avg_speed_ms = self.length_3d / self.duration
        self.avg_speed_kmh = self.avg_speed_ms * 60. ** 2 / 1000.        

        # what about extensions ?
        # use the self._gpx_extensions arrays to manage the max, min and so.

        self.max_heart_rate,self.min_heart_rate, self.avg_heart_rate  = \
            max_min_avg_from_list(self.track._gpx_extensions['heart_rate'])
      
        self.max_power,self.min_power, self.avg_power  = \
            max_min_avg_from_list(self.track._gpx_extensions['power'])
                                  
        self.max_cadence,self.min_cadence, self.avg_cadence  = \
            max_min_avg_from_list(self.track._gpx_extensions['cadence'])
                                          
        self.max_temperature,self.min_temperature, self.avg_temperature  = \
            max_min_avg_from_list(self.track._gpx_extensions['temperature'])

        min_lat, max_lat, min_lon, max_lon = self.track._gpx.tracks[0].segments[0].get_bounds()
    
        self.bounds= C(min_latitude=min_lat,
                    max_latitude=max_lat,
                    min_longitude=min_lon,
                    max_longitude=max_lon
                    )

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

        print("[*Distance GAP: %3.2f m (For Slopes)]" % self.distance_gap)
        print("[%12.2f] UP Avg: %8.2f D(%9.2f m)->%5.2f%% E(%8.2f m) S(%8.2f Km/h) T(%s)->%5.2f%%" % \
              (self.up_slope.score, 
               self.up_slope.avg, 
               self.up_slope.distance, self.up_slope.p_distance, self.up_slope.elevation, 
               self.up_slope.speed*3.6,self.up_slope.time_str,self.up_slope.p_time))
        
        print("\t\t 0.5%% -  3%%: [%10.2f m (%s)]"  % (self.up_slope.range_distance[0], time_str(self.up_slope.range_time[0])))
        print("\t\t   3%% -  5%%: [%10.2f m (%s)]" % (self.up_slope.range_distance[1], time_str(self.up_slope.range_time[1])))
        print("\t\t   5%% -  7%%: [%10.2f m (%s)]" % (self.up_slope.range_distance[2], time_str(self.up_slope.range_time[2])))
        print("\t\t   7%% - 10%%: [%10.2f m (%s)]" % (self.up_slope.range_distance[3], time_str(self.up_slope.range_time[3])))
        print("\t\t  10%% - 14%%: [%10.2f m (%s)]" % (self.up_slope.range_distance[4], time_str(self.up_slope.range_time[4])))
        print("\t\t  14%% - 20%%: [%10.2f m (%s)]" % (self.up_slope.range_distance[5], time_str(self.up_slope.range_time[5])))
        print("\t\t       >20%%: [%10.2f m (%s)]"  % (self.up_slope.range_distance[6], time_str(self.up_slope.range_time[6])))
        
        print("[%12.2f] LEVEL Avg: %5.2f D(%9.2f m)->%5.2f%% E(%8.2f m) S(%8.2f Km/h) T(%s)->%5.2f%%" % \
               (self.level_slope.score,
                self.level_slope.avg, 
                self.level_slope.distance, self.level_slope.p_distance, self.level_slope.elevation, 
                self.level_slope.speed*3.6,self.level_slope.time_str,self.level_slope.p_time))
        
        print("[%12.2f] DOWN Avg: %6.2f D(%9.2f m)->%5.2f%% E(%8.2f m) S(%8.2f Km/h) T(%s)->%5.2f%%" % \
               (self.down_slope.score, 
                self.down_slope.avg, 
                self.down_slope.distance, self.down_slope.p_distance, self.down_slope.elevation, 
                self.down_slope.speed*3.6,self.down_slope.time_str,self.down_slope.p_time))

        print("\t\t-3%% - -0.5%%: [%10.2f m (%s)]"  % (self.down_slope.range_distance[0], time_str(self.down_slope.range_time[0])))
        print("\t\t-5%%   - -3%%: [%10.2f m (%s)]" % (self.down_slope.range_distance[1], time_str(self.down_slope.range_time[1])))
        print("\t\t-7%%   - -5%%: [%10.2f m (%s)]" % (self.down_slope.range_distance[2], time_str(self.down_slope.range_time[2])))
        print("\t\t-10%%  - -7%%: [%10.2f m (%s)]" % (self.down_slope.range_distance[3], time_str(self.down_slope.range_time[3])))
        print("\t\t-14%% - -10%%: [%10.2f m (%s)]" % (self.down_slope.range_distance[4], time_str(self.down_slope.range_time[4])))
        print("\t\t-20%% - -14%%: [%10.2f m (%s)]" % (self.down_slope.range_distance[5], time_str(self.down_slope.range_time[5])))
        print("\t\t<-20%%      : [%10.2f m (%s)]"  % (self.down_slope.range_distance[6], time_str(self.down_slope.range_time[6])))
        
        print("               Numpoints: %d" % self.number_of_points)
        print("                  Length: %3.2f Km" % (self.length_2d / 1000.0))
        print("                Duration: %s" % self.duration_str)
        print("                  Uphill: %3.2f m" % ( self.uphill_climb))
        print("                Downhill: %3.2f m" % self.downhill_climb)
        print("                SpeedAVG: %3.2f Km/h" % (self.speed_avg*3.6))
        print("                 Alt_Max: %3.2f m" % (self.maximum_elevation))
        print("                 Alt_Min: %3.2f m" % (self.minimum_elevation))
        print("               Clockwise: %s" % self.is_clockwise)
        print("                    HINT: %s:%3.2f" % (self.hint, self.hint_value))
        print("                   Score: [%3.2f]" % self.score)
        print("                 Quality: [%3.2f]" % self.quality)
        
        if not self.errors:
            return 
        
        s = ""
        for i in self.errors.keys():
            s+= "%s: [%3.2f %%] " % (i, self.errors[i]['counter'])
        print("                  Errors: %s" % s)


    # deprecated code. to be removed soon
    #   
    # def to_html(self):
    #     tT = """
    #     <table border='1' class='dataframe table-condensed table-responsive table-success'>
    #     <tbody>
    #     __D
    #     </tbody>
    #     </table>
    #     """
        
    #     tI = """
    #         <tr>
    #         <th align='left'>__N</th>
    #         <td align='right'>__V</td>
    #         </tr>
    #     """

    #     i = []
    #     def _ai(tpl, data):
    #         r = tpl
    #         for k in data.keys():
    #             name = k
    #             value = data[k]
    #             r = re.sub(f"{name}",f"{value}", r)
    #         return r

    #     i.append(_ai(tI, {'__N': 'Points','__V'      : self.number_of_points }))
    #     i.append(_ai(tI, {'__N': 'Start Time','__V'  : self.start_time }))
    #     i.append(_ai(tI, {'__N': 'End Time','__V'    : self.end_time }))
    #     i.append(_ai(tI, {'__N': 'Duration','__V'    : str(datetime.timedelta(seconds=self.duration)) }))
    #     i.append(_ai(tI, {'__N': 'Moving Time','__V' : str(datetime.timedelta(seconds=self.moving_time)) }))
    #     i.append(_ai(tI, {'__N': 'Stopped Time','__V': str(datetime.timedelta(seconds=self.stopped_time)) }))
    #     i.append(_ai(tI, {'__N': 'Max Speed','__V'   : "%.3f Km/h" % self.max_speed_kmh }))
    #     i.append(_ai(tI, {'__N': 'Avg Speed','__V'   : "%.3f Km/h" %self.avg_speed_kmh }))
    #     i.append(_ai(tI, {'__N': 'Length 2D','__V'   : "%.3f m" %self.length_2d }))
    #     i.append(_ai(tI, {'__N': 'Length 3D','__V'   : "%.3f m" %self.length_3d }))
    #     i.append(_ai(tI, {'__N': 'Distance (Moving)','__V' : "%.3f m" %self.moving_distance }))
    #     i.append(_ai(tI, {'__N': 'Distance (Stopped)','__V': "%.3f m" %self.stopped_distance }))
        
    #     i.append(_ai(tI, {'__N': 'Climb (Uphill)', '__V' : "%.3f m" %self.uphill_climb }))
    #     i.append(_ai(tI, {'__N': 'Climb (Downhill)','__V': "%.3f m" %self.downhill_climb }))
    #     i.append(_ai(tI, {'__N': 'Min Elevation', '__V' : "%.3f m" %self.minimum_elevation }))
    #     i.append(_ai(tI, {'__N': 'Max Elevation','__V': "%.3f m" %self.maximum_elevation }))

    #     i.append(_ai(tI, {'__N': 'Max Heart Rate','__V' : "%d bpm" %self.max_heart_rate }))
    #     i.append(_ai(tI, {'__N': 'Min Heart Rate', '__V': "%d bpm" %self.min_heart_rate }))
    #     i.append(_ai(tI, {'__N': 'Avg Heart Rate','__V' : "%d bpm" %self.avg_heart_rate }))

    #     i.append(_ai(tI, {'__N': 'Max Power','__V' : "%d watt" %self.max_power }))
    #     i.append(_ai(tI, {'__N': 'Min Power', '__V': "%d watt" %self.min_power }))
    #     i.append(_ai(tI, {'__N': 'Avg Power','__V' : "%d watt" %self.avg_power}))
        
    #     i.append(_ai(tI, {'__N': 'Max Cadence','__V' : "%d rpm" %self.max_cadence }))
    #     i.append(_ai(tI, {'__N': 'Min Cadence', '__V': "%d rpm" %self.min_cadence }))
    #     i.append(_ai(tI, {'__N': 'Avg Cadence','__V' : "%d rpm" %self.avg_cadence }))

    #     i.append(_ai(tI, {'__N': 'Max Temperature','__V' : "%d &ordm;C" %self.max_temperature }))
    #     i.append(_ai(tI, {'__N': 'Min Temperature', '__V': "%d &ordm;C" %self.min_temperature }))
    #     i.append(_ai(tI, {'__N': 'Avg Temperature','__V' : "%d &ordm;C" %self.avg_temperature }))

    #     tbl = _ai(tT, {'__D': os.linesep.join(i)})
    #     return(tbl)