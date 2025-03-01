from ..abstract import *

class Mode105:
	def __init__(self,mode):
		self.itemname = "Mode"
		self.version = "105"
		self.cadence = False
		self.altitude = False
		self.ccdata	= False 	# false: HR_DATA_ONLY, true: HR+cycling data
		self.euro_us = False	# false: EURO (Km km/h m) false: US (miles, mph, ft)

		a = mode[0]
		b = mode[1]
		c = mode[2]

		if a == '0': self.cadence = True
		if a == '1': self.altitude = True
		if a == '3': pass #both false

		if b == '0': pass # False: HR_DATA_ONLY
		if b == '1': self.ccdata = True #HR+cycling data

		if c == '0': pass   # EURO (Km km/h m)
		if c == '1': self.euro_us = True # US (miles, mph, ft)

	def ToBinary(self):
		s = ""
		if not self.cadence and not self.altitude:	s+= '3'
		if self.cadence: s+= '0'
		if self.altitude: s+= '1'

		if self.ccdata: s+= '1'
		else: s+= '0'

		if self.euro_us: s+= '1'
		else: s+= '0'

		return s



class SMode106:
	def __init__(self,mode):
		self.itemname = "SMode"
		self.version = "106"

		self.speed = False
		self.cadence = False
		self.altitude = False
		self.power = False
		self.power_left_right_balance = False
		self.pedalling_index = False
		self.ccdata = False	# false: HR_DATA_ONLY, true: HR+cycling data
		self.euro_us = False # false: EURO (Km km/h m) true: US (miles, mph, ft)

		a = mode[0]
		b = mode[1]
		c = mode[2]
		d = mode[3]
		e = mode[4]
		f = mode[5]
		g = mode[6]
		h = mode[7]

		if a == '1': self.speed = True
		if b == '1': self.cadence = True
		if c == '1': self.altitude = True
		if d == '1': self.power = True
		if e == '1': self.power_left_right_balance = True
		if f == '1': self.pedalling_index = True
		if g == '1': self.ccdata = True 	 	# HR+cycling data
		if h == '1': self.euro_us = True		# true: US (miles, mph, ft)

	def ToBinary(self):

		s = [ "0" ] * 8

		if self.speed:						s[0] = '1'
		if self.cadence:					s[1] = '1'
		if self.altitude:					s[2] = '1'
		if self.power:						s[3] = '1'
		if self.power_left_right_balance:			s[4] = '1'
		if self.pedalling_index:				s[5] = '1'
		if self.ccdata:						s[6] = '1'
		if self.euro_us:					s[7] = '1'

		return 	"".join(s)

class SMode107(SMode106):
	def __init__(self, mode):
		SMode106.__init__(self,mode)

		self.air_pressure = False

		i = mode[8]

		if i == '1': self.air_pressure = True

		def ToBinary(self):

			s = SMode106.ToBinary(self)
			if self.air_pressure: s+= '1'
			else: s+= '0'

			return s


