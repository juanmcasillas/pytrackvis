import os
import sys
import time

from .abstract import *
from .sections.params import *
from .sections.trip import *
from .sections.inttimes import *
from .sections.hrdata import *

from .sections.generic import *

# ordered list of sections
SectionList = [			'Params'	 ,
						'Note'		 ,
						'IntTimes'	 ,
						'ExtraData'  ,
						'Summary-123',
						'Summary-TH' ,
						'HRZones'	 ,
						'SwapTimes'	 ,
						'Trip'		 ,




						'HRData'
]

SectionFactory = {
	'Params':		ParamsSection 			,
	'Coach':		CoachSection 			,
	'Note': 		NoteSection 			,
	'HRZones': 		HRZonesSection 			,
	'SwapTimes':	SwapTimesSection 		,
	'HRCCModeCh': 	HRCCModeChSection 		,
	'IntTimes': 	IntTimesSection 		,
	'IntNotes': 	IntNotesSection 		,
	'ExtraData': 	ExtraDataSection 		,
	'LapNames':		LapNamesSection         ,
	'Summary-123': 	Summary123Section 		,
	'Summary-TH': 	SummaryTHSection 		,
	'Trip': 		TripSection 			,
	'HRData': 		HRDataSection 			,
	# undocummented sections, but appear in the files

}


class HRMParser(AbstractParser):
	def __init__(self):
		AbstractParser.__init__(self)
		self.sections = {}

	def ParseFromFile(self, fname):

		AbstractParser.ParseFromFile(self, fname)

		# split using the two lines (defined in the documentation
		for section in self.rawdata.split("\r\n\r\n"):
			#
			# Section now has the chunck of raw data without processing.
			# note that if you fail, you get a malformed file
			#
			if not section:
				continue
			section_name =  AbstractSection().ExtractName(section)
			self.sections[section_name] = SectionFactory[section_name]()
			self.sections[section_name].ParseFromData(section)

		self.Validate()

	def CreateEmpty(self):
			for s in SectionFactory.keys():
				self.sections[s] = SectionFactory[s]()
				self.sections[s].CreateEmpty()




	# special methods


	def DebugSections(self, verbose):
		if verbose >= 2:
			print(self.sections['Params'].Print())

		if verbose >= 3:
			# rcx5 and rc3 don't include this section by default in raw hrms

			if 'Trip' in self.sections.keys():
			    print(self.sections['Trip'].Print())
			print(self.sections['IntTimes'].Print())
			print(self.sections['HRData'].Print(self.sections['Params'].mode))