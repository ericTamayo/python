import sys
import string
from HIDController import *
from PowerSupply import *
import os
from time import sleep
from time import strftime

Version=0.2
DEBUG=False

#################################################################
##Version 0.1 --Eric Tamayo 9-14-2016
##				Base First Version
##Version 0.2 --Eric Tamayo 9-15-2016
##				Added Diagnostic Failure Report For Failures 
##					- Save Retimer Register and VCO Tune New
#################################################################

def Output_Print(OutString):
	TimeStamp=strftime("%H:%M:%S")
	print "%s\t%s"%(TimeStamp,OutString)

def IntializeBoard_A(boardName,PID):
	global Board_A
	try:
		Output_Print("Itializing " +  boardName + "...")
		Board_A=HIDControl(boardName,PID)
		Output_Print("\t" + boardName + " Intialized")
	except:
		Error()
		Output_Print(boardName + " Intialization Unsucessful...")
		Output_Print("DEBUG:")
		Output_Print("\t 1. Check PID")
		Output_Print("\t 2. Disconnect and reconnect HID controller")
		sys.exit()
def IntializeBoard_B(boardName,PID):
	global Board_B
	try:
		Output_Print("Itializing " +  boardName + "...")
		Board_B=HIDControl(boardName,PID)
		Output_Print("\t" + boardName + " Intialized")
	except:
		Error()
		Output_Print(boardName + " Intialization Unsucessful...")
		Output_Print("DEBUG:")
		Output_Print("\t 1. Check PID")
		Output_Print("\t 2. Disconnect and reconnect HID controller")
		sys.exit()
def InitializePowerSupply(comport):
	global PowerSupply
	Output_Print("Intializing Power Supply...")
	try:
		PowerSupply=KA3005P(comport)
		Output_Print("\tPower Supply Initialized")
		return
	except:
		pass
	
	try:
		PowerSupply=KA33005P(comport)
		Output_Print("\tPower Supply Initialized")
	except:
		Error()
		Output_Print("Could Not Intialize Power Supply")
		Output_Print("DEBUG:")
		Output_Print("\t1. Check Comport")
		sys.exit()

def PowerSupplyToggle():
	PowerSupply.OFF()
	sleep(5)
	PowerSupply.ON()
	sleep(5)
	
def SetPowerSupplyOutput(voltage,current):
	Output_Print("Disabling PowerSupply")
	PowerSupply.OFF()
	PowerSupply.SET_VOLTAGE(voltage)
	PowerSupply.SET_CURRENT(current)
	PowerSupply.OFF_OCP()
	PowerSupply.OFF_OVP()

def Error():
	Output_Print("!!!ERROR!!!")	

def DiagnosticReport(judge, fail_count):
	currentTime = strftime("%H:%M:%S")
	tempMem = [] 
	tempMem.append("\n"+judge+" total number of failure:"+str(fail_count))
	tempMem.append("\nHost:")
	tempMem.append("\nLockDetect:%s,CalComplete:%s,SubRate:%s,FreqLock:%s,VCOTuneNew:%s"%(Host.Read_LockDetect(),Host.Read_CalComplete(),Host.Read_SubRate(),Host.Read_FreqLock(),Host.Read_VCOTuneNew()))
	tempMem.append("\nDevice:")
	tempMem.append("\nLockDetect:%s,CalComplete:%s,SubRate:%s,FreqLock:%s,VCOTuneNew:%s\n\n"%(Device.Read_LockDetect(),Device.Read_CalComplete(),Device.Read_SubRate(),Device.Read_FreqLock(),Device.Read_VCOTuneNew()))
	returnMe = ''.join(tempMem)
	return returnMe

