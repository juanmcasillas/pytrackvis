import math
from ..abstract import *


class HRDataSection(AbstractSection):
	def __init__(self):
		AbstractSection.__init__(self,"HRData")
		self.items = [ ]

	def Validate(self):
		pass

	def CreateEmpty(self):
		pass


	def PrintHeader(self, speed=False, cadence=False, power=False, altitude=False):
		r = "{:<20}"
		item = [ "HR(bpm)" ]

		if speed:
			r += " {:<15}"
			item.append( "Speed (km/h)" )

		if cadence:
			r += " {:<15}"
			item.append( "Cadence(rpm)" )

		if power:
			r += " {:<5}"
			item.append( "PWR " )

			r += " {:<7}"
			item.append( "PB/PI" )

		if altitude:
			r += " {:<15}"
			item.append("Altitude (m)")

		r = r.format(*item)
		r += "\r\n"
		r += "=" * 80
		r += "\r\n"
		return r

		r += "{:<20} {:<10} {:<10} {:>38}\r\n".format( "HR(bpm)",	"Speed (km/h)",	"Cadence(rpm)", "Altitude (m)"	)

	def Print(self, mode):
		"print the data for debugging"
		r = ""
		r += "Section [%s]\r\n" % self.name
		r += self.PrintData(mode)
		r += "\r\n"

		return r

	def ParseData(self, line):
		data = line.split()
		self.items.append( map(int, data) )

	def PrintData(self,mode):

		# mode is passed to get the values of cadence, speed and so on
		s = self.PrintHeader(mode.speed, mode.cadence, mode.power, mode.altitude)
		
		for i in self.items:
			r = "{:<20}"
			item = [ i[0] ]

			if mode.speed:
				r += " {:<15}"
				item.append( i[1] )

			if mode.cadence:
				r += " {:<15}"
				if mode.speed:
					item.append( i[2] )
				else:
					item.append( i[1] )	

			if mode.power:
				r += " {:<5} {:<7}"
				if mode.cadence and mode.speed:
					item.append( i[4])
					item.append( i[5])
				if mode.speed and not mode.cadence:
					item.append( i[1])
					item.append( i[2])
				if not mode.speed and not mode.cadence:
					item.append( i[0])
					item.append( i[1])
					
			if mode.altitude:
				r += " {:<15}"
				if mode.cadence and mode.speed:
					item.append( i[3] )
				if not mode.cadence and not mode.speed:
					item.append( i[1] )
				if not mode.cadence and mode.speed:
					item.append( i[2] )
				if mode.cadence and not mode.speed:
					item.append( i[2] )

			r += "\r\n"
			s += r.format(*item)

		s += "\r\n"
		return s

		for i in self.items:
			if len(i) < 3:
				r += "{:<20} {:<20} {:>38}\r\n".format( i[0], i[1], "N/A" )
			else:
				r += "{:<20} {:<20} {:>38}\r\n".format( i[0], i[1], i[2] )
		return r

	def len(self):	return len(self.items)

	def set_all(self, values):
		#
		# add all the values as array inside the item container.
		# note:
		# HRDATA
		# Speed-> To 0.1*3.6 (m/s to km/h * 0.1)
		# altitude -> Integer (in meters)
		# cadence ->
		#

		values = values or [ [0,0] ]
		for i in range(len(values)):
			self.items.append(values[i])


	def set_speed(self, speed_values):
		# data comes in m/s and polar likes km/h

		for i in range(len(speed_values)):
			speed_c = math.ceil( (speed_values[i] / 0.1) * 3.6 )
			self.items[i].append(speed_c)


	def set_altitude(self, altitude_values):
		# data comes in m

		for i in range(len(altitude_values)):
			alt_c = int(math.ceil( altitude_values[i] ))

			self.items[i].append(alt_c)


	def set_cadence(self, cadence_values):
		# data comes in rpm

		for i in range(len(cadence_values)):
			self.items[i].append(cadence_values[i])

	def set_power(self, power_values):
		# data comes in rpm

		for i in range(len(power_values)):
			self.items[i].append(power_values[i][0])
			self.items[i].append(power_values[i][1])

	def ExportData(self):
		r = ""
		for i in self.items:
			s = "\t".join( map(str, i))
			r += "%s\r\n" % s

		return r
