#!/usr/bin/env python
import serial
from time import sleep
Version=0.1
DEBUG=False

#################################################################
##Version 0.1 --Dhileepan Thamotharam Release 05/01/2015
##				Base First Version
#################################################################





##########################################################################
##Support PowerSupply KA3005P Programmable Power Supply
##Keyssa Inc.
##########################################################################
class KA3005P:
	def __init__(self,port):
		try:
			self.ser =serial.Serial(port, 9600, timeout=1)
			if(DEBUG):
				print "Power Supply is Connected to Port %s" %port
		except:
			print "Power Supply is Not Connected or Cannot be detected"
			exit(0)	
			
	##################################################
	##Turn On the Power Supply
	##################################################
	def ON(self):
		self.COMMAND("OUT1")
		#if(DEBUG):
		#	print "PowerSupply Power Supply is Connected"
        #sleep(1)
	
	##################################################
	##Turn OFF the Power Supply
	##################################################
	def OFF(self):
		self.COMMAND("OUT0")
		#if(DEBUG):
		#	print "PowerSupply Power Supply is Disconnected"
        #sleep(1)
	##################################################
	##Turn On Over Current Protection 
	##################################################
	def ON_OCP(self):
		self.COMMAND("OCP1")

	##################################################
	##Turn Off Over Current Protection
	##################################################
	def OFF_OCP(self):
		self.COMMAND("OCP0")
		
	##################################################
	##Turn ON Over Voltage Protection
	##################################################	
	def ON_OVP(self):
		self.COMMAND("OVP1")
		
	##################################################
	##Turn Off Over Voltage Protection
	##################################################
	def OFF_OVP(self):
		self.COMMAND("OVP0")
	
	##################################################
	##Set Current Internal Function Not to be used from outside
	##################################################
	def S_CURRENT(self,channel,value):
		self.COMMAND("ISET%s:%s" % ( channel, value))

	##################################################
	##Set Voltage Internal Function Not to be used from outside
	##################################################
	def S_VOLTAGE(self,channel,value):
		self.COMMAND("VSET%s:%s" % ( channel, value))
  
	##################################################
	##Send Serial Data Command
	##################################################
	def COMMAND(self,text):
		sleep(0.5)
		self.ser.write(text)

	
	##################################################
	##Set Voltage
	##################################################
	def SET_VOLTAGE(self,value):
		self.OFF()
		self.S_VOLTAGE(1,value)
		sleep(1)
		self.ON_OCP()
		sleep(1)
		
	
	##################################################
	##Get Output Current
	##################################################
	def GET_OUTPUT_CURRENT(self):
		return self.FEEDBACK("IOUT1?")

	##################################################
	##Get Output Voltage
	##################################################
	def GET_OUTPUT_VOLTAGE(self):
		return self.FEEDBACK("VOUT1?")
	
	##################################################
	##Feedback from Device
	##################################################
	def FEEDBACK(self,text):
		self.COMMAND(text)
		return self.ser.read(200)
	
	##################################################
	##Set Current
	##################################################		
	def SET_CURRENT(self,value):
		self.OFF()
		self.S_CURRENT(1,value)
		sleep(2)
		self.ON_OVP()
		sleep(2)

	##################################################
	##Set Voltage and Current CONFIRMATION
	##################################################		
	def SET_VOLTAGE_CURRENT(self,valueVoltage,valueCurrent):
		self.OFF()
		self.S_VOLTAGE(1,valueVoltage)
		self.S_CURRENT(1,valueCurrent)
		
		self.ON_OVP()
		self.ON_OCP()
		self.ON()
		sleep(1)
		OutputVolt=self.GET_OUTPUT_VOLTAGE()
		if(abs(float(valueVoltage)-float(OutputVolt))>0.5):
			self.SET_VOLTAGE_CURRENT(valueVoltage,valueCurrent)

	##################################################
	##Close Korad Power Supply
	##################################################		
	def CLOSE_POWER_SUPPLY(self):
		if(self.ser.isOpen()):
			self.ser.close()

