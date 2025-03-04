import datetime
import time
import math 
import calendar
import os.path

from .parser import HRMParser

def get_location_at_utc(gpx, start, delta):

    #d = datetime.datetime.utcfromtimestamp(timepoint)
    d = start + datetime.timedelta(seconds=delta)
    r = gpx.tracks[0].get_location_at(d)

    

    if len(r) == 0:
      #
      # last point reached (lap time is the last one)
      # return the last point info with altitude data
      #
      pindex = -1
      p = gpx.tracks[0].segments[0].points[pindex]
      while p.elevation == 0 and math.fabs(pindex) < gpx.tracks[0].get_points_no():
        p = gpx.tracks[0].segments[0].points[pindex]
        pindex -= 1
     
      return p

    return r[0]

def get_average_speed(gpx):
        """
        compute the average speed using the get_speed() method of the segment
        (Sum(PartialSpeed/#POints)

		Returns
		-------
        Float (speed m/s)
        """

        mt, st, md, sd, maxs = gpx.get_moving_data()

        #jmc fix 0 division no speed (e.g. roller)
        if mt+st == 0 or mt == 0:
            return (0,0)

        return ((md+sd)/(mt+st),(md)/(mt))

        # not reached

        speed = 0.0
        count = 0
        for track_segment in self.segments:
            for p in range(len(track_segment.points)):
                s = track_segment.get_speed(p)
                if s != None:
                    speed += s
                    count += 1

        return speed/count

