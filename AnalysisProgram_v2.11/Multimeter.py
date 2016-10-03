#############################################################
## Keithley Mutlimter Programming
## Keyssa Inc.
#############################################################
import sys
import visa
import string
import struct

from time import sleep
Version=0.1
DEBUG=False

#################################################################
##Version 0.1 --Dhileepan Thamotharam Release 10/03/2015
##				Base First Version
#################################################################


class Keithley_2110:
	def __init__(self,Address="Default"):
		try:
			ResourceManager=visa.ResourceManager()
			if Address=="Default":
				self.Object=ResourceManager.open_resource("USB0::0x05E6::0x2110::1424501::INSTR")
			else:
				self.Object=ResourceManager.open_resource(Address)
			self.Object.timeout=10000
			self.Object.read_termination=""
			self.Object.write_termination=""
		except:
			print "!!! Multimeter Cannot Be Reached and connected"
			exit(1)
			
	def WriteCommand(self,command):
		try:
			self.Object.write("%s\n"% command)
			sleep(2)
			return True
		except:
			print "!!! Multimeter Cannot Written"
			return False


	def Reset(self):
		try:		
			self.WriteCommand("*RST")
			sleep(2)
			return True
		except:
			print "!!! Multimeter Reset Error"
			return False

	def Clear(self):
		try:
			self.WriteCommand("*CLS")
			sleep(1)
			return True
		except:
			print "!!! Multimeter Clear Error"
			return False


    
	def QueryValues(self,query):
		try:
			queryValue=self.Object.query("%s\n"%query)
			return queryValue
		except:
			print "!!! Multimeter QueryValues Error"
			return False
    
	def CheckInitialValues(self):
		try:
			Identification=self.QueryValues("*IDN?")
			print Identification
			return True
		except:
			print "!!! Multimeter CheckInitialValues Error"
			return False

	def MeasVolt(self):
		try:
			Voltage=self.QueryValues(":MEASURE:VOLTage?")
			return Voltage
		except:
			print "!!! Multimeter Error Measuring Voltage"
			return False		
	def MeasTemp(self):
		try:
			sleep(1)
			self.WriteCommand(":TCOuple:TYPE K")
			sleep(1)
			Temp=self.QueryValues(":MEASURE:TCouple?")
			return Temp
		except:
			print "!!! Multimeter Error Measuring Temperature"
			return False	
def main():
	import sys
	import visa
	import string
	import struct

	from time import sleep

	Multi=Keithley_2110("USB0::0x05E6::0x2110::1424501::INSTR")
	Multi.CheckInitialValues()
	Multi.Reset()
	Value=float(Multi.MeasVolt())
	print "Voltage Measured is: %.2f"%Value

	Value=float(Multi.MeasTemp())
	print "Temperature Measured is: %.2f"%Value
    

    
if __name__ == '__main__':
	if (DEBUG):
		print "Debug Routine Being Called"
		print "Multimeter Libary Version %.2f"%Version
		main()
	else:
		print "Loaded Multimeter Libraries %.2f Successfully"%Version
	




