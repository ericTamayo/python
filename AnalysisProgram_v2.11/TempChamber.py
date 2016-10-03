#!/usr/bin/env python

import minimalmodbus
import serial
import datetime
from time import sleep

Version=0.1
DEBUG=False

#################################################################
##Version 0.1 --Dhileepan Thamotharam Release 05/01/2015
##				Base First Version
#################################################################

class TestEquity_205H:
    def __init__(self,port):
        try:
            self.Object=minimalmodbus.Instrument(port,1,'rtu')
            self.Object.serial.xonxoff=False
            self.Object.serial.baudrate=9600
            self.Object.serial.parity=serial.PARITY_NONE
            self.Object.serial.bytesize=8
            self.Object.serial.port=port
            self.Object.serial.timeout=None
           
            sleep(1)
            if(DEBUG):
                print "Temperature Chamber is Connected to Port %s"%port
        except:
            print "Temperature Chamber is Not Connected or Cannot be detected"
            exit(0)
		    
    def READ_TEMP(self):

		read_value=self.Object.read_register(100,1)
		sleep(5)
		return read_value

    def TWOS_COMPLEMENT(self,value,bits):
		if value < 0:
			value = ( 1<<bits ) + value
		formatstring = '{:0%ib}' % bits
		return formatstring.format(value) 
		
    def WRITE_TEMP(self,value):
		read_accuracy=self.Object.read_register(606,1)
		sleep(2)
		set_value=int(float(value)/float(read_accuracy))
		set_value=int(self.TWOS_COMPLEMENT(set_value,16),2)
		self.Object.write_register(300,set_value)
		sleep(2)
		if (value<0):
			tempValueRead=self.Object.read_register(100,1)/float(read_accuracy)
			tempValueReadTwosComplement=self.TWOS_COMPLEMENT(int(tempValueRead),16)
			feedback_read=int(self.TWOS_COMPLEMENT(int(tempValueRead),16),2)
			sleep(2)
			while(abs(float(feedback_read)-float(set_value))>10):
				sleep(10)
				print "Please Wait While Temperature is set to: %s"%value
				tempValueRead=self.Object.read_register(100,1)/float(read_accuracy)
				tempValueReadTwosComplement=self.TWOS_COMPLEMENT(int(tempValueRead),16)
				feedback_read=int(self.TWOS_COMPLEMENT(int(tempValueRead),16),2)
		else:
			feedback_read=self.Object.read_register(100,1)
			sleep(2)
			while(abs(float(feedback_read)-float(value))>1):
				sleep(10)
				print "Please Wait While Temperature is set to: %s Current Temperature is: %.2f"%(value,float(feedback_read))
				feedback_read=self.Object.read_register(100,1)
		sleep(5)

    def READ_HUMIDITY(self):
        read_value=self.Object.read_register(104,1)
        sleep(5)
        return read_value

    def WRITE_HUMIDITY(self,value):
        read_accuracy=self.Object.read_register(606,1)
        sleep(2)
        set_value=int(float(value)/float(read_accuracy))
        self.Object.write_register(319,set_value)
        sleep(2)
        feedback_read=self.Object.read_register(104,1)
        sleep(2)
        while(abs(float(feedback_read)-float(value))>1):
            sleep(10)
            print "Please Wait While Humidity is set to: %s Current Humidity is: %.2f"%(value,float(feedback_read))
            feedback_read=self.Object.read_register(104,1)
        sleep(5)

class TestEquity_107:
    def __init__(self,port):
        try:
            self.Object=minimalmodbus.Instrument(port,1,'rtu')
            self.Object.serial.baudrate=9600
            self.Object.serial.parity=serial.PARITY_NONE
            self.Object.serial.bytesize=8
            self.Object.serial.port=port
            self.Object.serial.timeout=None
            sleep(1)
            if(DEBUG):
                print "Temperature Chamber is Connected to Port %s"%port
        except:
            print "Temperature Chamber is Not Connected or Cannot be detected"
            exit(0)
		    
    def READ_TEMP(self):
        read_value=self.Object.read_float(27586)
        sleep(5)
        return read_value
	
    def WRITE_TEMP(self,value):
        self.Object.write_float(2782,value)
        sleep(2)
        feedback_read=self.Object.read_float(27586)
        sleep(2)
        while(abs(float(feedback_read)-float(value))>1):
            sleep(10)
            print "Please Wait While Temperature is set to: %s Current Temperature is: %.2f"%(value,float(feedback_read))
            feedback_read=self.Object.read_float(27586)	
        sleep(5)
		
def main():
    TC=TestEquity_205H('COM3')
    print "Temperature Read is: %.2f"%value_read_temp
    TC.WRITE_TEMP(-1)
    value_read_humidity=TC.READ_HUMIDITY()
    print "Now set the Humidity"
    TC.WRITE_HUMIDITY(50)

if __name__ == '__main__':
    if (DEBUG):
        print "Debug Routine Being Called"
        print "TempChamber Libary Version %.2f"%Version
        main()
    else:
        print "Loaded TempChamber Libraries %.2f Successfully"%Version
	
		
