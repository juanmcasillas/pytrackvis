##!/usr/bin/env bash
# -*- coding: utf-8 -*-
# /////////////////////////////////////////////////////////////////////////////
# //
# // helpers.py 
# //
# // 
# //
# // 19/11/2024 09:46:13  
# // (c) 2024 Juan M. Casillas <juanm.casillas@gmail.com>
# //
# /////////////////////////////////////////////////////////////////////////////

import gpxpy
import math
import os
class C:
    def __init__(self, **kargs):
        for i in kargs:
            self.__setattr__(i, kargs[i])


def manhattan_distance(a,b):
    # Σ|Ai – Bi|
    return sum(abs(val1-val2) for val1, val2 in zip(a,b))

def manhattan_point(p1,p2):
    a = [p1.latitude, p1.longitude, p1.elevation]
    b = [p2.latitude, p2.longitude, p2.elevation]
    return sum(abs(val1-val2) for val1, val2 in zip(a,b))


def module(vector):
    return math.sqrt(sum(v**2 for v in vector))


def track_similarity(trk1, trk2):
    # iterate the track with less points, and calculate
    # the sum of the manhattan_distance between points.

    if len(trk1._gpx_points) >= len(trk2._gpx_points):
        max_points = len(trk2._gpx_points) 
    else:
        max_points = len(trk1._gpx_points)

    similarity = 0.0
    for i in range(0,max_points):
        similarity += manhattan_point(trk1._gpx_points[i], trk2._gpx_points[i])

    return similarity / max_points 



def set_proxy(proxy_url):
    "proxy = 'http://<user>:<pass>@<proxy>:<port>'"
    os.environ['http_proxy']  = proxy_url 
    os.environ['HTTP_PROXY']  = proxy_url
    os.environ['https_proxy'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url    


def max_min_avg_from_list(l):
    max_value = max(l)
    min_value = min(l)
    avg_value = 0 if len(l) == 0 else float(sum(l))/len(l)
    return (max_value, min_value, avg_value)

def is_nan(x):
    return (x != x) or x is None

def get_fval(x, v=0.0):
    return  x if not is_nan(x) else v

def time_str(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)

def next_odd_floor(x):
    
    i = int(x)
    while i>0:
        if i % 2 != 0:
            return i
        i = i-1
    
    return x

def bearing(A, B):
    return gpxpy.geo.get_course(A.latitude, A.longitude, 
                                B.latitude, B.longitude, 
                                loxodromic=True)

def distancePoints(A, B):
    return gpxpy.geo.distance( A.latitude, A.longitude, A.elevation,
                               B.latitude, B.longitude, B.elevation,
                               haversine=False )
    
def distancePoints3D(A, B):
    return gpxpy.geo.distance( A.latitude, A.longitude, A.elevation,
                               B.latitude, B.longitude, B.elevation,
                               haversine=True )

def gradeslope(distance, elevation):
    
    if distance == 0.0 or elevation == 0.0: 
        return 0.0
    
    r = math.pow(distance, 2) - math.pow(elevation, 2)

    d = distance    
    if r > 0.0: 
        d = math.sqrt( r )
        
    s = (elevation / d) * 100.0             # projected distance (horizontal)
    s = (elevation / distance) * 100.0      # aproximation
    
    #print("distance: %3.2f elevation: %3.2f d: %3.2f s: %3.2f " % (distance,elevation,d, s))
    return s

def guess_clockwise(gpx_points, p_center):
    
    a = gpx_points[0]
    b = gpx_points[int(len(gpx_points)/6)]
    
    a_b = bearing(p_center,a) 
    b_b = bearing(p_center,b) 
    
    # convert from compass to algebra.
    
    a_b = (a_b-90) % 360
    b_b = (b_b-90) % 360 
     
    a_d = distancePoints(p_center, a)
    b_d = distancePoints(p_center, b)
    
    A = ( a_d * math.cos(math.radians(a_b)), a_d * math.sin(math.radians(a_b)) )
    B = ( b_d * math.cos(math.radians(b_b)), b_d * math.sin(math.radians(b_b)) )
    
    MA =  math.sqrt( math.pow(A[0],2) + math.pow(A[1],2) )

    AX = (A[0]*B[1]) - (A[1]*B[0])
    M_AX = (AX / (2 * MA ))
    

    if M_AX >= 0:
        #if DEBUG: print "->"
        return True
    
    #if DEBUG: print "<-"
    return False


def savitzky_golay(y, window_size, order, deriv=0, rate=1):

    import numpy as np
    from math import factorial

    try:
        window_size = np.abs(int(window_size))
        order = np.abs(int(order))
    except ValueError as e:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')
