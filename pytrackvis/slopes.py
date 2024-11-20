##!/usr/bin/env bash
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // slopes.py 
# //
# // 
# //
# // 20/11/2024 10:08:22  
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# /////////////////////////////////////////////////////////////////////////////

import math
import gpxpy
#from .optimizer import *

from .helpers import distancePoints3D,gradeslope



class SlopeManager:
    def __init__(self, distance_gap=100.0):
        self.distance_gap = distance_gap
        self.fname = None
        self.gpx = None
        self.points = None
        
               
        #[n,m] -> [counter,weight]
        self.errors = { 'distance': { 'counter': 0, 'weight': 0.5},  #distance == 0
                        'stopped':  { 'counter': 0, 'weight': 0.5},  #speed = 0
                        'slope':    { 'counter': 0, 'weight': 1.0},  #><45
                        'speed':    { 'counter': 0, 'weight': 1.2}   #>120
                      }
 
    def __getitem__(self, key):
        return self.points[key]
    
    def __setitem__(self, key, value):
        
        self.points[key] = value
        return self.points[key]
    
    def __delitem__(self,key):
        return self.points.__delitem__(key)
    
    def len(self):
        return len(self.points)

    def SetGPXPoints(self, gpx_points, fname='-'):
        self.fname = fname
        self.gpx = None
        self.points = gpx_points


        
    def Analyze(self):
            
        tdata = []
        for i in range(len(self.points)):
            
            p = self.points[i]
            
            if not p.time:
                continue
            
            
            
            
            
            p.stime =  p.time.strftime("%Y-%m-%d %H:%M:%S")
            
            # calculate some metrics.
            p.time_d = 0.0
            p.distance_d = 0.0
            p.elevation_d = 0.0
            p.uphill = 0.0
            p.downhill = 0.0
            p.distance = 0.0
            p.speed = 0.0
            p.slope = 0.0
            p.wrong = ""
            
            if not hasattr(p,'keep'):
                p.keep = True
            
            has_error = False
            
            if i > 0:
                q = self.points[i-1]
                
                p.time_d      = p.time - q.time
                p.distance_d  = distancePoints3D(p, q)
                p.elevation_d = p.elevation - q.elevation
                p.distance    = q.distance + p.distance_d
                p.speed       = 0.0
                if p.distance_d > 0.0 and p.time_d.total_seconds() > 0:
                    p.speed       = (p.distance_d / p.time_d.total_seconds()) * 3.6 # km/h
                
                # slope
                p.slope       = gradeslope(p.distance_d, p.elevation_d)
                
                
                if p.elevation_d > 0:
                    p.uphill   = q.uphill + p.elevation_d
                    p.downhill = q.downhill
                else:
                    p.downhill   = q.downhill + p.elevation_d
                    p.uphill     = q.uphill 
            
                # mark "errors"
                
                if p.distance_d == 0.0: 
                    has_error = True
                    p.wrong = "DistanceD==0.0"
                    self.errors['distance']['counter'] += 1
                
                if p.speed == 0.0: 
                    has_error = True
                    p.wrong = "speed==0.0"
                    self.errors['stopped']['counter'] += 1
                    
                if math.fabs(p.slope) > 45: 
                    has_error = True
                    p.wrong = "slope %3.2f" % p.slope
                    self.errors['slope']['counter']  += 1
                    
                if math.fabs(p.speed) > 120:  
                    has_error = True
                    p.wrong = "speed %3.2f" % p.speed
                    self.errors['speed']['counter']  += 1
                    
                
            tdata.append( (has_error, i, 
                          p.latitude, p.longitude, p.stime, p.elevation,
                          p.distance, p.uphill, p.downhill,
                          p.elevation_d, p.distance_d, p.time_d, p.speed,  p.slope, p.slope_avg,  p.wrong, p.keep) )
            

        return tdata
    
    
   
    
    def ComputeSlope(self):
        
        if len(self.points) == 0:
            return
    
        distance_incr = 0.0
        elevation_incr = 0.0
        
        for i in range(len(self.points)):
            p = self.points[i]
            
            if i == 0:
                p.slope_avg = None
                continue
            
            q = self.points[i-1]
            
            distance_d  = distancePoints3D(p, q)
            elevation_d = p.elevation - q.elevation
            
            # skip stopped movements for computations
            # 10/06/2017 (remove high slopes on stops)
            # the average slope is not well computed.
            
            #if distance_d <1.0:
            #    p.slope_avg = None
            #    continue
            
            distance_incr += distance_d
            elevation_incr += elevation_d            
            
            ## print "[%5d] D: %7.2f | E: %7.2f" % (i, distance_incr, elevation_incr)
            
            if distance_incr >= self.distance_gap:
                # calculate average.
                # set before points ???
                p.slope_avg = gradeslope(distance_incr,elevation_incr)
                distance_incr = 0.0
                elevation_incr = 0.0
                ##print "* D: %7.2f | E: %7.2f | S: %3.2f" % (distance_incr, elevation_incr, p.slope_avg)
            else:
                p.slope_avg = None
        
        # manage trail ?
        p.slope_avg = gradeslope(distance_incr,elevation_incr)        
        
        # fix the holes.
        i = 0
        while i < len(self.points):
            p = self.points[i]
            if p.slope_avg == None:
                for j in range(i+1, len(self.points)):
                    q = self.points[j]
                    if q.slope_avg != None:
                        for k in range(i,j):
                            r = self.points[k]
                            r.slope_avg = q.slope_avg
                            
                        i = j+1
                        break
            else:
                i += 1
            
                    
            
            