##########################################################################
##Support PowerSupply KA3305P Programmable Power Supply
##Keyssa Inc.
##########################################################################
class KA3305P:
	def __init__(self,port):
		try:
			self.ser =serial.Serial(port, 9600, timeout=1)
			self.COMMAND("TRACK0")
			if(DEBUG):
				print "Power Supply is Connected to Port %s" %port
		except:
			print "Power Supply is Not Connected or Cannot be detected"
			exit(0)	
			
	##################################################
	##Turn On the Power Supply (Please Be Aware All channels are turned on same time)
	##################################################
	def ON(self):
		self.COMMAND("OUT1")
		if(DEBUG):
			print "PowerSupply Power Supply is Connected"
		#sleep(1)
	
	##################################################
	##Turn OFF the Power Supply
	##################################################
	def OFF(self):
		self.COMMAND("OUT0")
		if(DEBUG):
			print "PowerSupply Power Supply is Disconnected"
        #sleep(1)
	##################################################
	##Turn On Over Current Protection 
	##################################################
	def ON_OCP(self):
		self.COMMAND("OCP1")

	##################################################
	##Turn Off Over Current Protection
	##################################################
	def OFF_OCP(self):
		self.COMMAND("OCP0")
		
	##################################################
	##Turn ON Over Voltage Protection
	##################################################	
	def ON_OVP(self):
		self.COMMAND("OVP1")
		
	##################################################
	##Turn Off Over Voltage Protection
	##################################################
	def OFF_OVP(self):
		self.COMMAND("OVP0")
	
	##################################################
	##Set Current Internal Function Not to be used from outside
	##################################################
	def S_CURRENT(self,channel,value):
		self.COMMAND("ISET%s:%s" % ( channel, value))

	##################################################
	##Set Voltage Internal Function Not to be used from outside
	##################################################
	def S_VOLTAGE(self,channel,value):
		self.COMMAND("VSET%s:%s" % ( channel, value))
  
	##################################################
	##Send Serial Data Command
	##################################################
	def COMMAND(self,text):
		sleep(1)
		self.ser.write(text)

	
	##################################################
	##Set Voltage
	##################################################
	def SET_VOLTAGE(self,Channel,value):
		self.OFF()
		self.S_VOLTAGE(Channel,value)
		sleep(1)
		self.ON_OCP()
		sleep(1)
	
	##################################################
	##Get Output Current
	##################################################
	def GET_OUTPUT_CURRENT(self,Channel):
		if Channel==1:
			return self.FEEDBACK("IOUT1?")
		elif Channel==2:
			return self.FEEDBACK("IOUT2?")

	##################################################
	##Get Output Voltage
	##################################################
	def GET_OUTPUT_VOLTAGE(self,Channel):
		if Channel==1:
			return self.FEEDBACK("VOUT1?")
		elif Channel==2:
			return self.FEEDBACK("VOUT2?")
	##################################################
	##Feedback from Device
	##################################################
	def FEEDBACK(self,text):
		self.COMMAND(text)
		return self.ser.read(200)
	
	##################################################
	##Set Current
	##################################################		
	def SET_CURRENT(self,Channel,value):
		self.OFF()
		self.S_CURRENT(Channel,value)
		sleep(2)
		self.ON_OVP()
		sleep(2)

	

	##################################################
	##Set Voltage and Current CONFIRMATION
	##################################################		
	def SET_VOLTAGE_CURRENT(self,Channel,valueVoltage,valueCurrent):
		self.OFF()
		self.S_VOLTAGE(Channel,valueVoltage)
		self.S_CURRENT(Channel,valueCurrent)
		self.ON_OVP()
		self.ON_OCP()
		self.ON()
		sleep(1)
		OutputVolt=self.GET_OUTPUT_VOLTAGE(Channel)
		if(abs(float(valueVoltage)-float(OutputVolt))>0.5):
			self.SET_VOLTAGE_CURRENT(Channel,valueVoltage,valueCurrent)

	##################################################
	##Close Korad Power Supply
	##################################################		
	def CLOSE_POWER_SUPPLY(self):
		if(self.ser.isOpen()):
			self.ser.close()
					
def main():
    Korad=KA3005P("COM18")
    Korad.OFF()
    Korad.SET_VOLTAGE(1.2)
    Korad.SET_CURRENT(0.2)

    Korad.ON()
   

if __name__ == '__main__':
	if (DEBUG):
		print "Debug Routine Being Called"
		print "PowerSupply Libary Version %.2f"%Version
		main()
	else:
		print "Loaded PowerSupply Libraries %.2f Successfully"%Version
	
