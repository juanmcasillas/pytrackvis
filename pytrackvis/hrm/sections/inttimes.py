import math
from ..abstract import *


class IntTimesSection(AbstractSection):

	#LAP1
	#00:03:43.7 123 100 150 200 		Row 1
	#32 0 0 0 0 0 						Row 2 Lap time 0
	#0 0 0 0 0 							Row 3
	#0 400 455 21 0 0 					Row 4#
	#0 0 0 0 0 0 						Row 5#

	#LAP2
	#00:03:43.7 123 100 150 200 		Row 1
	#32 0 0 0 0 0 						Row 2 Lap time 0
	#0 0 0 0 0 							Row 3
	#0 400 455 21 0 0 					Row 4#
	#0 0 0 0 0 0 						Row 5#

	#...




	def __init__(self):
		AbstractSection.__init__(self,"IntTimes")
		self.items =  []
		self.laps 	= []
		self.tmp	= []

		#row2, field 6: momentary altitude.
		#row3, field 4: lap ascent from XTr+

	def CreateEmpty(self):
		pass

	def NumberOfLaps(self):
		return len(self.laps)

	def	LapTime(self, lap):
		row = self.laps[lap][0]	# first row
		t = row.split()[0]

		h,m,s = t.split(':')
		s,d = s.split('.')

		return map(int,[h, m, s, d])


	def set_momentary_altitude(self, lap, value):
		row = self.laps[lap][1] # second row
		t = row.split()
		t[5] = math.ceil(value)
		self.laps[lap][1] = '\t'.join(map(str,t))


	def set_asc(self, lap, value):
		row = self.laps[lap][2] # third row
		t = row.split()
		t[4] = math.ceil(value)
		self.laps[lap][2] = '\t'.join(map(str,t))

	def Validate(self):

		# move the tmp items, if any to lap.
		if len(self.tmp) > 0:
			self.laps.append(self.tmp)
			self.tmp = []


	def ParseData(self, line):
		t = line.split()
		x = t[0].split(':')

		if len(t) == 5 and len(x) == 3:
			# start of lap information
			if len(self.tmp) > 0:
				self.laps.append(self.tmp) #  all the bunch
				self.tmp = []
			self.tmp.append(line)
		else:
			# data from previous lap
			self.tmp.append(line)



	def PrintData(self):

		r = self.PrintHeader()
		c = 0
		for l in self.laps:
			ltime = l[0].split()[0] # row1,field1
			alt   = l[1].split()[5] # row2,field6
			asc   = l[2].split()[4] # row3,field4

			ltf = self.LapTime(c)
			fmt_ltime = "%d:%d:%d.%d" % (ltf[0],ltf[1],ltf[2],ltf[3] )

			r += "{:2d} {:<17} {:<20} {:>38}\r\n".format(c, "Time r1,f1", ltime, fmt_ltime)
			r += "{:2d} {:<17} {:<20} {:>38}\r\n".format(c, "Alt  r2,f6", alt, alt)
			r += "{:2d} {:<17} {:<20} {:>38}\r\n".format(c, "Asc  r3,f4", asc, asc)
			r += "-" * 80
			r += "\r\n"
			c+= 1

		return r

	def ExportData(self):
		r = ""
		for i in self.laps:
			for j in i:
				r += "%s\r\n" % j

		return r