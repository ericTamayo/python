#############################################################
## BertScope Programming
## Keyssa Inc.
#############################################################
import socket, re, time, visa, math, sys, datetime, csv, traceback, os
from sys import argv
import numpy as np
from threading import Timer
from datetime import timedelta, datetime
from time import sleep

Version=0.1
DEBUG=True

#################################################################
##Version 0.1 --Dhileepan Thamotharam Release 05/01/2015
##				Base First Version
#################################################################
class BertScope:
	bert=''
	def __init__(self,ipaddress,port=23):
		try:			
			self.bert=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.bert.connect((ipaddress,port))
		except:
			print "!!! BertScope Cannot Be Reached and connected"
			exit(1)

	def cmdBert(self, cmd):
		l = cmd.split()    
		l[0] = re.sub('_',':',l[0])
		cmd = ' '.join(l)
		if not cmd.endswith('\n'):
			cmd += '\n'
		self.bert.send( cmd )
		#if '?' in cmd or cmd.startswith('MGET'):
		#	print cmd, self.bert.recv(1024)
		#else:
		#	print cmd

	def getRespBert(self, cmd):
		l = cmd.split()    
		l[0] = re.sub('_',':',l[0])
		cmd = ' '.join(l)
		if not cmd.endswith('\n'):
			cmd += '\n'
		self.bert.send( cmd )
		if '?' in cmd or cmd.startswith('MGET'):
			return self.bert.recv(1024)
		else:
			return ''    

	def CheckInitialValues(self):
		try:
			self.bert.send('*IDN?\n')
			return self.bert.recv(1024)

		except:
			print "!!! BertScope CheckInitialValues Error"
			exit(1)

	def setGenClockRate(self, rate = 1250000000):
		self.cmdBert('GEN:ICL ' + str(rate))

	def setGenClockDivisor(self, value = 1):
		self.cmdBert('GEN:CLKDIV ' + str(value))

    #Enable Generator SSC
	def enGenSSC(self, enable = 1):
		self.cmdBert('GEN:SSCMOD:ENAB ' + str(enable))
	
	#Load Bert Generator Pattern <PN7 | PN11 | PN15 | PN20 | PN23 | PN31 | USTart | UGRab | USHift | AUTomatic | ALLZERO>"""
	def loadGenPatt(self, genPattern):
		self.cmdBert('GEN:PATT ' + genPattern)

	def setClockPosOutputLevels(self, Vhigh=500, Vlow=-500): 
		self.cmdBert('GEN:COP:SLVH ' + str(Vhigh))
		self.cmdBert('GEN:COP:SLVL ' + str(Vlow))
		time.sleep(2)
        
	def getClockPosOutputLevels(self): 
		pos = self.getRespBert('GEN:COP:SLVH?')
		neg = self.getRespBert('GEN:COP:SLVL?')
		print " Vhigh of Data+ Output = ", pos
		print " Vlow of Data+ Output = ",neg
		return(0)
        
	def setClockNegOutputLevels(self, Vhigh=500, Vlow=-500): 
		self.cmdBert('GEN:CON:SLVH ' + str(Vhigh))
		self.cmdBert('GEN:CON:SLVL ' + str(Vlow))
		time.sleep(2)
        
	def getClockNegOutputLevels(self): 
		pos = self.getRespBert('GEN:CON:SLVH?')
		neg = self.getRespBert('GEN:CON:SLVL?')
		print " Vhigh of Data- Output = ", pos
		print " Vlow of Data- Output = ",neg
		return(0)
	
	def LinkPosNegClocks(self,enable=1):
		self.cmdBert('GEN:COUT:LPNS '+str(enable))
		time.sleep(2)

	def TurnOffOutput(self):
		self.cmdBert('GEN:COP:ENAB 0')
		self.cmdBert('GEN:CON:ENAB 0')
		self.cmdBert('GEN:DOP:ENAB 0')
		self.cmdBert('GEN:DON:ENAB 0')

	def TurnOnOutput(self):
		self.cmdBert('GEN:COP:ENAB 1')
		self.cmdBert('GEN:CON:ENAB 1')
		self.cmdBert('GEN:DOP:ENAB 1')
		self.cmdBert('GEN:DON:ENAB 1')

	def MeasureBER(self):
		self.cmdBert('VIEW DET')
		time.sleep(5)
		self.cmdBert('DET:PDC') ##Initiate Auto Align
		time.sleep(5)
		self.cmdBert('DET:RESE') ##Reset All
		self.cmdBert('RSTATE 1')
		response=self.getRespBert('RSTATE?')
		response=self.getRespBert('DET:DCS?')
		self.cmdBert('DET:RUIN 20')
		time.sleep(30)

		response=self.getRespBert('DET:BITS?')
		#print "Number of Bits is: %s"%response
		response=self.getRespBert('DET:ERR?')
		#print "Number of Errors is: %s"%response
		BER_Value=self.getRespBert('DET:BER?')
		#print "BER is: %s"%BER_Value
		self.cmdBert('RSTATE 0')
		return BER_Value
		
	def MeasureJitter(self):	
		self.cmdBert('VIEW JITTER')
		self.cmdBert('RSTATE 1')
		time.sleep(30)
		response=self.getRespBert('JITT:TST?')
		#print "Response back is %s"%response
		if response=='OK':
			TJ=self.getRespBert('JITT:TJIT?')
			#print "Total Jitter is %s"%TJ
			DJ=self.getRespBert('JITT:DJITter?')
			#print "Deterministic Jitter is %s"%DJ
			RJ=self.getRespBert('JITT:RJITter?')
			#print "Random Jitter is %s"%RJ
		self.cmdBert('RSTATE 0')
		returnString=TJ+","+DJ+","+RJ
		returnString
		return returnString

	def ShowEye(self):
		self.cmdBert("VIEW EYE")
		time.sleep(5)
		self.cmdBert('RST 1')		
		self.cmdBert("EYE:ASM EOP")
		
	def closeBert(self):
		self.bert.close()

def main():
	Bert=BertScope("10.1.40.72")
	Bert.cmdBert("VIEW GEN")
	#Bert.TurnOffOutput()
	Bert.setGenClockRate(5000000000)
	Bert.setGenClockDivisor(1)
	Bert.enGenSSC(0)
	Bert.loadGenPatt('PN7')
	Bert.LinkPosNegClocks(0)
	Bert.setClockPosOutputLevels(200,-200)
	Bert.setClockNegOutputLevels(200,-200)
	Bert.LinkPosNegClocks(1)
	#Bert.TurnOnOutput()
	print Bert.MeasureBER()
	print Bert.MeasureJitter()
	Bert.cmdBert("VIEW EYE")



if __name__ == '__main__':
	if (DEBUG):
		print "Debug Routine Being Called"
		print "BertScope Libary Version %.2f"%Version
		main()
	else:
		print "Loaded BertScope Libraries %.2f Successfully"%Version
	
