from ..abstract import *



class IntNotesSection(GenericSection):
	def __init__(self):
		GenericSection.__init__(self,"IntNotes")

	def CreateEmpty(self):
		self.items.append('Exercise-GPX')


class ExtraDataSection(GenericSection):
	def __init__(self):
		GenericSection.__init__(self,"ExtraData")



class Summary123Section(GenericSection):
	def __init__(self):
		GenericSection.__init__(self,"Summary-123")

	def set_time(self, tdata):
		t = tdata
		#4390    4390    0    0    0    0
		#0    0    0    0
		#4390    4390    0    0    0    0
		#0    0    0    0
		#0    0    0    0    0    0
		#0    0    0    0
		#0    4390

		self.items.append("%s\t%s\t0\t0\t0\t0" % (t,t))
		self.items.append("0\t0\t0\t0")
		self.items.append("%s\t%s\t0\t0\t0\t0" % (t,t))
		self.items.append("0\t0\t0\t0")
		self.items.append("0\t0\t0\t0\t0\t0")
		self.items.append("0\t0\t0\t0")
		self.items.append("0\t%s" % t)


class SummaryTHSection(GenericSection):
	def __init__(self):
		GenericSection.__init__(self,"Summary-TH")

	def set_time(self, tdata):
		t = tdata
		#4390	4390	0	0	0	0
		#0	0	0	0
		#0	1
		#0	0
		self.items.append("%s\t%s\t0\t0\t0\t0" % (t,t))
		self.items.append("0\t0\t0\t0")
		self.items.append("0\t1")
		self.items.append("0\t0")


class HRZonesSection(GenericSection):
	def __init__(self):
		GenericSection.__init__(self,"HRZones")

	def CreateEmpty(self):
		for i in [ 184, 166, 147, 129, 110, 92, 0, 0, 0, 0, 0 ]:
			self.items.append(i)




class NoteSection(GenericSection):
	def __init__(self):
		GenericSection.__init__(self,"Note")

class SwapTimesSection(GenericSection):
	def __init__(self):
		GenericSection.__init__(self,"SwapTimes")

#
# UNDOCUMENTED SECTIONS
#

class LapNamesSection(GenericSection):
	def __init__(self):
		GenericSection.__init__(self,"LapNames")

#
# TODO SECTIONS
#

class CoachSection(GenericSection):
	"TODO. This section is used only by Polar Coach HR monitor."
	def __init__(self):
		GenericSection.__init__(self,"Coach")

class HRCCModeChSection(GenericSection):
	def __init__(self):
		GenericSection.__init__(self,"HRCCModeCh")


