
import sys
import string
from mcp2210 import MCP2210
import os
from time import sleep
from time import strftime
import serial

Version=0.2
DEBUG=True

#################################################################
##Version 0.1 --Dhileepan Thamotharam Release 05/01/2015
##				Base First Version
##Version 0.2 --Eric Tamayo Release 06/07/2016
##              Added Suppourt for 104 ReTimer
##              Added Functions:
##                  Read_LockDetect, Read_PassAccu, Read_CalComplete
#################################################################

class HIDControl():
	def __init__(self,Identification,PID):
		self.dev = MCP2210(1240, PID)
		self.ID=Identification
		settings = self.dev.chip_settings
		settings.pin_designations[0] = 0x01  # GPIO 0 to chip select
		self.dev.chip_settings = settings  # Settings are updated on property assignment

	def Output_Print(self,OutString):
		TimeStamp=strftime("%H:%M:%S")
		print "%s\t%s"%(TimeStamp,OutString)

	def selectChip(self, Val):
		if(Val=="L1" or Val=="0"):
			chipID=0
		elif(Val=="L2" or Val=="1"):
			chipID=1
		else:
			print "Error Select Chip Specified"
			exit(1)
		spisettings = self.dev.transfer_settings
		spisettings.idle_cs = 0xff
		spisettings.active_cs = ~(0b00000001 << chipID) #'~' is a bitwise not
		self.dev.transfer_settings = spisettings
		self.slaveid = chipID
		
	def Write(self, Address, Value, mask=0xff, shift=0):
		Value=Value.lower()
		target=int(Address,16)
		data=int(Value,16)
		previousData = (self.Read(target) if mask != 0xff else 0x00)
		toWrite  = (previousData & (~ mask))    #previous data and not mask
		data = data << shift
		toWrite |= (data & mask)             #data and mask
		self.dev.transfer(chr(target * 2 + 1) + chr(toWrite) + chr(0))
		sleep(0.5)

	#target can be a register address, string, or tuple from C0spimap
	def Read(self, Address, mask=0xff, shift=0):
		target=int(Address,16)
		val = ord(self.dev.transfer(chr(target * 2) + chr(0) + chr(0))[1])
		val = val & mask
		val = val >> shift
		val=format(val,'#04x')
		return val

	def reTimerReset(self):
		self.Output_Print("\tReseting ReTimer...")
		#toggle reTimer reset 
		self.Write("0x2e","0x0a")
		sleep(1)
		self.Write("0x2e","0x4a")
		sleep(1)
		#enable reTimer
		self.Write("0x2e","0xca")
		#check if reset sucessful 
		if self.Read_PassAccu() == 0 or self.Read_CalComplete() == 0:
			self.Output_Print("\tReTimer Not Sucessfully Reset")
			self.Output_Print("\tPassAccu: " + str(self.Read_PassAccu()))
			self.Output_Print("\tCalComplete: " + str(self.Read_CalComplete()))
			exit(1)
		else:
			self.Output_Print("\tReTimer Reset")
			#self.Output_Print("PassAccu: " + str(self.Read_PassAccu()))
			#self.Output_Print("CalComplete: " + str(self.Read_CalComplete()))

	def Read_LockDetect(self):
		Value = int(self.Read("0x2a", 0x80, 7),0)
		return Value 

	def Read_VCOTuneNew(self):
		Value = self.Read("0x2d")
		return Value

	def Read_FreqLock(self):
		Value = int(self.Read("0x2a", 0x04, 2),0)
		return Value 

	def Read_SubRate(self):
		Value = int(self.Read("0x2a", 0x30, 4),0)
		return Value 
	
	def Read_PassAccu(self):
		Value = int(self.Read("0x2a", 0x40,6),0)
		return Value 

	def Read_CalComplete(self):
		Value = int(self.Read("0x2a", 0x08,3),0)
		#self.Output_Print("CalComplete: " + str(Value))
		return Value

	def Read_MiscStatus(self):
		self.Write("0x1b","0x20")
		Value=self.Read("0x1c")
		return Value  

	def Read_ReplicaOffset(self):
		self.Write("0x1b","0x21")
		Value=self.Read("0x1c")
		return Value  

	def Read_EyeHeight(self):
		self.Write("0x1b","0x22")
		Value=self.Read("0x1c")
		return Value  

	def Read_UpperSet(self):
		self.Write("0x1b","0x23")
		Value=self.Read("0x1c")
		return Value  

	def Read_SummOff(self):
		self.Write("0x1b","0x24")
		Value=self.Read("0x1c")
		return Value  

	def Read_RefSet(self):
		self.Write("0x1b","0x25")
		Value=self.Read("0x1c")
		return Value  

	def Read_GainSet(self):
		self.Write("0x1b","0x26")
		Value=self.Read("0x1c")
		return Value  

	def Reset_IC(self):
		self.Output_Print("Resetting IC")
		self.Write("0x15","0x91")
		sleep(2)        
		#dataToWrite = self.Read("0x15")
		#dataToWrite &= (~0x10)
		#dataToWrite |= (0x10 & 0x10)
		#self.Write("0x15", dataToWrite)
	def Disable_WP(self):
		try:
			self.Write("0x2f","0x92")
		except:
			self.Output_Print("Could Not Disable Write Protection")

def main():
	Board_A=HIDControl('Board_A',222)
	Board_B=HIDControl('Board_B',223)
	#Select Board A TX
	Board_A.selectChip('0')
	#Select Board B RX
	Board_B.selectChip('1')

	print Board_A.Read('0x00')
	print Board_B.Read('0x00')
	raw_input("")

	print("Disabling Write Protection...")
	Board_A.Write("0x2f","0x92")
	Board_B.Write('0x2f','0x92')
	print("Write Protection Disabled")
	case = input ("Enter Case to Debug: ")
	if case == 1:
		while(True):
			print("Reading ReTimer Reg for Board A...")
			print ("\tPass_Accu:" + str(Board_A.Read_PassAccu()) + " Lock_Detect:" + str(Board_A.Read_LockDetect()) + " Cal_Compl:" + str(Board_A.Read_CalComplete()))
			print("Reading ReTimer Reg for Board B...")
			print ("\tPass_Accu:" + str(Board_B.Read_PassAccu()) + " Lock_Detect:" + str(Board_B.Read_LockDetect()) + " Cal_Compl:" + str(Board_B.Read_CalComplete()))
			x = raw_input("Run Again?")
			if x == 'n':
				break
	if case == 2:
		Board_A.selectChip('0')
		sleep(1)
		print Board_A.Read_VCOTuneNew
		
		Board_A.selectChip('1')
		sleep(1)
		print Board_A.Read_VCOTuneNew
		
		Board_B.selectChip('0')
		sleep(1)
		print Board_B.Read_VCOTuneNew
		
		sleep(1)
		Board_B.selectChip('1')
		print Board_B.Read_VCOTuneNew
if __name__ == '__main__':
	if (DEBUG):
		print "Debug Routine Being Called"
		print "HID Libary Version %.2f"%Version
		main()
	else:
		print "Loaded HID Libraries %.2f Successfully"%Version
	




   
	