def main():
	###Intialize Output File###
	#filename = "test"
	filename = raw_input(strftime("%H:%M:%S")+ '\tOutput File Name:')
	dir_path = os.path.dirname(os.path.realpath(__file__))
	Output_Print("Output Path:%s\\%s"%(dir_path,filename))
	#Check for an Ouput Dir
	if not os.path.exists("Data"):
		os.makedirs("Data")
	###Intialize Output File###

	###Intialization###
	IntializeBoard_A("Host",222)
	IntializeBoard_B("Device",223)
	InitializePowerSupply("COM6")
	global Host
	global Device
	global mem
	mem = ""
	Host = Board_A
	Device = Board_B
	###Intialization###
	
	###Power Supply Parameters###
	SetPowerSupplyOutput(3.30,1.00)
	###Power Supply Parameters###

	###Chip Select###
	#Select Host TX
	Host.selectChip('1')
	#Select Decice RX
	Device.selectChip('0')
	###Chip Select###
	
	Output_Print("Disabling Host Write Protection...")
	Host.Disable_WP()
	Output_Print("\tHost Write Protection Disabled")
	Output_Print("Disabling Device Write Protection...")
	Device.Disable_WP()
	Output_Print("\tDevice Write Protection Disabled")

	numFail = 0
	numPass = 0
	numPowerCycles = 10000
	testStart = strftime("%H:%M:%S")

	#START CHARACTERIZATION
	#POWER ON 
	#PowerSupply.ON()

	iHostLockDetect = Host.Read_LockDetect()
	iDeviceLockDetect = Device.Read_LockDetect()
	fail_count=0
	for i in range(0,numPowerCycles):	
		Output_Print("Power Cycling...")
		PowerSupplyToggle()
		Output_Print("Power Cycle Complete")

		#Read Retimer Register
		Output_Print("Reading Host and Device Retimer Register...")
		#if(Host.Read_LockDetect() == HostLockDetect ):
			#if(Device.Read_LockDetect() == DeviceLockDetect ):
		if (Host.Read_LockDetect() == iHostLockDetect  and str(Host.Read_CalComplete()) == '1' and str(Host.Read_SubRate()) == '0' and str(Host.Read_FreqLock()) == '1'):
			if (Device.Read_LockDetect() == iDeviceLockDetect  and str(Device.Read_CalComplete()) == '1' and str(Device.Read_SubRate()) == '0' and str(Device.Read_FreqLock()) == '1'):
				Output_Print("\tLock Sucessful")
				numPass +=1 
			else:
				Output_Print("\tLock Unsucessful")
				numPass +=1
				Output_Print("\tPrinting Diagnostic")
				fail_count +=1
				mem += DiagnosticReport('Test_Fail', fail_count) 
				#Update OutputFile
				testEnd = strftime("%H:%M:%S") 
				target = open("Data\\%s"%filename, 'w')
				target.write("Test Start Time:%s Test End Time:%s"%(testStart,testEnd))
				target.write("\nNumber of test run:%s"%(str(numPass)))
				target.write("\nHost Initial LockDetect:%s Device Initial LockDetect:%s\n"%(iHostLockDetect,iDeviceLockDetect))
				target.write(mem)
				target.close()
				#sys.exit()
		else:
			Output_Print("\tLock Unsucessful")
			numPass +=1
			Output_Print("\tPrinting Diagnostic")
			fail_count +=1
			mem += DiagnosticReport('Test_Fail', fail_count) 
			#Update OutputFile
			testEnd = strftime("%H:%M:%S") 
			target = open("Data\\%s"%filename, 'w')
			target.write("Test Start Time:%s Test End Time:%s"%(testStart,testEnd))
			target.write("\nNumber of test run:%s"%(str(numPass+1)))
			target.write("\nHost Initial LockDetect:%s Device Initial LockDetect:%s\n"%(iHostLockDetect,iDeviceLockDetect))
			target.write(mem)
			target.close()
			#sys.exit()

		sleep(2)
		
if __name__ == '__main__':
	if (DEBUG):
		Output_Print ("Debug Routine Being Called")
		Output_Print ("DP_Automation Version %.2f"%Version)
		main()
	else:
		main()