#############################################################
## JBert Programming for Scope
## Keyssa Inc.
#############################################################
import sys
import visa
import string
import struct
import numpy

from time import sleep
Version=0.1
DEBUG=True

#################################################################
##Version 0.1 --Dhileepan Thamotharam Release 09/28/2015
##				Base First Version
#################################################################

class JBert:
	def __init__(self,IPAddress="Default"):
		ResourceManager=visa.ResourceManager()
		if IPAddress=="Default":
			self.Object=ResourceManager.open_resource("TCPIP0::10.1.30.218::inst0::INSTR")
		else:
			Resource="TCPIP0::"+IPAddress+"::inst0::INSTR"
			self.Object=ResourceManager.open_resource(Resource)
		self.Object.timeout=10000
		self.Object.read_termination=""
		self.Object.write_termination=""
		
	def CheckInitialValues(self):
		try:
			Identification=self.Object.query("*IDN?")
			print Identification
			return True
		except:
			print "!!! BertCheckInitialValues Error"
			return False
	
	def ReadBER(self):
		
		self.Object.write("MEAS:FEM:cre?")
		self.Object.write("MEAS:FEM2:PAR:MERR 0")
		self.Object.write("MEAS:FEM2:PAR:MERR:MODE ENA")
		self.Object.write("MEAS:FEM2:PAR:PFCR 1.0E-12")
		self.Object.write("MEAS:GEN2:GO")
		while done == 0:
			done = self.Object.read("MEAS:GEN2:OPC? BLOCK")
			prgogress = self.Object.read("MEAS:GEN2:PROG?")
			print prgogress
			sleep(1)
		result = self.Object.read("MEAS:GEN2:PASS?")
		print result 
		
	
	def SelectPattern(self,Type="Default",Name="PRBS7"):
		if Type=="File":
			self.Object.write(":SOUR1:PATT:SEL FILENAME, \"%s\""%Name)
		elif Type=="Default":
			self.Object.write(":SOUR1:PATT:SEL PRBS7")
		
	def SetVoltage(self,Voltage=800):
		Voltage=Voltage/1000
		SetValue=Voltage/4
		SetString=":SOURce1:VOLT:HIGH "+str(SetValue)+"; LOW -"+str(SetValue)
		self.Object.write(SetString)
		sleep(1)
		SetString=":SOURce5:VOLT:HIGH "+str(SetValue)+"; LOW -"+str(SetValue)
		self.Object.write(SetString)
		sleep(1)
		
	def SetElectricalIdle(self,Option):
		if Option=="ON":
			self.Object.write(":OUTP1:EIDL ON")
			sleep(1)	
			self.Object.write(":OUTP5:EIDL ON")
			sleep(1)
		if Option=="OFF":
			self.Object.write(":OUTP1:EIDL OFF")
			sleep(1)	
			self.Object.write(":OUTP5:EIDL OFF")
			sleep(1)
	def SetDataRate(self,DataRate=5000000000):
		self.Object.write(":SOURce9:FREQ %d"%DataRate)
		sleep(1)
		self.Object.write(":SOUR5:MODE Schannel")
		sleep(1)
	
	def TurnOff(self):
		self.Object.write(":OUTP1:CENT DISC")
		sleep(1)

	def TurnOn(self):
		self.Object.write(":OUTP1:CENT CONN")
		sleep(1)

	
def main():
	import sys
	import visa
	import string
	import struct

	from time import sleep
	Bert=JBert("10.1.40.65")
	Bert.CheckInitialValues()
	
	case = input("Enter debug case to run: ")
	
	if case == 1: 
		Bert.TurnOff()
		Bert.SelectPattern("File","C:\N4903B\Pattern\clock.ptrn")
		Bert.SetDataRate(6000000000)
		Bert.SetVoltage(800.000000)
		Bert.TurnOn()
	elif case == 2:
		Bert.ReadBER()

if __name__ == '__main__':
	if (DEBUG):
		print "Debug Routine Being Called"
		print "JBert Libary Version %.2f"%Version
		main()
	else:
		print "Loaded JBert Libraries %.2f Successfully"%Version
	

