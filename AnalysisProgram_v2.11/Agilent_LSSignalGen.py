import sys
import visa
import string
import struct
import numpy

from time import sleep
DEBUG=False
class Agilent_LS:
	def __init__(self,IPAddress="Default"):
		ResourceManager=visa.ResourceManager()
		if IPAddress=="Default":
			self.Object=ResourceManager.open_resource("GPIB0::20::INSTR")
		else:
			self.Object=ResourceManager.open_resource(IPAddress)
		self.Object.timeout=10000
		self.Object.read_termination=""
		self.Object.write_termination=""
		
	def CheckInitialValues(self):
		try:
			Identification=self.Object.query("*IDN?")
			print Identification
			return True
		except:
			print "!!! Agilent_LS_CheckInitialValues Error"
			return False
	def Reset(self):
		self.Object.write("*RST")
		self.Object.write("*CLS")
		

	def SetPRBSPattern(self):
		self.Object.write(":ARM:SOUR IMM")
		self.Object.write(":DIG:PATT:SEGM1:TYPE1 PRBS")
		self.Object.write(":DIG:PATT:SEGM1:TYPE2 PRBS")
		self.Object.write(":DIG:PATT ON")

		self.Object.write(":DIG:PATT:SEGM1:LENG 2032")
		self.Object.write(":DIG:PATT:SEGM2:LENG 0")
		self.Object.write(":DIG:PATT:SEGM3:LENG 0")
		self.Object.write(":DIG:PATT:SEGM4:LENG 0")
		self.Object.write(":DIG:PATT:LOOP 1")
		self.Object.write(":DIG:PATT:PRBS 7")
		self.Object.write(":DIG:SIGN:FORM NRZ")
		self.Object.write(":DIG:PATT ON")
		self.Object.write(":DIG:PATT:UPD ONCE")


	def TurnOFF(self):
		self.Object.write(":OUTP1 OFF")
		self.Object.write(":OUTP1:COMP OFF")
		self.Object.write(":OUTP2 OFF")
		self.Object.write(":OUTP2:COMP OFF")

	def TurnON(self,option="ALL"):
		if option=="1":
			self.Object.write(":OUTP1 ON")
		elif option=="1_COMP":
			self.Object.write(":OUTP1:COMP ON")
		elif option=="2":
			self.Object.write(":OUTP2 ON")
		elif option=="2_COMP":
			self.Object.write(":OUTP2:COMP ON")
		else:
			self.Object.write(":OUTP1 ON")
			self.Object.write(":OUTP1:COMP ON")
			self.Object.write(":OUTP2 ON")
			self.Object.write(":OUTP2:COMP ON")
	
	def SetFrequency(self,value):
		self.Object.write(":TRIG:SOUR INT")
		FreqString=':FREQ '+value
		self.Object.write(FreqString)
		self.Object.write(":PULS:DCYC1 50PCT")

	def SetVoltage(self,Value):
		self.Object.write(":HOLD VOLT")
		VoltString=":VOLT1:HIGH "+str(Value)
		self.Object.write(VoltString)
		VoltString=":VOLT1:LOW 0V"
		self.Object.write(VoltString)
def main():
	import sys
	import visa
	import string
	import struct

	from time import sleep
	LS=Agilent_LS()
	LS.CheckInitialValues()
	LS.Reset()
	LS.TurnOFF()
	LS.SetPRBSPattern()
	LS.SetFrequency("300MHz")
	LS.SetVoltage("1.0V")
	LS.TurnON("1")
	sleep(5)
	print "Done Setting Values"

	


if __name__ == '__main__':
	if (DEBUG):
		print "Debug Routine Being Called"
		main()
	