def build_hrm_file(track, output_dir):

        # remove similar begin points

        for i in range(len(track.points)):
            #self._gpx_extensions['heart_rate'].append(get_fval(p.heart_rate))
            #self._gpx_extensions['power'].append(get_fval(p.power))
            #self._gpx_extensions['cadence'].append(get_fval(p.cadence))
            #self._gpx_extensions['temperature'].append(get_fval(p.temperature))
            track.points[i].extensions = { 'hr': track._gpx_extensions['heart_rate'][i], 
                                        'cad': track._gpx_extensions['cadence'][i], 
                                        'power': track._gpx_extensions['power'][i], 
                                        'left_torque_effectiveness': 0, 
                                        'left_pedal_smoothness': 0, 
                                        'speed': 0 }

        #
        # Ok, we have the HR from Garmin GPX. Now we have to build all the HRM
        # file
        #

        hrmfile = HRMParser()
        hrmfile.CreateEmpty()

        #
        # fill data.
        #
        hrmfile.sections['Params'].set_altitude(1)
        hrmfile.sections['Params'].set_speed(1)


        if 'cadence' in track._gpx_extensions.keys():
            hrmfile.sections['Params'].set_cadence(1)

        total_time_s = track._gpx.get_duration()
        gpx_date =  UTC2Localtime(track.points[0].time)#.strftime('%Y%m%d')
        gpx_starttime =UTC2Localtime(track.points[0].time)#.strftime('%H:%M:%S.0')
        gpx_length =  datetime.datetime.utcfromtimestamp(total_time_s)#.strftime('%H:%M:%S.0')

        #Params
        #Notes
        #IntTimes
        #ExtraData
        #Summary-123
        #Summary-TH
        #HRZones
        #SwapTimes
        #Trip
        #HRData


        hrmfile.sections['Params'].set_date(gpx_date)
        hrmfile.sections['Params'].set_starttime(gpx_starttime)
        hrmfile.sections['Params'].set_length(gpx_length)

        hrmfile.sections['Params'].set_altitude(True)

        hrmfile.sections['Summary-123'].set_time(total_time_s)
        hrmfile.sections['Summary-TH'].set_time(total_time_s)

        # then, calculate and fill the Trip Area

        hrmfile.sections['Trip'].set_distance       ( track._gpx.length_3d() )

        uphill,downhill = track._gpx.get_uphill_downhill()
        minalt,maxalt = track._gpx.get_elevation_extremes()
        moving_time, stopped_time, stopped_distance, moving_distance, max_speed = track._gpx.get_moving_data()

        hrmfile.sections['Trip'].set_ascent         ( uphill )
        hrmfile.sections['Trip'].set_totaltime      ( track._gpx.get_duration() )
        hrmfile.sections['Trip'].set_average_alt    ( (maxalt-minalt)/2.0 )
        hrmfile.sections['Trip'].set_max_alt        ( maxalt )
        hrmfile.sections['Trip'].set_average_speed  ( get_average_speed(track._gpx)[1] )
        hrmfile.sections['Trip'].set_max_speed      ( max_speed )
        hrmfile.sections['Trip'].set_odometer       ( track._gpx.length_3d() )

        # and now, generate the HRData !
        # get first point, add 5 seconds, and get data, until npoints
        # reached.

        npoints = int(math.ceil(total_time_s / float(hrmfile.sections['Params'].interval))) + 1

        hdata = []
        power_values = []

        #
        # GetLocationAt is looking for stamps in LocalTime instead
        # UTC... so the call is wrong. Use the get_location_at_utc instead
        #

        #start_date = calendar.timegm(track.points[0].time.timetuple())
        start_date = track.points[0].time

        prev_point = None
        for i in range(0, npoints):

    
            delta = i*hrmfile.sections['Params'].interval
          
            gpx_point = get_location_at_utc( track._gpx, start_date, delta )
      
            if gpx_point.extensions == None:
                gpx_point.extensions = { 'hr': 0, 
                                        'cad': 0, 
                                        'power': 0, 
                                        'left_torque_effectiveness': 0, 
                                        'left_pedal_smoothness': 0, 
                                        'speed': 0}

            hr = gpx_point.extensions['hr']
            cad = gpx_point.extensions['cad']
            power = gpx_point.extensions['power']
            left_pedal_smoothness = gpx_point.extensions['left_pedal_smoothness']
            left_torque_effectiveness = gpx_point.extensions['left_torque_effectiveness']

            pbpi_v = 0.0
            if left_pedal_smoothness != None and left_torque_effectiveness != None:
                pbpi_v = (left_pedal_smoothness*256)+left_torque_effectiveness

            if prev_point:
                speed = gpx_point.speed_between(prev_point)
                time_delta = gpx_point.time_difference(prev_point)
                distance_delta = gpx_point.distance_3d(prev_point)

                # fix out of bounds speeds (for example, when sampling > 1 sec)


                if (time_delta > 0 and speed > distance_delta / time_delta):
                    speed = distance_delta / time_delta

                if not speed:
                    speed = 0

                # converted later
                #speed = speed * 3.6 * 10 # (km/h)

            else:
                speed = 0
                time_delta = 0
                distance_delta = 0


            if not cad:
                    cad = 0


            hitem = [ int(hr), int(speed*3.6*10) ]
            power_values.append( (power, int(math.floor(pbpi_v))) )

            #jmc
            ##print speed, time_delta, distance_delta, "//",  roller_mode, hitem

            if 'cadence' in track._gpx_extensions.keys():
                hitem.append(int(cad))

            hitem.append(int(gpx_point.elevation))
            hdata.append(hitem)

            # advance!
            prev_point = gpx_point

        #
        # everything is done.
        # Equalize All the values and set it into the HRM file.
        #
  

        hrmfile.sections['HRData'].set_all( hdata )

        # add power data, if found in gpx.exceptions
        if 'power' in track._gpx_extensions.keys():

            hrmfile.sections['Params'].set_power(True)
            hrmfile.sections['HRData'].set_power(power_values)

        # target file is the date.
            
        gpx_date =  UTC2Localtime(track.points[0].time)
        target_fname = os.path.join(output_dir, gpx_date.strftime("%y%m%d01.hrm"))
        ##hrmfile.DebugSections(3)

        with open(target_fname,"w") as f:
            f.write(hrmfile.Export())
        return True







def UTC2Localtime(tobject):
    # changed to put the right hour in the HRM files
    # 19_11_2015

    # return a datetimeobject converted to current localtime
    #return datetime.fromtimestamp( calendar.timegm(tobject.timetuple()) )
    return datetime.datetime.fromtimestamp( time.mktime(tobject.timetuple()) )

