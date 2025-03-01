import math
from ..abstract import *


class TripSection(AbstractSection):
	def __init__(self):
		AbstractSection.__init__(self,"Trip")
		self.items = []

		self.distance = 0
		self.ascent   = 0 # 102 10m/10f, 105 1m/1f
		self.totaltime = 0 # in seconds
		self.average_alt = 0 # 102 10m/10f, 105 1m/1f
		self.max_alt = 0 # 102 10m/10f, 105 1m/1f
		self.average_speed = 0 # NUMBER / 128  km/h / mph (version 106 stores the data without divisions)
		self.max_speed = 0  # NUMBER / 128  km/h / mph (version 106 stores the data without divisions)
		self.odometer = 0

	def CreateEmpty(self):

		self.items = [ 0 ] * 8


	### SETTERS (this section CAN be modified)
	def setdefault(self):
		self.items = [ 0, 0, 0, 0, 0, 0, 0, 0 ]

	def set_ascent(self, value):		self.ascent = value
	def set_average_alt(self, value):	self.average_alt = value
	def set_max_alt(self, value):		self.max_alt = value

	def Validate(self):

		self.distance 		= self.items[0]
		self.ascent 		= self.items[1]
		self.totaltime 		= self.items[2]
		self.average_alt 	= self.items[3]
		self.max_alt 		= self.items[4]
		self.average_speed 	= self.items[5]
		self.max_speed 		= self.items[6]
		self.odometer 		= self.items[7]


	def ParseData(self, line):
		self.items.append( int(line) )

	def PrintData(self):

		r = self.PrintHeader()
		r += "{:<20} {:<20} {:>38}\r\n".format( "Distance", 			self.items[0], 				self.distance )
		r += "{:<20} {:<20} {:>38}\r\n".format( "Ascent", 				self.items[1], 				self.ascent )
		r += "{:<20} {:<20} {:>38}\r\n".format( "TotalTime", 			self.items[2], 				self.totaltime )
		r += "{:<20} {:<20} {:>38}\r\n".format( "AverageAlt", 			self.items[3], 				self.average_alt )
		r += "{:<20} {:<20} {:>38}\r\n".format( "MaxAlt", 				self.items[4], 				self.max_alt )
		r += "{:<20} {:<20} {:>38}\r\n".format( "AverageSpeed", 		self.items[5], 				self.average_speed  )
		r += "{:<20} {:<20} {:>38}\r\n".format( "MaxSpeed", 			self.items[6], 				self.max_speed  )
		r += "{:<20} {:<20} {:>38}\r\n".format( "Odometer", 			self.items[7], 				self.odometer )
		return r


	def set_distance(self, d):
		#remove dot, 8.7 is 87 measured in Km, receive meters)
		s = "%.1f" % (d/1000.0)
		self.distance = s.replace('.','')
		self.items[0] = self.distance

	def set_ascent(self, d):
		s = "%d" % d
		self.ascent = s
		self.items[1] = self.ascent

	def set_totaltime(self, d):
		# data come in seconds
		self.totaltime = d
		self.items[2] = self.totaltime

	def set_average_alt(self, d):
		# absolute value in meters
		self.average_alt = int(math.ceil(d))
		self.items[3] = int(self.average_alt)

	def set_max_alt(self, d):
		# absolute value in meters

		self.max_alt = int(math.ceil(d or 0.0))
		self.items[4] = int(self.max_alt)

	def set_average_speed(self, d):
		#remove dot, 8.7 is 87 measured in km/h, receive m/s)
		s = "%.1f" % (128 * d * 3.6)
		self.average_speed = s.replace('.','')
		self.items[5] = self.average_speed

	def set_max_speed(self, d):
		#remove dot, 8.7 is 87 measured in km/h, receive m/s)
		s = "%.1f" % (128 * d * 3.6)
		self.max_speed = s.replace('.','')
		self.items[6] = self.max_speed

	def set_odometer(self, d):
		#remove dot, 8.7 is 87 measured in Km, receive meters)
		s = "%.1f" % (d/10000.0)
		self.odometer = s.replace('.','')
		self.items[7] = self.odometer



	def ExportData(self):
		temp = self.items

		temp[1] = self.ascent
		temp[3] = self.average_alt
		temp[4] = self.max_alt

		r = ""
		for i in temp:
			r += "%s\r\n" % i

		return r
