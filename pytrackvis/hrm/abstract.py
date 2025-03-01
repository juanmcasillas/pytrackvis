#!/usr/bin/env python

#
# Juan M. Casillas
# HRM & PPD parser and reconstructor
# Used to fix the altitude and bugs in the PPD
#
# see http://www.polar.com/sites/default/files/Polar_HRM_file%20format.pdf
# see http://www.polar.com/sites/default/files/Polar_PWD_PDD_file%20format.pdf
#

#
# Global format
# The data is stored in ASCII format. CR and LF (0Dh and 0Ah) at the end of each line.
# There is one empty line between each data section. The data section name is separated
# from actual data always with brackets [ ].
#

import os
import sys
import time
import codecs


class AbstractSection:
	"Generate an abstraction for the generic section"

	def __init__(self, name=""):
		self.rawdata = None
		self.name = name
		#self.items = {}

	def ExtractName(self, data):

		if not data:
			raise Exception("Section has invalid name")


		line = data.splitlines()[0]

		if line.startswith('[') and line.endswith(']'):
			return line[1:-1]
		else:
			raise Exception("Section has invalid name")

	def ParseData(self, line):	raise Exception("Abstract class: child must redefine it")
	def PrintData(self):		raise Exception("Abstract class: child must redefine it")
	def ExportData(self):		raise Exception("Abstract class: child must redefine it")
	def Validate(self):			raise Exception("Abstract class: child must redefine it")
	def CreateEmtpy(self):		raise Exception("Abstract class: child must redefine it")

	# tools

	def ParsePolarTime(self, ptime):

		d = 0
		h,m,s = ptime.split(':')
		if s.find('.') > -1:
			s,d = s.split('.')
		return map(int, [ h, m, s, d])


	def ParseFromData(self, data):

		# Check if section name is the same as current section

		lines = data.splitlines()
		first_line = lines[0]
		lines = lines[1:]

		if first_line.startswith('[') and first_line.endswith(']') and first_line[1:-1] == self.name:
			pass
		else:
			raise Exception ("Section expected %s, get %s" % (self.name, first_line[1:-1]))

		# ITEMS section. This change from element to element, so implement it as a method
		for line in lines:
			self.ParseData(line)


	def PrintHeader(self):
		r = ""
		r += "{:<20} {:<20} {:>38}\r\n".format( "Entry Name",			"File Data",						"Processed Info"					)
		r += "=" * 80
		r += "\r\n"
		return r

	def Print(self):
		"print the data for debugging"
		r = ""
		r += "Section [%s]\r\n" % self.name
		r += self.PrintData()
		r += "\r\n"

		return r


	def Export(self):
		"export the section to HRM/POLAR compatible format"
		r = ""
		r += "[%s]\r\n" % self.name
		r += self.ExportData()
		r += "\r\n"

		return r


#use this one by default, then override it if needed

class GenericSection(AbstractSection):
	"Implement a common class that enables reading and writting without modification"

	def __init__(self, name=""):
		AbstractSection.__init__(self,name)
		self.items = []

	def ParseData(self, line):
		self.items.append(line)

	def PrintData(self):
		r = self.PrintHeader()
		for i in self.items:
			r += "{:<20} {:<20} {:>38}\r\n".format( i, self.items[0],self.items[0])
		return r

	def ExportData(self):
		r = ""
		for i in self.items:
			r += "%s\r\n" % i
		return r


	def Validate(self):
		pass

	def CreateEmpty(self):
		pass








class AbstractParser:
	"A generic parser for the files"

	def __init__(self):
		self.rawdata = None
		self.sections = {}

	def Print(self):
		r = ""
		for s in self.sections.keys():
			print(s)
			r += self.sections[s].Print()
		return r

	def Export(self):
		r = ""
		section_list = ['Params'	 ,
						'Coach'		 ,
						'Note'		 ,
						'HRZones'	 ,
						'SwapTimes'	 ,
						'HRCCModeCh' ,
						'IntTimes'	 ,
						'IntNotes'	 ,
						'ExtraData'  ,
						'LapNames'   ,
						'Summary-123',
						'Summary-TH' ,
						'Trip'		 ,
						'HRData' ]

		for section in section_list:
			if section in self.sections.keys():
				r += self.sections[section].Export()

		return r


	def ParseFromFile(self, fname):
		f = open(fname,'rb')
		try:

			self.rawdata = f.read()
		except Exception as e:
			print("Error opening (%s): %s" % (fname, e))
		finally:
			f.close()


	def Validate(self):

		for s in self.sections.keys():

			self.sections[s].Validate()


class AbstractManager:
	def __init__(self, verbose=0):
		self.verbose = verbose

	def add_ele_extension(self, filen):
		"c:\\gpx10file.gpx -> C:\\gpx10file_ele.gpx"

		abspath = os.path.abspath(filen)

		fn = os.path.basename(os.path.splitext(abspath)[0])
		ex = os.path.splitext(abspath)[1]

		fn = "%s%s%s_ele%s" % (os.path.dirname(abspath), os.sep, fn, ex)
		return fn

	def replace_or_overwrite(self, fn, data):
		fnl = fn
		if not self.overwrite:
			# add the ele extension to the file name.
			fnl = self.add_ele_extension(fn)

		outf = file(fnl,"wb")
		outf.write(data)
		outf.close()

		if self.verbose >= 1:
			print(self.LOG("Data written to '%s'" % fnl))


	def create_or_overwrite(self, fn, data):
		fnl = fn
		if not self.overwrite and os.path.exists(os.path.abspath(fnl)):
			# add the ele extension to the file name.
			fnl = self.add_ele_extension(fn)

		# support unicode.
		
		if isinstance(data,unicode):
			outf = codecs.open(fnl, "wb", 'utf-8')
		else:
			outf = file(fnl,"wb")
		outf.write(data)
		outf.close()

		if self.verbose >= 1:
			print(self.LOG("Data written to '%s'" % fnl))

	def LOG(self, msg):
		dt = time.strftime("%Y/%m/%d %H:%M:%S",time.localtime())
		return "[%s] %s" % (dt, msg)