class ParamsSection(AbstractSection):
	def __init__(self):
		AbstractSection.__init__(self,"Params")
		self.items = {}
		self.version = { '102': '1.02', '105': '1.05', '106': '1.06', '107': '1.07' }
		self.monitor= {
						'0':	'RCX5/RC3 GPS',
						'1':	'Polar Sport Tester / Vantage XL'	,
						'2':	'Polar Vantage NV (VNV)' 			,
						'3':	'Polar Accurex Plus' 				,
						'4':	'Polar XTrainer Plus' 				,
						'6':	'Polar S520' 						,
						'7':	'Polar Coach' 						,
						'8':	'Polar S210' 						,
						'9':	'Polar S410'						,
						'10':	'Polar S510' 						,
						'11':	'Polar S610 / S610i' 				,
						'12':	'Polar S710 / S710i / S720i' 		,
						'13':	'Polar S810 / S810i' 				,
						'15':	'Polar E600' 						,
						'20':	'Polar AXN500' 						,
						'21':	'Polar AXN700' 						,
						'22':	'Polar S625X / S725X' 				,
						'23':	'Polar S725' 						,
						'33':	'Polar CS400' 						,
						'34':	'Polar CS600X' 						,
						'35':	'Polar CS600' 						,
						'36':	'Polar RS400' 						,
						'37':	'Polar RS800' 						,
						'38':	'Polar RS800X'
						}

		# mode. Depends on each version. so we have to create a superset of items, and checkers
		self.mode = None # if version > 1.05 the entry is called SMode
		#self.smode = None # for versions up to 1.05

		self.date = [ 0, 0, 0 ] # year, month, day
		self.starttime = [ 0, 0, 0, 0 ] # hour, minutes, seconds, decs
		self.length = [ 0, 0, 0, 0 ] # hour, minutes, seconds, decs
		self.interval = None
		self.interval_mode = 0 # 0: NORMAL (secs), 1 R-R Data (238) 2 Intermediate (PST,VXL...)

		self.upper = [ 0, 0, 0 ] # Upper limit in BPM
		self.lower = [ 0, 0, 0 ] # Lower Limit in BPM
		self.timer = [ [0,0], [0,0], [0,0] ] # Exec timers in format mm:ss

		self.activelimit = 0		# Limits used in file-summary. 0: Limits 1 and 2, 1: Treshold limits
		self.maxhr 	= 0				# personal max heart rate (BPM)
		self.resthr = 0				# personal resting heart rate (BPM)
		self.startdelay = 0			# RR start delay (ms) (Vantage NV RR data only)
		self.v02max = 0				# VO2Max at time of exercise (for calories calc) # new version, VO2max
		self.vO2max = 0				# VO2Max at time of exercise (for calories calc) # new version, VO2max
		self.weight = 0				# Weight at time of exercise (for calories calc)

		# param list

		self.param_list = [ 'Version','Monitor','SMode','Date','StartTime','Length',
						    'Interval','Upper1','Lower1','Upper2','Lower2','Upper3','Lower3',
						    'Timer1','Timer2','Timer3','ActiveLimit','MaxHR',
						    'RestHR','StartDelay','VO2max','Weight' ]



	#RCX5 monitor flags with '0' (no monitor)  by default, PolarProTrainer adds a '1'
	#Polar Sport Tester / Vantage XL. Maybe it's better to put here the value
	#'22':	'Polar S625X / S725X' for more capable item.

	def CheckMonitor(self, monitor='22'):
		# brand new item
		if self.items['Monitor'] not in self.monitor.keys():
			self.items['Monitor'] = monitor # RCX5 :/
			return False
		else:
			# if the monitor is set to '1' (Vantage) move it to '22' (the RCX5 export data ...)
			if self.items['Monitor'] == '1':
				self.items['Monitor'] = monitor # RCX5 :/
		return True

	def Validate(self):
		"parse the values from the file and get human readable info"

		version = self.version[self.items['Version']]

		if version == '1.05': self.mode = Mode105(self.items['Mode'])
		if version == '1.06': self.mode = SMode106(self.items['SMode'])
		if version == '1.07': self.mode = SMode107(self.items['SMode'])

		self.date = [ self.items['Date'][0:4], self.items['Date'][4:6], self.items['Date'][6:8] ] # year, month, day

		self.starttime = self.ParsePolarTime(self.items['StartTime'])
		self.length = self.ParsePolarTime(self.items['Length'])
		self.interval = int(self.items['Interval'])

		# by default self.inverval_mode == 0, means time in seconds.
		if self.interval == '238': self.interval_mode = 1 # RRData
		if self.interval == '204': self.interval_mode = 2 # Intermediate times only

		self.upper = map(int, [ self.items['Upper1'], self.items['Upper2'], self.items['Upper3'] ])
		self.lower = map(int, [ self.items['Lower1'], self.items['Lower2'], self.items['Lower3'] ])

		# timers in the new file formats follow the hh:mm:ss.d format


		self.timer = [ self.ParsePolarTime(self.items['Timer1']),
					   self.ParsePolarTime(self.items['Timer2']),
					   self.ParsePolarTime(self.items['Timer3']) ]

		self.activelimit = int(self.items['ActiveLimit'])

		self.maxhr 	= int(self.items['MaxHR'])				# personal max heart rate (BPM)
		self.resthr = int(self.items['RestHR'])				# personal resting heart rate (BPM)
		self.startdelay = int(self.items['StartDelay'])		# RR start delay (ms) (Vantage NV RR data only)
		if 'V02max' in self.items.keys():
			self.v02max = int(self.items['V02max'])				# V02Max at time of exercise (for calories calc)
		else:
			self.vO2max = int(self.items['VO2max'])				# VO2Max new version

		self.weight = int(self.items['Weight'])				# Weight at time of exercise (for calories calc)

	def CreateEmpty(self):

		for p in self.param_list:
			self.items[p] = 0

		self.items['Version'] = '106'
		self.items['Monitor'] = '22' # Use the "Standard Not Found Monitor"
		self.items['SMode'] = '00000010'
		self.mode = SMode106(self.items['SMode'])

		self.items['Timer1'] = '00:00:00.0'
		self.items['Timer2'] = '00:00:00.0'
		self.items['Timer3'] = '00:00:00.0'

		# ###################################################################
		# USER config
		# fixed parameters (my configuration... put elsewere)
		# ####################################################################

		self.interval = 5
		self.maxhr = 184
		self.resthr = 59
		self.vO2max = 58
		self.weight = 67
		self.activelimit = 0
		self.interval_mode = 0

		self.items['Interval'] = self.interval
		self.items['IntervalMode'] = self.interval_mode
		self.items['MaxHR'] = self.maxhr
		self.items['RestHR'] = self.resthr
		self.items['VO2max'] = self.vO2max
		self.items['Weight'] = self.weight







	def ParseData(self, line):
		name,value = line.split('=')
		self.items[name] = value

	def PrintData(self):

		bools = [ 'No', 'Yes' ]
		ccdatas = [ 'HR_DATA_ONLY', 'HR_DATA_ONLY+Cycling' ]
		euros = [ 'EURO (km/h)', 'US (mph)' ]
		intervals =  [ 'seconds', 'R-R data', 'Intermediate times' ]
		activelimits = [ 'Limits 1 and 2', 'Treshold limits' ]

		r = self.PrintHeader()


		r += "{:<20} {:<20} {:>38}\r\n".format( "Version", 				self.items['Version'], 				self.version[self.items['Version']] )
		r += "{:<20} {:<20} {:>38}\r\n".format( "Monitor", 				self.items['Monitor'], 				self.monitor[self.items['Monitor']]	)
		r += "{:<20} {:<20} {:>38}\r\n".format( self.mode.itemname, 	self.items[self.mode.itemname], 	self.mode.version	 	  			)


		# show the modes depending on the version

		if self.items['Version'] == '105':
			r += "{:<20} {:<20} {:>38}\r\n".format( "Cadence", 			self.items[self.mode.itemname], 	bools[self.mode.cadence] 	)
			r += "{:<20} {:<20} {:>38}\r\n".format( "Altitude", 		self.items[self.mode.itemname], 	bools[self.mode.altitude] 	)
			r += "{:<20} {:<20} {:>38}\r\n".format( "ccdata", 			self.items[self.mode.itemname], 	ccdatas[self.mode.ccdata] 	)
			r += "{:<20} {:<20} {:>38}\r\n".format( "EURO/US", 			self.items[self.mode.itemname], 	euros[self.mode.euro_us] 	)

		if self.items['Version'] == '106' or self.items['Version'] == '107':
			r += "{:<20} {:<20} {:>38}\r\n".format( "Speed", 			self.items[self.mode.itemname], 	bools[self.mode.speed] 	)
			r += "{:<20} {:<20} {:>38}\r\n".format( "Cadence", 			self.items[self.mode.itemname], 	bools[self.mode.cadence] 	)
			r += "{:<20} {:<20} {:>38}\r\n".format( "Altitude", 		self.items[self.mode.itemname], 	bools[self.mode.altitude] 	)
			r += "{:<20} {:<20} {:>38}\r\n".format( "Power", 			self.items[self.mode.itemname], 	bools[self.mode.power] 	)
			r += "{:<20} {:<20} {:>38}\r\n".format( "PowerLR", 			self.items[self.mode.itemname], 	bools[self.mode.power_left_right_balance] 	)
			r += "{:<20} {:<20} {:>38}\r\n".format( "PedallingIDX", 	self.items[self.mode.itemname], 	bools[self.mode.pedalling_index] 	)
			r += "{:<20} {:<20} {:>38}\r\n".format( "ccdata", 			self.items[self.mode.itemname], 	ccdatas[self.mode.ccdata] 	)
			r += "{:<20} {:<20} {:>38}\r\n".format( "EURO/US", 			self.items[self.mode.itemname], 	euros[self.mode.euro_us] 	)

		if self.items['Version'] == '107':
			r += "{:<20} {:<20} {:>38}\r\n".format( "AirPressure", 	self.items[self.mode.itemname], 	bools[self.mode.air_pressure] 	)

		# continue with the parameters

		r += "{:<20} {:<20} {:>38}\r\n".format( "Date", 		self.items['Date'], 			"{:4}/{:2}/{:2} (yy/mm/dd)".format(self.date[0],self.date[1],self.date[2])  )
		r += "{:<20} {:<20} {:>38}\r\n".format( "StartTime", 	self.items['StartTime'], 		"{:02d}:{:02d}:{:02d}.{} (hh:mm:ss.d)".format(self.starttime[0],self.starttime[1],self.starttime[2],self.starttime[3])  )
		r += "{:<20} {:<20} {:>38}\r\n".format( "Length", 		self.items['Length'], 			"{:02d}:{:02d}:{:02d}.{} (hh:mm:ss.d)".format(self.length[0],self.length[1],self.length[2],self.length[3])  )
		r += "{:<20} {:<20} {:>38}\r\n".format( "Interval", 	self.items['Interval'], 		self.interval )
		r += "{:<20} {:<20} {:>38}\r\n".format( "IntervalMode", self.items['Interval'], 		intervals[self.interval_mode] )


		for i in range(0,3):
			r += "{:<20} {:<20} {:>38}\r\n".format( "Upper%s" % (i+1), self.items['Upper%s' %(i+1)], 		"{} bpm".format(self.upper[i]) )

		for i in range(0,3):
			r += "{:<20} {:<20} {:>38}\r\n".format( "Lower%s" % (i+1), self.items['Lower%s' %(i+1)], 		"{} bpm".format(self.lower[i]) )

		for i in range(0,3):
			r += "{:<20} {:<20} {:>38}\r\n".format( "Timer%s" % (i+1), self.items['Timer%s' %(i+1)], 		"{:02d}:{:02d} (mm:ss)".format(self.timer[i][0],self.timer[i][1] ))

		r += "{:<20} {:<20} {:>38}\r\n".format( "ActiveLimit", self.items['ActiveLimit'], 		activelimits[self.activelimit] )
		r += "{:<20} {:<20} {:>38}\r\n".format( "MaxHR", self.items['MaxHR'], 			 		"{} bpm".format(self.maxhr) )
		r += "{:<20} {:<20} {:>38}\r\n".format( "RestHR", self.items['RestHR'], 				"{} bpm".format(self.resthr) )
		r += "{:<20} {:<20} {:>38}\r\n".format( "StartDelay", self.items['StartDelay'], 		"{} (ms)".format(self.startdelay) )

		# some versions has V02Max, other VO2Max ....
		vo2maxkey = 'VO2max'
		vo2max = None
		if 'V02Max' in self.items.keys():
			vo2maxkey = 'V02max'
			vo2max = self.v02max
		else:
			vo2max = self.vO2max

		r += "{:<20} {:<20} {:>38}\r\n".format( "V02Max", self.items[vo2maxkey], 		vo2max )

		r += "{:<20} {:<20} {:>38}\r\n".format( "Weight", self.items['Weight'], 		self.weight )

		return r

	# serializers to fix the Param Section (adding the Altitude value to the table)

	def set_altitude(self, data):
		self.mode.altitude = data
		self.items[self.mode.itemname] = self.mode.ToBinary()


	def set_speed(self, data):
		self.mode.speed = data
		self.items[self.mode.itemname] = self.mode.ToBinary()


	def set_cadence(self, data):
		self.mode.cadence = data
		self.items[self.mode.itemname] = self.mode.ToBinary()

	def set_power(self, data):
		self.mode.power = data
		self.mode.power_left_right_balance = data
		self.mode.pedalling_index = data
		self.items[self.mode.itemname] = self.mode.ToBinary()


	def set_date(self, gpx_date):
		self.date = [gpx_date.year, gpx_date.month, gpx_date.day ]
		self.items['Date'] = gpx_date.strftime('%Y%m%d')

	def set_starttime(self, gpx_start_time):
	
		self.starttime = [ gpx_start_time.hour,
						   gpx_start_time.minute,
						   gpx_start_time.second,
						   0 ]
		self.items['StartTime'] = gpx_start_time.strftime('%H:%M:%S.0')

	def set_length(self, gpx_length):

		self.length = [ gpx_length.hour,
						   gpx_length.time().minute,
						   gpx_length.time().second,
						   0 ]
		self.items['Length'] = gpx_length.strftime('%H:%M:%S.0')



	def ExportData(self):
		r = ""

		for key in self.param_list:
			r += "%s=%s\r\n" % (key, self.items[key])
		return r
