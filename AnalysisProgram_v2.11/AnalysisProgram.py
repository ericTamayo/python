###Analaysis Program

import re
import hashlib
from Agilent import *
from OpticalBench import *
from SLTBoardRegister import *
from PowerSupply import *
from time import strftime
from TempChamber import *
from HIDController import *
from Multimeter import *
from JBert import *
from Agilent_LSSignalGen import *
from BertScope import *
from pyfiglet import Figlet
import uuid
import socket

import threading
import sys
import getopt
import os
import time

from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import numpy
from pylab import *
import matplotlib.image as mpimg
import easygui

import csv
import glob


DEBUG=False
MotorSpeed=1.0
Points=1
Version=2.1

#################################################################
##Version 0.1 --Dhileepan Thamotharam Release 05/01/2015
##				Base First Version
##Version 1.0 --Dhileepan Thamotharam
##				TimeStamp to indicate the completion Time
##				Support for Multimeter Keithley
##				Support for HIDController for EV Board
##				JBert support for Input Data control
##Version 1.1 --Dhileepan Thamotharam
##				Fixed the issue on setting Negative Temperature on TestEquity Model 205H
##Version 1.2 --Dhileepan Thamotharam
##				Enhanced support to do current measurement while running
##Version 1.3 --Dhileepan Thamotharam
##				Fixed destability issues on the CP0 Patterns
##				Added Feature to read Idle state / under MiscReadOut
##				Cleaner PrintOut
##Version 1.4 --Dhileepan Thamotharam
##				Plot the output data set option for KIC and other EM Measurements
##				Can do plot via python AnalysisProgram.py -p
##				Based on request from PDX have feature to enable the transmitter and receiver by default
##				python AnalysisProgram.py -s
##Version 1.5 --Dhileepan Thamotharam
##				Speed up the process a bit
##				StatusFile to be kept in local user directory
##Version 1.6 --Dhileepan Thamotharam
##				ON BOARD VDD AND VDDQ SUPPORT
##Version 1.7 --Dhileepan Thamotharam
##				Update the program to be able to do simultaneous scaling for Register Sweep
##Version 1.8 --Dhileepan Thamotharam
##				Support for Agilent LS Pattern Generator
##Version 1.9 --Dhileepan Thamotharam
##				Support for Agilent LS Pattern Generator
##Version 2.1 -- Eric Tamayo 
##				Support for 104B0 
##				ReTimer Suppourt PassAccu CalComplete Lock Detect 
##				python AnalysisProgram -r a
##				python AnalysisProgram -r rx
##				python AnalysisProgram -r tx
##				python AnalysisProgram -r read
##				python AnalysisProgram -a reset
#################################################################

class FuncThread(threading.Thread):
	def __init__(self, target, *args):
		self._target = target
		self._args = args
		threading.Thread.__init__(self)
 
	def run(self):
		self._target(*self._args)



def Status_Write(OutputString):
	STATUS_exists='STATUS' in locals() or 'STATUS' in globals()
	if (STATUS_exists):
		TimeStamp=strftime("%m:%d:%y::%H:%M:%S")
		STATUS.write("\n"+TimeStamp+"\t"+OutputString)
		STATUS.flush()
		os.fsync(STATUS.fileno())
			
def Output_Print(OutString):
	TimeStamp=strftime("%H:%M:%S")
	print "%s\t%s"%(TimeStamp,OutString)


def ReadInputFile(FileName):
	global RunTimeHash,TXReTimerHash,RXReTimerHash,BoardConfigHash,PreCondHash,ExecutionOrderHash,OPTBenchHash,RegisterSweepHash,PowerSupplyHash,TemperatureHash,HumidityHash,OtherValuesHash,LaneHash,TransHash,ReceiveHash,InputDataHash,InputLSDataHash,VDDHash,VDDQHash
	global RunTimeVal,BoardConfig,PreCondValues,ExecutionOrder,OPTBench,RegisterSweep,Temperature,HumidityValues,PowerSupply,OtherValues,TXReTimerVal,RXReTimerVal,TransValues,ReceiveValues,InputDataValues,InputLSDataValues,VDDValues,VDDQValues
	global OPTBenchStartPos
	global SetRegisterThread 
	OPTBenchStartPos=[None,None,None]
	global PlotDataHash
	PlotDataHash={}
	RunTimeHash={}
	BoardConfigHash={}
	ExecutionOrderHash={}
	OPTBenchHash={}
	RegisterSweepHash={}
	PowerSupplyHash={}
	TemperatureHash={}
	OtherValuesHash={}
	LaneHash={}
	TransHash={}
	TXReTimerHash={}
	RXReTimerHash={}
	ReceiveHash={}
	PreCondHash={}
	HumidityHash={}
	InputDataHash={}
	InputLSDataHash={}
	VDDHash={}
	VDDQHash={}
	RunTimeVal=[]
	BoardConfig=[]
	ExecutionOrder=[]
	OPTBench=[]
	RegisterSweep=[]
	PowerSupply=[]
	Temperature=[]
	HumidityValues=[]
	OtherValues=[]
	TransValues=[]
	TXReTimerVal=[]
	RXReTimerVal=[]
	ReceiveValues=[]
	PreCondValues=[]
	InputDataValues=[]
	InputLSDataValues=[]
	VDDValues=[]
	VDDQValues=[]
	my_file=open(FileName,"r")
	lines=my_file.read()
	my_file.close()

	if re.search('__BOARD_CONFIG_BEGIN__',lines):
		match=re.search(r'__BOARD_CONFIG_BEGIN__(.*)__BOARD_CONFIG_END__',lines,re.DOTALL)
		BoardConfig=match.group(0).split('\n')

	if re.search('__RUNTIME_BEGIN__',lines):
		match=re.search(r'__RUNTIME_BEGIN__(.*)__RUNTIME_END__',lines,re.DOTALL)
		RunTimeVal=match.group(0).split('\n')
								
	if re.search('__EXECUTION_ORDER_BEGIN__',lines):
		match=re.search(r'__EXECUTION_ORDER_BEGIN__(.*)__EXECUTION_ORDER_END__',lines,re.DOTALL)
		ExecutionOrder=match.group(0).split('\n')
		
	if re.search('__OPTICAL_BENCH_BEGIN__',lines):
		match=re.search(r'__OPTICAL_BENCH_BEGIN__(.*)__OPTICAL_BENCH_END__',lines,re.DOTALL)
		OPTBench=match.group(0).split('\n')

	if re.search('__REGISTER_SWEEP_BEGIN__',lines):
		match=re.search(r'__REGISTER_SWEEP_BEGIN__(.*)__REGISTER_SWEEP_END__',lines,re.DOTALL)
		RegisterSweep=match.group(0).split('\n')

	if re.search('__VOLTAGE_BEGIN__',lines):
		match=re.search(r'__VOLTAGE_BEGIN__(.*)__VOLTAGE_END__',lines,re.DOTALL)
		PowerSupply=match.group(0).split('\n')

	if re.search('__TEMPERATURE_BEGIN__',lines):
		match=re.search(r'__TEMPERATURE_BEGIN__(.*)__TEMPERATURE_END__',lines,re.DOTALL)
		Temperature=match.group(0).split('\n')

	if re.search('__HUMIDITY_BEGIN__',lines):
		match=re.search(r'__HUMIDITY_BEGIN__(.*)__HUMIDITY_END__',lines,re.DOTALL)
		HumidityValues=match.group(0).split('\n')

	if re.search('__OTHER_BEGIN__',lines):
		match=re.search(r'__OTHER_BEGIN__(.*)__OTHER_END__',lines,re.DOTALL)
		OtherValues=match.group(0).split('\n')

	if re.search('__SET_TRANSMITTER_BEGIN__',lines):
		match=re.search(r'__SET_TRANSMITTER_BEGIN__(.*)__SET_TRANSMITTER_END__',lines,re.DOTALL)
		TransValues=match.group(0).split('\n')

	if re.search('__SET_RECEIVER_BEGIN__',lines):	
		match=re.search(r'__SET_RECEIVER_BEGIN__(.*)__SET_RECEIVER_END__',lines,re.DOTALL)
		ReceiveValues=match.group(0).split('\n')

	if re.search('__SET_TXRETIMER_BEGIN__',lines):
		match=re.search(r'__SET_TXRETIMER_BEGIN__(.*)__SET_TXRETIMER_END__',lines,re.DOTALL)
		TXReTimerVal=match.group(0).split('\n')	

	if re.search('__SET_RXRETIMER_BEGIN__',lines):
		match=re.search(r'__SET_RXRETIMER_BEGIN__(.*)__SET_RXRETIMER_END__',lines,re.DOTALL)
		RXReTimerVal=match.group(0).split('\n')

	if re.search('__PRECONDITION_BEGIN__',lines):
		match=re.search(r'__PRECONDITION_BEGIN__(.*)__PRECONDITION_END__',lines,re.DOTALL)
		PreCondValues=match.group(0).split('\n')
	
	if re.search('__INPUT_DATA_BEGIN__',lines):
		match=re.search(r'__INPUT_DATA_BEGIN__(.*)__INPUT_DATA_END__',lines,re.DOTALL)
		InputDataValues=match.group(0).split('\n')

	if re.search('__INPUT_LS_DATA_BEGIN__',lines):
		match=re.search(r'__INPUT_LS_DATA_BEGIN__(.*)__INPUT_LS_DATA_END__',lines,re.DOTALL)
		InputLSDataValues=match.group(0).split('\n')

	if re.search('__ONBOARD_VDD_BEGIN__',lines):
		match=re.search(r'__ONBOARD_VDD_BEGIN__(.*)__ONBOARD_VDD_END__',lines,re.DOTALL)
		VDDValues=match.group(0).split('\n')

	if re.search('__ONBOARD_VDDQ_BEGIN__',lines):
		match=re.search(r'__ONBOARD_VDDQ_BEGIN__(.*)__ONBOARD_VDDQ_END__',lines,re.DOTALL)
		VDDQValues=match.group(0).split('\n')

	if re.search('__OPTICAL_BENCH_START_POSITIONS_BEGIN__',lines):
		match=re.search(r'__OPTICAL_BENCH_START_POSITIONS_BEGIN__(.*)__OPTICAL_BENCH_START_POSITIONS_END__',lines,re.DOTALL)
		OPTS=['X_START_POS','Y_START_POS','Z_START_POS']
		for i in range(3):
			for m in match.group(0).split('\n'):
				if OPTS[i] == m.split(',')[0].strip():
					OPTBenchStartPos[i]=float(m.split(',')[1])

	if re.search('__PLOT_DATA_SETTINGS_BEGIN__',lines):
		match=re.search(r'__PLOT_DATA_SETTINGS_BEGIN__(.*)__PLOT_DATA_SETTINGS_END__',lines,re.DOTALL)
		PLOTS=['JITTER_PLOT','EYEHEIGHT_PLOT','GAINSET_PLOT']
		for i in range(3):
			for m in match.group(0).split('\n'):
				if PLOTS[i] == m.split(',')[0].strip():
					if not PLOTS[i] in PlotDataHash.keys():
						PlotDataHash[PLOTS[i]]={}
						PlotDataHash[PLOTS[i]]["StartValue"]=int(m.split(',')[1])
						PlotDataHash[PLOTS[i]]["EndValue"]=int(m.split(',')[2])

#decimal to hex 
def dec2hex(n):
	return hex(n)

#hex to binary
def hex2bin(hex,Holder):
	num_of_bits=Holder.count('0')
	scale=16
	returnval=bin(int(hex,scale))[2:].zfill(num_of_bits)
	return returnval

def SetupBoardConfig():
	for Brd in BoardConfig:
		if re.match('^#',Brd) or "__BOARD_CONFIG_" in Brd or not re.search('[a-zA-Z]+',Brd):
			continue
		BrdArray=Brd.split(',')
		if not BrdArray[0] in BoardConfigHash.keys():
			BoardConfigHash[BrdArray[0]]={}
		if BrdArray[1]=="SLTBoard":
			BoardConfigHash[BrdArray[0]]["Type"]="SLTBoard"
			BoardConfigHash[BrdArray[0]]["Comport"]=BrdArray[2]
			if BrdArray[3] !="N/A":
				Port1Array=BrdArray[3].split(':')
				BoardConfigHash[BrdArray[0]]["Port_1"]=Port1Array[0]

				if not int(Port1Array[1]) in LaneHash.keys():
					LaneHash[int(Port1Array[1])]={}
				if not Port1Array[0] in LaneHash[int(Port1Array[1])].keys():
					LaneHash[int(Port1Array[1])][Port1Array[0]]={}
				LaneHash[int(Port1Array[1])][Port1Array[0]]["Comport"]=BrdArray[2]
				LaneHash[int(Port1Array[1])][Port1Array[0]]["Lane"]="L1"
				LaneHash[int(Port1Array[1])][Port1Array[0]]["Type"]="SLTBoard"
				LaneHash[int(Port1Array[1])][Port1Array[0]]["Name"]=BrdArray[0]
			
			if BrdArray[4] !="N/A":
				Port2Array=BrdArray[4].split(':')
				BoardConfigHash[BrdArray[0]]["Port_2"]=Port2Array[0]
				if not int(Port2Array[1]) in LaneHash.keys():
					LaneHash[int(Port2Array[1])]={}
				if not Port2Array[0] in LaneHash[int(Port2Array[1])].keys():
					LaneHash[int(Port2Array[1])][Port2Array[0]]={}
				LaneHash[int(Port2Array[1])][Port2Array[0]]["Comport"]=BrdArray[2]
				LaneHash[int(Port2Array[1])][Port2Array[0]]["Lane"]="L2"
				LaneHash[int(Port2Array[1])][Port2Array[0]]["Type"]="SLTBoard"
				LaneHash[int(Port2Array[1])][Port2Array[0]]["Name"]=BrdArray[0]

		elif BrdArray[1]=="HIDBoard":
			BoardConfigHash[BrdArray[0]]["Type"]="HIDBoard"
			BoardConfigHash[BrdArray[0]]["Comport"]="N/A"
			if not 1 in LaneHash.keys():
				LaneHash[1]={}
			if BrdArray[3]!="N/A":
				Port1Array=BrdArray[3].split(':')
				BoardConfigHash[BrdArray[0]]["Port_1"]=Port1Array[0]			
				if not Port1Array[0] in LaneHash[1].keys():
					LaneHash[1][Port1Array[0]]={}
				LaneHash[1][Port1Array[0]]["Type"]="HIDBoard"
				LaneHash[1][Port1Array[0]]["Lane"]="L1"
				LaneHash[1][Port1Array[0]]["Name"]=BrdArray[0]
				LaneHash[1][Port1Array[0]]["Comport"]="N/A"
			if BrdArray[4]!="N/A":					   
				Port2Array=BrdArray[4].split(':')
				BoardConfigHash[BrdArray[0]]["Port_2"]=Port2Array[0]   
				if not Port2Array[0] in LaneHash[1].keys():
					LaneHash[1][Port2Array[0]]={}
				LaneHash[1][Port2Array[0]]["Type"]="HIDBoard"
				LaneHash[1][Port2Array[0]]["Lane"]="L2"
				LaneHash[1][Port2Array[0]]["Name"]=BrdArray[0]
				LaneHash[1][Port2Array[0]]["Comport"]="N/A"
			

def SetupRunTime():
	RunTimeHash[0] = ""
	for RunVal in RunTimeVal:
		if re.match('^#',RunVal) or "__RUNTIME_" in RunVal or not re.search('[a-zA-Z0-9]+',RunVal):
			continue
		RunTimeHash[0]=RunVal

def SetupTXRX():
	TX_i=0
	for TXVal in TransValues:
		if re.match('^#', TXVal) or "__SET_TRANSMITTER_" in TXVal or not re.search('[a-zA-Z]+',TXVal):
			continue
		TXValArray=TXVal.split(',')
		if len(TXValArray)==2:
			if not TX_i in TransHash.keys():
				TransHash[TX_i]={}
				TransHash[TX_i]["Address"]=TXValArray[0].strip()
				TransHash[TX_i]["Value"]=TXValArray[1].strip()
				TX_i=TX_i+1
	RX_i=0
	for RXVal in ReceiveValues:
		if re.match('^#', RXVal) or "__SET_RECEIVER_" in RXVal or not re.search('[a-zA-Z]+',RXVal):
			continue
		RXValArray=RXVal.split(',')
		if len(RXValArray)==2:
			if not RX_i in ReceiveHash.keys():
				ReceiveHash[RX_i]={}
				ReceiveHash[RX_i]["Address"]=RXValArray[0].strip()
				ReceiveHash[RX_i]["Value"]=RXValArray[1].strip()
				RX_i=RX_i+1

def SetupReTimer():
	TX_i=0
	for TXVal in TXReTimerVal:
		if re.match('^#', TXVal) or "__SET_TXRETIMER_" in TXVal or not re.search('[a-zA-Z]+',TXVal):
			continue
		TXValArray=TXVal.split(',')
		if len(TXValArray)==2:
			if not TX_i in TXReTimerHash.keys():
				TXReTimerHash[TX_i]={}
				TXReTimerHash[TX_i]["Address"]=TXValArray[0].strip()
				TXReTimerHash[TX_i]["Value"]=TXValArray[1].strip()
				TX_i=TX_i+1
	RX_i=0
	for RXVal in RXReTimerVal:
		if re.match('^#', RXVal) or "__SET_RXRETIMER_" in RXVal or not re.search('[a-zA-Z]+',RXVal):
			continue
		RXValArray=RXVal.split(',')
		if len(RXValArray)==2:
			if not RX_i in RXReTimerHash.keys():
				RXReTimerHash[RX_i]={}
				RXReTimerHash[RX_i]["Address"]=RXValArray[0].strip()
				RXReTimerHash[RX_i]["Value"]=RXValArray[1].strip()
				RX_i=RX_i+1

def SetupPreCond():
	global Points
	for Pre in PreCondValues:
		if re.match('^#',Pre) or "__PRECONDITION_" in Pre  or not re.search('[a-zA-Z]+',Pre):
			continue
		PreCondArray=Pre.split(',')
		if not PreCondArray[0] in PreCondHash.keys():
			PreCondHash[PreCondArray[0]]={}
		LaneArray=PreCondArray[1].split(':')
		if not LaneArray[0] in PreCondHash[PreCondArray[0]].keys():
			PreCondHash[PreCondArray[0]][LaneArray[0]]={}
		if not LaneArray[1] in PreCondHash[PreCondArray[0]][LaneArray[0]].keys():
			PreCondHash[PreCondArray[0]][LaneArray[0]][LaneArray[1]]={}

		Count=len(PreCondHash[PreCondArray[0]][LaneArray[0]][LaneArray[1]].keys())
		PreCondHash[PreCondArray[0]][LaneArray[0]][LaneArray[1]][Count]={}
		PreCondHash[PreCondArray[0]][LaneArray[0]][LaneArray[1]][Count]["Address"]=PreCondArray[2]
		PreCondHash[PreCondArray[0]][LaneArray[0]][LaneArray[1]][Count]["Value"]=PreCondArray[3]

	if len(PreCondHash.keys())>0:
		HEADER_OUTPUT.write("PreCondition,")
		Points=len(PreCondHash.keys())*Points

def SetupExecutionOrder():
	global Points
	ExecOrder_i=0
	for ExecOrder in ExecutionOrder:
		if re.match('^#', ExecOrder) or "__EXECUTION_ORDER_" in ExecOrder or not re.search('[a-zA-Z]+',ExecOrder):
			continue
		if "Meas_DSA_JitterReTimerOn" in ExecOrder:
			ExecOrderArray=ExecOrder.split(',')
			if not ExecOrder_i in ExecutionOrderHash.keys():
				ExecutionOrderHash[ExecOrder_i]={}
				ExecutionOrderHash[ExecOrder_i]["Type"]=ExecOrderArray[0]
				ExecutionOrderHash[ExecOrder_i]["Test"]=ExecOrderArray[1]
			HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_TJ,"+ExecutionOrderHash[ExecOrder_i]["Test"]+"_RJ,"+ExecutionOrderHash[ExecOrder_i]["Test"]+"_DJ,"+ExecutionOrderHash[ExecOrder_i]["Test"]+"_TXPASSACCU," + ExecutionOrderHash[ExecOrder_i]["Test"]+"_RXPASSACCU,")
			if "READ_MISC_STATUS" in OtherValuesHash.keys() and OtherValuesHash["READ_MISC_STATUS"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_MiscStatus,")
			if "READ_REPLICA_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_REPLICA_OFFSET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_ReplicaOffset,")
			if "READ_EYE_HEIGHT" in OtherValuesHash.keys() and OtherValuesHash["READ_EYE_HEIGHT"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_EyeHeight,")
			if "READ_UPPER_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_UPPER_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_UpperSet,")
			if "READ_SUMM_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_SUMM_OFFSET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_SummOffset,")
			if "READ_REFERENCE_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_REFERENCE_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_RefSet,")
			if "READ_GAIN_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_GAIN_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_GainSet,")

		elif "Meas_DSA_Jitter" in ExecOrder:
			ExecOrderArray=ExecOrder.split(',')
			if not ExecOrder_i in ExecutionOrderHash.keys():
				ExecutionOrderHash[ExecOrder_i]={}
				ExecutionOrderHash[ExecOrder_i]["Type"]=ExecOrderArray[0]
				ExecutionOrderHash[ExecOrder_i]["Test"]=ExecOrderArray[1]
			HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_TJ,"+ExecutionOrderHash[ExecOrder_i]["Test"]+"_RJ,"+ExecutionOrderHash[ExecOrder_i]["Test"]+"_DJ,")
			if "READ_MISC_STATUS" in OtherValuesHash.keys() and OtherValuesHash["READ_MISC_STATUS"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_MiscStatus,")
			if "READ_REPLICA_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_REPLICA_OFFSET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_ReplicaOffset,")
			if "READ_EYE_HEIGHT" in OtherValuesHash.keys() and OtherValuesHash["READ_EYE_HEIGHT"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_EyeHeight,")
			if "READ_UPPER_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_UPPER_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_UpperSet,")
			if "READ_SUMM_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_SUMM_OFFSET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_SummOffset,")
			if "READ_REFERENCE_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_REFERENCE_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_RefSet,")
			if "READ_GAIN_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_GAIN_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_GainSet,")

		elif "Meas_DSA_Frequency" in ExecOrder:
			ExecOrderArray=ExecOrder.split(',')
			if not ExecOrder_i in ExecutionOrderHash.keys():
				ExecutionOrderHash[ExecOrder_i]={}
				ExecutionOrderHash[ExecOrder_i]["Type"]=ExecOrderArray[0]
				ExecutionOrderHash[ExecOrder_i]["Test"]=ExecOrderArray[1]
			HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_Frequency,")
			if "READ_MISC_STATUS" in OtherValuesHash.keys() and OtherValuesHash["READ_MISC_STATUS"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_MiscStatus,")
			if "READ_REPLICA_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_REPLICA_OFFSET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_ReplicaOffset,")
			if "READ_EYE_HEIGHT" in OtherValuesHash.keys() and OtherValuesHash["READ_EYE_HEIGHT"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_EyeHeight,")
			if "READ_UPPER_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_UPPER_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_UpperSet,")
			if "READ_SUMM_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_SUMM_OFFSET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_SummOffset,")
			if "READ_REFERENCE_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_REFERENCE_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_RefSet,")
			if "READ_GAIN_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_GAIN_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_GainSet,")

		elif "Meas_DSA_Amplitude" in ExecOrder:
			ExecOrderArray=ExecOrder.split(',')
			if not ExecOrder_i in ExecutionOrderHash.keys():
				ExecutionOrderHash[ExecOrder_i]={}
				ExecutionOrderHash[ExecOrder_i]["Type"]=ExecOrderArray[0]
				ExecutionOrderHash[ExecOrder_i]["Test"]=ExecOrderArray[1]
			HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_Amplitude,")
			if "READ_MISC_STATUS" in OtherValuesHash.keys() and OtherValuesHash["READ_MISC_STATUS"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_MiscStatus,")
			if "READ_REPLICA_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_REPLICA_OFFSET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_ReplicaOffset,")
			if "READ_EYE_HEIGHT" in OtherValuesHash.keys() and OtherValuesHash["READ_EYE_HEIGHT"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_EyeHeight,")
			if "READ_UPPER_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_UPPER_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_UpperSet,")
			if "READ_SUMM_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_SUMM_OFFSET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_SummOffset,")
			if "READ_REFERENCE_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_REFERENCE_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_RefSet,")
			if "READ_GAIN_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_GAIN_SET"]=="True":
				HEADER_OUTPUT.write(ExecutionOrderHash[ExecOrder_i]["Test"]+"_GainSet,")

		elif "MeasMultimeter" in ExecOrder:
			ExecOrderArray=ExecOrder.split(',')
			if not ExecOrder_i in ExecutionOrderHash.keys():
				ExecutionOrderHash[ExecOrder_i]={}
				ExecutionOrderHash[ExecOrder_i]["Type"]=ExecOrderArray[0]
				ExecutionOrderHash[ExecOrder_i]["Test"]=ExecOrderArray[1]
			if ExecOrderArray[1]=="Voltage":
				HEADER_OUTPUT.write("Voltage,")
			elif ExecOrderArray[1]=="Temperature":
				HEADER_OUTPUT.write("Temperature,")
		elif "Meas_BertScope" in ExecOrder:
 			ExecOrderArray=ExecOrder.split(',')
			if not ExecOrder_i in ExecutionOrderHash.keys():
				ExecutionOrderHash[ExecOrder_i]={}
				ExecutionOrderHash[ExecOrder_i]["Type"]=ExecOrderArray[0]
				ExecutionOrderHash[ExecOrder_i]["Test"]=ExecOrderArray[1]
			if ExecOrderArray[0]=="Meas_BertScope":
				HEADER_OUTPUT.write("BER,TotalJitter,DeterminisitcJitter,RandomJitter,")
			if "READ_MISC_STATUS" in OtherValuesHash.keys() and OtherValuesHash["READ_MISC_STATUS"]=="True":
				HEADER_OUTPUT.write("RF_MiscStatus,")
			if "READ_REPLICA_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_REPLICA_OFFSET"]=="True":
				HEADER_OUTPUT.write("RF_ReplicaOffset,")
			if "READ_EYE_HEIGHT" in OtherValuesHash.keys() and OtherValuesHash["READ_EYE_HEIGHT"]=="True":
				HEADER_OUTPUT.write("RF_EyeHeight,")
			if "READ_UPPER_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_UPPER_SET"]=="True":
				HEADER_OUTPUT.write("RF_UpperSet,")
			if "READ_SUMM_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_SUMM_OFFSET"]=="True":
				HEADER_OUTPUT.write("RF_SummOffset,")
			if "READ_REFERENCE_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_REFERENCE_SET"]=="True":
				HEADER_OUTPUT.write("RF_RefSet,")
			if "READ_GAIN_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_GAIN_SET"]=="True":
				HEADER_OUTPUT.write("RF_GainSet,")

		else:
			continue
		if OtherValuesHash["CURRENT_DRAWN"]=="True":
			HEADER_OUTPUT.write("CurrentDrawn,")
		ExecOrder_i=ExecOrder_i+1
	Points=Points*ExecOrder_i
		

def SetupInputData():
	global Points
	InputOrder_i=0
	for InputOrder in InputDataValues:
		if re.match('^#', InputOrder) or "__INPUT_DATA_" in InputOrder or not re.search('[a-zA-Z]+',InputOrder):
			continue
		if not InputOrder_i in InputDataHash.keys():
			InputDataHash[InputOrder_i]={}
			InputOrderArray=InputOrder.split(',')
			InputDataHash[InputOrder_i]["Type"]=InputOrderArray[0]
			InputDataHash[InputOrder_i]["DataType"]=InputOrderArray[1]
			InputDataHash[InputOrder_i]["DataRate"]=int(InputOrderArray[2])
			InputDataHash[InputOrder_i]["VoltageLevel"]=float(InputOrderArray[3])
		InputOrder_i=InputOrder_i+1
	if InputDataHash.has_key(0):
		Points=Points*InputOrder_i
		HEADER_OUTPUT.write("DataType,DataRate,DataLevel,")

def SetupInputLSData():
	global Points
	InputOrder_i=0
	for InputOrder in InputLSDataValues:
		if re.match('^#', InputOrder) or "__INPUT_LS_DATA_" in InputOrder or not re.search('[a-zA-Z]+',InputOrder):
			continue
		if not InputOrder_i in InputLSDataHash.keys():
			InputLSDataHash[InputOrder_i]={}
			InputOrderArray=InputOrder.split(',')
			InputLSDataHash[InputOrder_i]["Type"]=InputOrderArray[0]
			InputLSDataHash[InputOrder_i]["Frequency"]=InputOrderArray[1]
			InputLSDataHash[InputOrder_i]["VoltageLevel"]=InputOrderArray[2]
		InputOrder_i=InputOrder_i+1
	if InputLSDataHash.has_key(0):
		Points=Points*InputOrder_i
		HEADER_OUTPUT.write("DataLSType,DataLSRate,DataLSLevel,")

def SetupVDD():
	global Points
	VDD_i=0
	for VDD_Val in VDDValues:
		if re.match('#', VDD_Val) or "__ONBOARD_VDD_" in VDD_Val or not re.search('[a-zA-Z0-9]+',VDD_Val):
			continue
		VDDHash[VDD_i]=VDD_Val
		VDD_i=VDD_i+1
	HASKEY=VDDHash.has_key(0)
	if (HASKEY):
		HEADER_OUTPUT.write("ONBOARD_VDD,")
		Points=Points*VDD_i
		
def SetupVDDQ():
	global Points
	VDDQ_i=0
	for VDDQ_Val in VDDQValues:
		if re.match('#', VDDQ_Val) or "__ONBOARD_VDDQ_" in VDDQ_Val or not re.search('[a-zA-Z0-9]+',VDDQ_Val):
			continue
		VDDQHash[VDDQ_i]=VDDQ_Val
		VDDQ_i=VDDQ_i+1
	HASKEY=VDDQHash.has_key(0)
	if (HASKEY):
		HEADER_OUTPUT.write("ONBOARD_VDDQ,")		
		Points=Points*VDDQ_i	
def SetupOPTBench():
	global Points
	for OptBen in OPTBench :
		if re.match('^#', OptBen) or "__OPTICAL_BENCH" in OptBen or not re.search('[a-zA-Z]+',OptBen):
			continue
		OptBenArray=OptBen.split(',')
		if (len(OptBenArray)==5):
			OPTBenchHash[OptBenArray[0]]={}
			OPTBenchHash[OptBenArray[0]][0]=OptBenArray[1]
			OPTBenchHash[OptBenArray[0]][1]=OptBenArray[2]
			OPTBenchHash[OptBenArray[0]][2]=OptBenArray[3]
			OPTBenchHash[OptBenArray[0]][3]=OptBenArray[4]
			Points=Points*(((float(OptBenArray[3])-float(OptBenArray[2]))/float(OptBenArray[4]))+1)
	if 'XAxis' in OPTBenchHash.keys():
		HEADER_OUTPUT.write("XAxis,")   
	if 'YAxis' in OPTBenchHash.keys():
		HEADER_OUTPUT.write("YAxis,")
	if 'ZAxis' in OPTBenchHash.keys():
		HEADER_OUTPUT.write("ZAxis,")

def SetupOtherValues():

	OtherValuesHash["POWER_CYCLE_DEVICE"]="False"
	OtherValuesHash["READ_REPLICA_OFFSET"]="False"
	OtherValuesHash["READ_MISC_STATUS"]="False"
	OtherValuesHash["READ_EYE_HEIGHT"]="False"
	OtherValuesHash["READ_UPPER_SET"]="False"
	OtherValuesHash["READ_SUMM_OFFSET"]="False"
	OtherValuesHash["READ_REFERENCE_SET"]="False"
	OtherValuesHash["READ_GAIN_SET"]="False"
	OtherValuesHash["DATA_ELECIDLE"]="False"
	OtherValuesHash["DSA_RETRY"]="1"
	OtherValuesHash["CURRENT_DRAWN"]="False"
	OtherValuesHash["PLOT_DATA"]="False"

	for Other in OtherValues:
		if re.match('^#',Other) or "__OTHER_" in Other or not re.search('[a-zA-Z]+',Other):
			continue
		OtherArray=Other.split(',')
		if OtherArray[0]=="DEVICE_FAMILY":
			OtherValuesHash["DEVICE_FAMILY"]=OtherArray[1]
		elif OtherArray[0]=="POWERSUPPLY_COMPORT":
			OtherValuesHash["POWERSUPPLY_COMPORT"]=OtherArray[1]
		elif OtherArray[0]=="DSA_IPADDRESS":
			OtherValuesHash["DSA_IPADDRESS"]=OtherArray[1]
		elif OtherArray[0]=="DATA_OUTPUT_DIRECTORY":
			OtherValuesHash["DATA_OUTPUT_DIRECTORY"]=OtherArray[1]
		elif OtherArray[0]=="TEMPCHAMBER_COMPORT":
			OtherValuesHash["TEMPCHAMBER_COMPORT"]=OtherArray[1]
		elif OtherArray[0]=="TEMPCHAMBER_SOAKTIME":
			OtherValuesHash["TEMPCHAMBER_SOAKTIME"]=OtherArray[1]
		elif OtherArray[0]=="DSA_SETUP_FILE_1":
			OtherValuesHash["DSA_SETUP_FILE_1"]=OtherArray[1]
		elif OtherArray[0]=="DSA_SETUP_FILE_2":
			OtherValuesHash["DSA_SETUP_FILE_2"]=OtherArray[1]
		elif OtherArray[0]=="DSA_AVERAGE_COUNT":
			OtherValuesHash["DSA_AVERAGE_COUNT"]=OtherArray[1]	
		elif OtherArray[0]=="POWER_CYCLE_DEVICE":
			OtherValuesHash["POWER_CYCLE_DEVICE"]=OtherArray[1]
		elif OtherArray[0]=="READ_REPLICA_OFFSET":
			OtherValuesHash["READ_REPLICA_OFFSET"]=OtherArray[1]
		elif OtherArray[0]=="READ_MISC_STATUS":
			OtherValuesHash["READ_MISC_STATUS"]=OtherArray[1]
		elif OtherArray[0]=="READ_EYE_HEIGHT":
			OtherValuesHash["READ_EYE_HEIGHT"]=OtherArray[1]
		elif OtherArray[0]=="READ_UPPER_SET":
			OtherValuesHash["READ_UPPER_SET"]=OtherArray[1]
		elif OtherArray[0]=="READ_SUMM_OFFSET":
			OtherValuesHash["READ_SUMM_OFFSET"]=OtherArray[1]
		elif OtherArray[0]=="READ_REFERENCE_SET":
			OtherValuesHash["READ_REFERENCE_SET"]=OtherArray[1]
		elif OtherArray[0]=="READ_GAIN_SET":
			OtherValuesHash["READ_GAIN_SET"]=OtherArray[1]
		elif OtherArray[0]=="MULTI_ADDRESS":
			OtherValuesHash["MULTI_ADDRESS"]=OtherArray[1]
		elif OtherArray[0]=="TEMPCHAMBER_TYPE":
			OtherValuesHash["TEMPCHAMBER_TYPE"]=OtherArray[1]
		elif OtherArray[0]=="BERT_IPADDRESS":
			OtherValuesHash["BERT_IPADDRESS"]=OtherArray[1]
		elif OtherArray[0]=="DATA_ELECIDLE":
			OtherValuesHash["DATA_ELECIDLE"]=OtherArray[1]
		elif OtherArray[0]=="AGILENT_LS_ADDRESS":
			OtherValuesHash["AGILENT_LS_ADDRESS"]=OtherArray[1]
		elif OtherArray[0]=="DSA_RETRY":
			OtherValuesHash["DSA_RETRY"]=OtherArray[1]
		elif OtherArray[0]=="DSA_SETUP_FILE_DP_1":
			OtherValuesHash["DSA_SETUP_FILE_DP_1"]=OtherArray[1]
		elif OtherArray[0]=="DSA_SETUP_FILE_DP_2":
			OtherValuesHash["DSA_SETUP_FILE_DP_2"]=OtherArray[1]
		elif OtherArray[0]=="DSA_SETUP_FILE_USB_1":
			OtherValuesHash["DSA_SETUP_FILE_USB_1"]=OtherArray[1]
		elif OtherArray[0]=="DSA_SETUP_FILE_USB_2":
			OtherValuesHash["DSA_SETUP_FILE_USB_2"]=OtherArray[1]
		elif OtherArray[0]=="CURRENT_DRAWN":
			OtherValuesHash["CURRENT_DRAWN"]=OtherArray[1]
		elif OtherArray[0]=="PLOT_DATA":
			OtherValuesHash["PLOT_DATA"]=OtherArray[1]

def SetupPowerSupply():
	global Korad
	global Points
	PS_i=0
	for PS in PowerSupply:
		if re.match('^#', PS) or "__VOLTAGE" in PS or not re.search('[a-zA-Z0-9]+',PS):
			continue
		PowerSupplyHash[PS_i]=PS
		PS_i=PS_i+1
	HASKEY=PowerSupplyHash.has_key(0)
	if (HASKEY):
		HEADER_OUTPUT.write("Voltage,")
		if "POWERSUPPLY_COMPORT" in OtherValuesHash.keys():
			Korad=KA3005P(OtherValuesHash["POWERSUPPLY_COMPORT"])
		else:
			print "Power Supply Comport is Not Specified in the Input.csv File"
			exit(1) 
		Points=Points*(PS_i)

def SetupTemperature():
	global Points
	Temp_i=0
	for TempObj in Temperature:
		if re.match('^#', TempObj) or "__TEMPERATURE" in TempObj or not re.search('[a-zA-Z0-9]+',TempObj):
			continue
		TemperatureHash[Temp_i]=TempObj
		Temp_i=Temp_i+1
	HASKEY=TemperatureHash.has_key(0)
	if (HASKEY):
		HEADER_OUTPUT.write("Temperature,")
		if "TEMPCHAMBER_COMPORT" in OtherValuesHash.keys():
			Chamber_exists='TemperatureChamber' in locals() or 'TemperatureChamber' in globals()
			if not Chamber_exists:
				global TemperatureChamber
				if OtherValuesHash["TEMPCHAMBER_TYPE"]=="107":
					TemperatureChamber=TestEquity_107(OtherValuesHash["TEMPCHAMBER_COMPORT"])
				elif OtherValuesHash["TEMPCHAMBER_TYPE"]=="205H":
					TemperatureChamber=TestEquity_205H(OtherValuesHash["TEMPCHAMBER_COMPORT"])  
		else:
			print "Chamber Comport is Not Specified in the Input.csv File"
			exit(1)
		Points=Points*(Temp_i)

def SetupHumidity():
	global Points
	Hum_i=0
	for HumObj in HumidityValues:
		if re.match('^#', HumObj) or "__HUMIDITY" in HumObj or not re.search('[a-zA-Z0-9]+',HumObj):
			continue
		HumidityHash[Hum_i]=HumObj
		Hum_i=Hum_i+1
	HASKEY=HumidityHash.has_key(0)
	if (HASKEY):
		HEADER_OUTPUT.write("Humidity,")
		if "TEMPCHAMBER_COMPORT" in OtherValuesHash.keys():
			Chamber_exists='TemperatureChamber' in locals() or 'TemperatureChamber' in globals()
			if not Chamber_exists:
				global TemperatureChamber
				if OtherValuesHash["TEMPCHAMBER_TYPE"]=="205H":
					TemperatureChamber=TestEquity_205H(OtherValuesHash["TEMPCHAMBER_COMPORT"])
				else:
					print "Incorrect Chamber chosen for Humidity only supported on 205H Model"
					exit(1)
		else:
			print "Chamber Comport is Not Specified in the Input.csv File"
			exit(1)
		Points=Points*(Hum_i)

def SetupRegisterSweep():
	global Points
	for RegSweep in RegisterSweep:
		if re.match('^#', RegSweep) or "_REGISTER_SWEEP" in RegSweep or not re.search('[a-zA-Z]+',RegSweep):
			continue
		RegSweepArray=RegSweep.split(',')
		if (len(RegSweepArray)==7):
			RegisterSweepHash[int(RegSweepArray[0])]={}
			RegisterSweepHash[int(RegSweepArray[0])][0]=RegSweepArray[1]
			RegisterSweepHash[int(RegSweepArray[0])][1]=RegSweepArray[2]
			RegisterSweepHash[int(RegSweepArray[0])][2]=RegSweepArray[3]
			RegisterSweepHash[int(RegSweepArray[0])][3]=RegSweepArray[4]
			StartString=RegSweepArray[4]
			EndString=RegSweepArray[5]
			RegisterSweepHash[int(RegSweepArray[0])][4]=int((StartString.replace("X","")),2)
			RegisterSweepHash[int(RegSweepArray[0])][5]=RegSweepArray[5]
			RegisterSweepHash[int(RegSweepArray[0])][6]=int((EndString.replace("X","")),2)
			RegisterSweepHash[int(RegSweepArray[0])][7]=EndString.replace("1","0")
			RegisterSweepHash[int(RegSweepArray[0])][8]=int(RegSweepArray[6])
			HEADER_OUTPUT.write(RegisterSweepHash[int(RegSweepArray[0])][0]+"_"+RegisterSweepHash[int(RegSweepArray[0])][1]+",")
			Val=(((RegisterSweepHash[int(RegSweepArray[0])][6])-(RegisterSweepHash[int(RegSweepArray[0])][4]))/RegisterSweepHash[int(RegSweepArray[0])][8])+1
			Points=Points*Val

def DebugReadLog():
	for DataKey in sorted(InputDataHash.keys()):
		sys.stdout.write("Type "+InputDataHash[DataKey]["Type"]+"\t")
		sys.stdout.write("SubType "+InputDataHash[DataKey]["DataType"]+"\t")
		sys.stdout.write("DataRate "+str(InputDataHash[DataKey]["DataRate"])+"\t")
		sys.stdout.write("\n")
	for DataKey in sorted(InputLSDataHash.keys()):
		sys.stdout.write("Type "+InputLSDataHash[DataKey]["Type"]+"\t")
		sys.stdout.write("SubType "+InputLSDataHash[DataKey]["Frequency"]+"\t")
		sys.stdout.write("DataRate "+InputLSDataHash[DataKey]["VoltageLevel"]+"\t")
		sys.stdout.write("\n")
	for TXKey in sorted(TransHash.keys()):
		sys.stdout.write("Setting Transmitter\t")
		sys.stdout.write("Address "+ReceiveHash[TXKey]["Address"]+"\t")
		sys.stdout.write("Value "+ReceiveHash[TXKey]["Value"]+"\t")
		sys.stdout.write("\n")
	for TXKey in sorted(TXReTimerHash.keys()):
		sys.stdout.write("Setting Transmitter ReTimer\t")
		sys.stdout.write("Address "+ReceiveHash[TXKey]["Address"]+"\t")
		sys.stdout.write("Value "+ReceiveHash[TXKey]["Value"]+"\t")
		sys.stdout.write("\n")
	for RXKey in sorted(ReceiveHash.keys()):
		sys.stdout.write("Setting Receiver\t")
		sys.stdout.write("Address "+ReceiveHash[RXKey]["Address"]+"\t")
		sys.stdout.write("Value "+ReceiveHash[RXKey]["Value"]+"\t")
		sys.stdout.write("\n")
	for RXKey in sorted(RXReTimerHash.keys()):
		sys.stdout.write("Setting Receiver ReTimer\t")
		sys.stdout.write("Address "+ReceiveHash[RXKey]["Address"]+"\t")
		sys.stdout.write("Value "+ReceiveHash[RXKey]["Value"]+"\t")
		sys.stdout.write("\n")
	for PowerSupplyKey in PowerSupplyHash.iterkeys():
		sys.stdout.write("Setting PowerSupply: "+PowerSupplyHash[PowerSupplyKey])
		sys.stdout.write("\n")
	for TempChamberKey in TemperatureHash.iterkeys():
		sys.stdout.write("Setting Temperature: "+TemperatureHash[TempChamberKey])
		sys.stdout.write("\n")
	for HumidChamberKey in HumidityHash.iterkeys():
		sys.stdout.write("Setting Humidity: "+HumidityHash[HumidChamberKey])
		sys.stdout.write("\n")
	for OtherKey in OtherValuesHash.iterkeys():
		sys.stdout.write("Setting :"+OtherKey+"="+OtherValuesHash[OtherKey])
		sys.stdout.write("\n")
	for BrdKey in sorted(BoardConfigHash.keys()):
		sys.stdout.write("\nSetting :"+BrdKey+"\n")
		sys.stdout.write("\tType:"+BoardConfigHash[BrdKey]["Type"]+"\n")
		if "Comport" in BoardConfigHash[BrdKey].keys():
			sys.stdout.write("\tComport:"+BoardConfigHash[BrdKey]["Comport"]+"\n")
		if "Port_1" in BoardConfigHash[BrdKey].keys():
			sys.stdout.write("\tPort_1:"+BoardConfigHash[BrdKey]["Port_1"]+"\n")
		if "Port_2" in BoardConfigHash[BrdKey].keys():
			sys.stdout.write("\tPort_2:"+BoardConfigHash[BrdKey]["Port_2"]+"\n")
		sys.stdout.write("\n")
	for Lane in sorted(LaneHash.keys()):
		sys.stdout.write("\nSetting Lane:"+str(Lane)+"\n")
		if "TX" in LaneHash[Lane].keys():
			sys.stdout.write("\n\tTXRX:"+"TX"+"\n")
			if "Comport" in LaneHash[Lane]["TX"].keys():
				sys.stdout.write("\tCOMPORT:"+LaneHash[Lane]["TX"]["Comport"]+"\n")
			if "Lane" in LaneHash[Lane]["TX"].keys():
				sys.stdout.write("\tLane:"+str(LaneHash[Lane]["TX"]["Lane"])+"\n")
			if "Type" in LaneHash[Lane]["TX"].keys():
				sys.stdout.write("\tType:"+str(LaneHash[Lane]["TX"]["Type"])+"\n")
			if "Name" in LaneHash[Lane]["TX"].keys():
				sys.stdout.write("\tName:"+str(LaneHash[Lane]["TX"]["Name"])+"\n")
		if "RX" in LaneHash[Lane].keys():
			sys.stdout.write("\tTXRX:"+"RX"+"\n")
			if "COMPORT" in LaneHash[Lane]["RX"].keys():
				sys.stdout.write("\tCOMPORT:"+LaneHash[Lane]["RX"]["COMPORT"]+"\n")
			if "Lane" in LaneHash[Lane]["TX"].keys():
				sys.stdout.write("\tPort:"+str(LaneHash[Lane]["RX"]["Lane"])+"\n")
			if "Type" in LaneHash[Lane]["RX"].keys():
				sys.stdout.write("\tType:"+str(LaneHash[Lane]["RX"]["Type"])+"\n")
			if "Name" in LaneHash[Lane]["RX"].keys():
				sys.stdout.write("\tName:"+str(LaneHash[Lane]["RX"]["Name"])+"\n")
		sys.stdout.write("\n")
	for OptKey in OPTBenchHash.iterkeys():
		sys.stdout.write("Setting Axis: "+OptKey+"\t")
		sys.stdout.write("SerialNum: "+OPTBenchHash[OptKey][0]+"\t")
		sys.stdout.write("Start: "+OPTBenchHash[OptKey][1]+"\t")
		sys.stdout.write("End: "+OPTBenchHash[OptKey][2]+"\t")
		sys.stdout.write("Resolution: "+OPTBenchHash[OptKey][3])
		sys.stdout.write("\n")
	for ExecOrderKey in ExecutionOrderHash.iterkeys():
		sys.stdout.write("Execute: "+ExecutionOrderHash[ExecOrderKey]["Type"]+"_OF_"+ExecutionOrderHash[ExecOrderKey]["Test"])
		sys.stdout.write("\n")

	for VDDKey in VDDHash.iterkeys():
		sys.stdout.write("VDD: "+VDDHash[VDDKey])
		sys.stdout.write("\n")

	for VDDQKey in VDDQHash.iterkeys():
		sys.stdout.write("VDDQ: "+VDDQHash[VDDQKey])
		sys.stdout.write("\n")

	for RegSweepKey in sorted(RegisterSweepHash.keys()):
		sys.stdout.write("Key: "+str(RegSweepKey)+"\t")
		sys.stdout.write("Reg: "+RegisterSweepHash[RegSweepKey][0]+"\t")
		sys.stdout.write("CH: "+RegisterSweepHash[RegSweepKey][1]+"\t")
		sys.stdout.write("Add: "+RegisterSweepHash[RegSweepKey][2]+"\t")
		sys.stdout.write("Start: "+RegisterSweepHash[RegSweepKey][3]+"\t")
		sys.stdout.write("StartDec: "+str(RegisterSweepHash[RegSweepKey][4])+"\t")
		sys.stdout.write("End: "+RegisterSweepHash[RegSweepKey][5]+"\t")
		sys.stdout.write("EndDec: "+str(RegisterSweepHash[RegSweepKey][6])+"\t")
		sys.stdout.write("ModReg: "+RegisterSweepHash[RegSweepKey][7]+"\t")
		sys.stdout.write("StepSize: "+str(RegisterSweepHash[RegSweepKey][8])+"\t")
		sys.stdout.write("\n")
	
def SetDefaultRegister():
	Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
	Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
	Board_exists='Board' in locals() or 'Board' in globals()	
	
	for TEST_BOARD in BoardConfigHash.keys():
		if BoardConfigHash[TEST_BOARD]["Type"]=="SLTBoard":
			if "Port_1" in BoardConfigHash[TEST_BOARD] and BoardConfigHash[TEST_BOARD]["Port_1"]=="TX":
				if Board_X_exists and TEST_BOARD==Board_X.ID:
					for Trans in sorted(TransHash.keys()):
						#print (TransHash[Trans]["Address"]+ ":" + TransHash[Trans]["Value"])
						Board_X.Write("L1",TransHash[Trans]["Address"],TransHash[Trans]["Value"])
				if Board_Y_exists and TEST_BOARD==Board_Y.ID:
					for Trans in sorted(TransHash.keys()):
						#print (TransHash[Trans]["Address"]+ ":" + TransHash[Trans]["Value"])
						Board_Y.Write("L1",TransHash[Trans]["Address"],TransHash[Trans]["Value"])
			if "Port_2" in BoardConfigHash[TEST_BOARD] and BoardConfigHash[TEST_BOARD]["Port_2"]=="TX":
				if Board_X_exists and TEST_BOARD==Board_X.ID:
					for Trans in sorted(TransHash.keys()):
						Board_X.Write("L2",TransHash[Trans]["Address"],TransHash[Trans]["Value"])
				if Board_Y_exists and TEST_BOARD==Board_Y.ID:
					for Trans in sorted(TransHash.keys()):
						Board_Y.Write("L2",TransHash[Trans]["Address"],TransHash[Trans]["Value"])						
		if BoardConfigHash[TEST_BOARD]["Type"]=="HIDBoard":
			if "Port_1" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_1"]=="TX":
				if Board_exists and TEST_BOARD==Board.ID:
					for Trans in sorted(TransHash.keys()):
						Board.selectChip("L1")
						Board.Write(TransHash[Trans]["Address"],TransHash[Trans]["Value"])
			if "Port_2" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_2"]=="TX":
				if Board_exists and TEST_BOARD==Board.ID:
					for Trans in sorted(TransHash.keys()):
						Board.selectChip("L2")
						Board.Write(TransHash[Trans]["Address"],TransHash[Trans]["Value"])
	
	sleep(5)
	
	for TEST_BOARD in BoardConfigHash.keys():
		if BoardConfigHash[TEST_BOARD]["Type"]=="SLTBoard":
			if "Port_1" in BoardConfigHash[TEST_BOARD] and BoardConfigHash[TEST_BOARD]["Port_1"]=="RX":
				if Board_X_exists and TEST_BOARD==Board_X.ID:
					for Receive in sorted(ReceiveHash.keys()):
						print ("L1" + ReceiveHash[Receive]["Address"]+ ":" + ReceiveHash[Receive]["Value"])
						Board_X.Write("L1",ReceiveHash[Receive]["Address"],ReceiveHash[Receive]["Value"])
						
				if Board_Y_exists and TEST_BOARD==Board_Y.ID:
					for Receive in sorted(ReceiveHash.keys()):
						Board_Y.Write("L1",ReceiveHash[Receive]["Address"],ReceiveHash[Receive]["Value"])
			if "Port_2" in BoardConfigHash[TEST_BOARD] and BoardConfigHash[TEST_BOARD]["Port_2"]=="RX":
				if Board_X_exists and TEST_BOARD==Board_X.ID:
					for Receive in sorted(ReceiveHash.keys()):
						Board_X.Write("L2",ReceiveHash[Receive]["Address"],ReceiveHash[Receive]["Value"])
				if Board_Y_exists and TEST_BOARD==Board_Y.ID:
					for Receive in sorted(ReceiveHash.keys()):
						Board_Y.Write("L2",ReceiveHash[Receive]["Address"],ReceiveHash[Receive]["Value"])					
		if BoardConfigHash[TEST_BOARD]["Type"]=="HIDBoard":
			if "Port_1" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_1"]=="RX":
				if Board_exists and TEST_BOARD==Board.ID:
					for Receive in sorted(ReceiveHash.keys()):
						Board.selectChip("L1")
						Board.Write(ReceiveHash[Receive]["Address"],ReceiveHash[Receive]["Value"])
			if "Port_2" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_2"]=="RX":
				if Board_exists and TEST_BOARD==Board.ID:
					for Receive in sorted(ReceiveHash.keys()):
						Board.selectChip("L2")
						Board.Write(ReceiveHash[Receive]["Address"],ReceiveHash[Receive]["Value"])
	
	Output_Print("Set Default Registers Successful")
	Status_Write("Set Default Registers Successful")

def SoftReset():
	Board_X.softReset("L1")
	sleep(2)
	Board_X.softReset("L2")
	sleep(2)
	Board_Y.softReset("L1")
	sleep(2)
	Board_Y.softReset("L2")
	sleep(2)

def SetTXReTimer():
	Output_Print("Loading TX ReTimer...")
	Status_Write("Loading TX ReTimer...")
	Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
	Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
	Board_exists='Board' in locals() or 'Board' in globals()	
	
	for TEST_BOARD in BoardConfigHash.keys():
		if BoardConfigHash[TEST_BOARD]["Type"]=="SLTBoard":
			if "Port_1" in BoardConfigHash[TEST_BOARD] and BoardConfigHash[TEST_BOARD]["Port_1"]=="TX":
				if Board_X_exists and TEST_BOARD==Board_X.ID:
					for Trans in sorted(TXReTimerHash.keys()):
						Board_X.Write("L1",TXReTimerHash[Trans]["Address"],TXReTimerHash[Trans]["Value"])
				if Board_Y_exists and TEST_BOARD==Board_Y.ID:
					for Trans in sorted(TXReTimerHash.keys()):
						Board_Y.Write("L1",TXReTimerHash[Trans]["Address"],TXReTimerHash[Trans]["Value"])
			if "Port_2" in BoardConfigHash[TEST_BOARD] and BoardConfigHash[TEST_BOARD]["Port_2"]=="TX":
				if Board_X_exists and TEST_BOARD==Board_X.ID:
					for Trans in sorted(TXReTimerHash.keys()):
						Board_X.Write("L2",TXReTimerHash[Trans]["Address"],TXReTimerHash[Trans]["Value"])
				if Board_Y_exists and TEST_BOARD==Board_Y.ID:
					for Trans in sorted(TXReTimerHash.keys()):
						Board_Y.Write("L2",TXReTimerHash[Trans]["Address"],TXReTimerHash[Trans]["Value"])						
		if BoardConfigHash[TEST_BOARD]["Type"]=="HIDBoard":
			if "Port_1" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_1"]=="TX":
				if Board_exists and TEST_BOARD==Board.ID:
					for Trans in sorted(TXReTimerHash.keys()):
						Board.selectChip("L1")
						Board.Write(TXReTimerHash[Trans]["Address"],TXReTimerHash[Trans]["Value"])
			if "Port_2" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_2"]=="TX":
				if Board_exists and TEST_BOARD==Board.ID:
					for Trans in sorted(TXReTimerHash.keys()):
						Board.selectChip("L2")
						Board.Write(TXReTimerHash[Trans]["Address"],TXReTimerHash[Trans]["Value"])
	sleep(5)
	
	Output_Print("Set ReTimer Successful")
	Status_Write("Set ReTimer Successful")

def SetRXReTimerSingle(lane):
	if lane == '1':
		Output_Print('Loading ReTimer for RX1...')
		for Receive in sorted(RXReTimerHash.keys()):
			Board_X.Write("L1",RXReTimerHash[Receive]["Address"],RXReTimerHash[Receive]["Value"])
		Output_Print('RX1 ReTimer Loaded')
	if lane == '2':
		Output_Print('Loading ReTimer for RX2...')
		for Receive in sorted(RXReTimerHash.keys()):
			Board_Y.Write("L1",RXReTimerHash[Receive]["Address"],RXReTimerHash[Receive]["Value"])
		Output_Print('RX2 ReTimer Loaded')

def SetRXReTimer():
	Output_Print("Loading RX ReTimer...")
	Status_Write("Loading RX ReTimer...")
	Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
	Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
	Board_exists='Board' in locals() or 'Board' in globals()	
		
	for TEST_BOARD in BoardConfigHash.keys():
		if BoardConfigHash[TEST_BOARD]["Type"]=="SLTBoard":
			if "Port_1" in BoardConfigHash[TEST_BOARD] and BoardConfigHash[TEST_BOARD]["Port_1"]=="RX":
				if Board_X_exists and TEST_BOARD==Board_X.ID:
					for Receive in sorted(RXReTimerHash.keys()):
						Board_X.Write("L1",RXReTimerHash[Receive]["Address"],RXReTimerHash[Receive]["Value"])
				if Board_Y_exists and TEST_BOARD==Board_Y.ID:
					for Receive in sorted(RXReTimerHash.keys()):
						Board_Y.Write("L1",RXReTimerHash[Receive]["Address"],RXReTimerHash[Receive]["Value"])
			if "Port_2" in BoardConfigHash[TEST_BOARD] and BoardConfigHash[TEST_BOARD]["Port_2"]=="RX":
				if Board_X_exists and TEST_BOARD==Board_X.ID:
					for Receive in sorted(RXReTimerHash.keys()):
						Board_X.Write("L2",RXReTimerHash[Receive]["Address"],RXReTimerHash[Receive]["Value"])
				if Board_Y_exists and TEST_BOARD==Board_Y.ID:
					for Receive in sorted(RXReTimerHash.keys()):
						Board_Y.Write("L2",RXReTimerHash[Receive]["Address"],RXReTimerHash[Receive]["Value"])					
		if BoardConfigHash[TEST_BOARD]["Type"]=="HIDBoard":
			if "Port_1" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_1"]=="RX":
				if Board_exists and TEST_BOARD==Board.ID:
					for Receive in sorted(RXReTimerHash.keys()):
						Board.selectChip("L1")
						Board.Write(RXReTimerHash[Receive]["Address"],RXReTimerHash[Receive]["Value"])
			if "Port_2" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_2"]=="RX":
				if Board_exists and TEST_BOARD==Board.ID:
					for Receive in sorted(RXReTimerHash.keys()):
						Board.selectChip("L2")
						Board.Write(RXReTimerHash[Receive]["Address"],RXReTimerHash[Receive]["Value"])
	
	Output_Print("ReTimer Loaded")
	Status_Write("ReTimer Loaded")
	sleep(5)

def DisableLane(Lane):
	Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
	Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
	Board_exists='Board' in locals() or 'Board' in globals()	
	if Lane in LaneHash.keys() and "TX" in LaneHash[Lane].keys() and LaneHash[Lane]["TX"]["Type"]=="SLTBoard":
		BoardID=LaneHash[Lane]["TX"]["Name"]
		LaneVal=LaneHash[Lane]["TX"]["Lane"]
		if(LaneVal=="L1"):
			LaneVal="0"
		elif(LaneVal=="L2"):
			LaneVal="1"
		if Board_X_exists and BoardID==Board_X.ID:
			if OtherValuesHash["DEVICE_FAMILY"] == "KSS104":
				Board_X.PDN_OFF(LaneVal)
			else:
				Board_X.Disable_Lane(LaneVal)
		elif Board_Y_exists and BoardID==Board_Y.ID:
			if OtherValuesHash["DEVICE_FAMILY"] == "KSS104":
				Board_Y.PDN_OFF(LaneVal)
			else:
				Board_Y.Disable_Lane(LaneVal)
			
		
	if Lane in LaneHash.keys() and "RX" in LaneHash[Lane].keys() and LaneHash[Lane]["RX"]["Type"]=="SLTBoard":
		BoardID=LaneHash[Lane]["RX"]["Name"]
		LaneVal=LaneHash[Lane]["RX"]["Lane"]
		if(LaneVal=="L1"):
			LaneVal="0"
		elif(LaneVal=="L2"):
			LaneVal="1"
		if Board_X_exists and BoardID==Board_X.ID:
			if OtherValuesHash["DEVICE_FAMILY"] == "KSS104":
				Board_X.PDN_OFF(LaneVal)
			else:
				Board_X.Disable_Lane(LaneVal)
		elif Board_Y_exists and BoardID==Board_Y.ID:
			if OtherValuesHash["DEVICE_FAMILY"] == "KSS104":
				Board_Y.PDN_OFF(LaneVal)
			else:
				Board_Y.Disable_Lane(LaneVal)
	Output_Print("Disable Lane: %d Successful"%Lane)
	Status_Write("Disable Lane: %d Successful"%Lane)

def EnableLane(Lane):
	Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
	Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
	Board_exists='Board' in locals() or 'Board' in globals()	
	if OtherValuesHash["DEVICE_FAMILY"] == "KSS103":
		if Lane in LaneHash.keys() and "RX" in LaneHash[Lane].keys() and LaneHash[Lane]["RX"]["Type"]=="SLTBoard":
			BoardID=LaneHash[Lane]["RX"]["Name"]
			LaneVal=LaneHash[Lane]["RX"]["Lane"]
			if(LaneVal=="L1"):
				LaneVal="0"
			elif(LaneVal=="L2"):
				LaneVal="1"
			if Board_X_exists and BoardID==Board_X.ID:
				for Receive in sorted(ReceiveHash.keys()):
					Board_X.Write(LaneVal,ReceiveHash[Receive]["Address"],ReceiveHash[Receive]["Value"])
			elif Board_Y_exists and BoardID==Board_Y.ID:
				for Receive in sorted(ReceiveHash.keys()):
					Board_Y.Write(LaneVal,ReceiveHash[Receive]["Address"],ReceiveHash[Receive]["Value"])
		if Lane in LaneHash.keys() and "TX" in LaneHash[Lane].keys() and LaneHash[Lane]["TX"]["Type"]=="SLTBoard":
			BoardID=LaneHash[Lane]["TX"]["Name"]
			LaneVal=LaneHash[Lane]["TX"]["Lane"]
			if(LaneVal=="L1"):
				LaneVal="0"
			elif(LaneVal=="L2"):
				LaneVal="1"
			if Board_X_exists and BoardID==Board_X.ID:
				for Trans in sorted(TransHash.keys()):
					Board_X.PDN_ON()
					Board_X.Write(LaneVal,TransHash[Trans]["Address"],TransHash[Trans]["Value"])
			elif Board_Y_exists and BoardID==Board_Y.ID:
				for Trans in sorted(TransHash.keys()):
					Board_Y.PDN_ON()
					Board_Y.Write(LaneVal,TransHash[Trans]["Address"],TransHash[Trans]["Value"])
	if OtherValuesHash["DEVICE_FAMILY"] == "KSS103":
		Board_X.PDN_ON()
		Board_Y.PDN_ON()
	Output_Print("Enable Lane: %d Successful"%Lane)
	Status_Write("Enable Lane: %d Successful"%Lane)
				 
def ReadRXStatus(Option,Lane):
	if not Lane in LaneHash.keys() or not "RX" in LaneHash[Lane].keys():
		RtnVal="N/A"
	else:
		Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
		Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
		Board_exists='Board' in locals() or 'Board' in globals()   
		
		ID=LaneHash[Lane]["RX"]["Name"]
		Type=LaneHash[Lane]["RX"]["Type"]
		if Type=="SLTBoard":
			LaneVal=LaneHash[Lane]["RX"]["Lane"]
			if Board_X_exists and ID==Board_X.ID:
				if Option=="MiscStatus":
					RtnVal=Board_X.Read_MiscStatus(LaneVal)
				elif Option=="ReplicaOffset":
					RtnVal=Board_X.Read_ReplicaOffset(LaneVal)		  
				elif Option=="EyeHeight":
					RtnVal=Board_X.Read_EyeHeight(LaneVal)
				elif Option=="UpperSet":
					RtnVal=Board_X.Read_UpperSet(LaneVal)
				elif Option=="SummOff":
					RtnVal=Board_X.Read_SummOff(LaneVal)
				elif Option=="RefSet":
					RtnVal=Board_X.Read_RefSet(LaneVal)
				elif Option=="GainSet":
					RtnVal=Board_X.Read_GainSet(LaneVal)
			elif Board_Y_exists and ID==Board_Y.ID:
				if Option=="MiscStatus":
					RtnVal=Board_Y.Read_MiscStatus(LaneVal)
				elif Option=="ReplicaOffset":
					RtnVal=Board_Y.Read_ReplicaOffset(LaneVal)		  
				elif Option=="EyeHeight":
					RtnVal=Board_Y.Read_EyeHeight(LaneVal)
				elif Option=="UpperSet":
					RtnVal=Board_Y.Read_UpperSet(LaneVal)
				elif Option=="SummOff":
					RtnVal=Board_Y.Read_SummOff(LaneVal)
				elif Option=="RefSet":
					RtnVal=Board_Y.Read_RefSet(LaneVal)
				elif Option=="GainSet":
					RtnVal=Board_Y.Read_GainSet(LaneVal)
			else:
				RtnVal="N/A"
		elif Type=="HIDBoard":
			if Board_exists and ID==Board.ID:
				Lane=LaneHash[Lane]["RX"]["Lane"]
				Board.selectChip(Lane)
				if Option=="MiscStatus":
					RtnVal=Board.Read_MiscStatus()
				elif Option=="ReplicaOffset":
					RtnVal=Board.Read_ReplicaOffset()   
				elif Option=="EyeHeight":
					RtnVal=Board.Read_EyeHeight()
				elif Option=="UpperSet":
					RtnVal=Board.Read_UpperSet()
				elif Option=="SummOff":
					RtnVal=Board.Read_SummOff()
				elif Option=="RefSet":
					RtnVal=Board.Read_RefSet()
				elif Option=="GainSet":
					RtnVal=Board.Read_GainSet()
			else:
				RtnVal="N/A"
	OUTPUT_DATA_HASH[Option]=RtnVal
	return RtnVal

def ReadLDOStatus(Option,Lane):
	if not Lane in LaneHash.keys():
		return
	else:
		Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
		Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
		Board_exists='Board' in locals() or 'Board' in globals()   
		
		ID=LaneHash[Lane]["TX"]["Name"]
		Type=LaneHash[Lane]["TX"]["Type"]
		if Type=="SLTBoard":
			LaneVal=LaneHash[Lane]["TX"]["Lane"]
			if Board_X_exists and ID==Board_X.ID:
				if Option=="RF_LDO":
					Board_X.LDO_RF(LaneVal)
				elif Option=="BB_LDO":
					Board_X.LDO_BB(LaneVal)
				elif Option=="OD_LDO":
					Board_X.LDO_OD(LaneVal)				
			if Board_Y_exists and ID==Board_Y.ID:
				if Option=="RF_LDO":
					Board_Y.LDO_RF(LaneVal)
				elif Option=="BB_LDO":
					Board_Y.LDO_BB(LaneVal)
				elif Option=="OD_LDO":
					Board_Y.LDO_OD(LaneVal)	

		ID=LaneHash[Lane]["RX"]["Name"]
		Type=LaneHash[Lane]["RX"]["Type"]
		if Type=="SLTBoard":
			LaneVal=LaneHash[Lane]["RX"]["Lane"]
			if Board_X_exists and ID==Board_X.ID:
				if Option=="RF_LDO":
					Board_X.LDO_RF(LaneVal)
				elif Option=="BB_LDO":
					Board_X.LDO_BB(LaneVal)
				elif Option=="OD_LDO":
					Board_X.LDO_OD(LaneVal)				
			if Board_Y_exists and ID==Board_Y.ID:
				if Option=="RF_LDO":
					Board_Y.LDO_RF(LaneVal)
				elif Option=="BB_LDO":
					Board_Y.LDO_BB(LaneVal)
				elif Option=="OD_LDO":
					Board_Y.LDO_OD(LaneVal)			

def ReadRXRegisterStatus(Lane):
	if "READ_MISC_STATUS" in OtherValuesHash.keys() and OtherValuesHash["READ_MISC_STATUS"]=="True":
		ReadRXStatus("MiscStatus",Lane)	
	if "READ_REPLICA_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_REPLICA_OFFSET"]=="True":
		ReadRXStatus("ReplicaOffset",Lane)	
	if "READ_EYE_HEIGHT" in OtherValuesHash.keys() and OtherValuesHash["READ_EYE_HEIGHT"]=="True":
		ReadRXStatus("EyeHeight",Lane)
	if "READ_UPPER_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_UPPER_SET"]=="True":
		ReadRXStatus("UpperSet",Lane)
	if "READ_SUMM_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_SUMM_OFFSET"]=="True":
		ReadRXStatus("SummOff",Lane)
	if "READ_REFERENCE_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_REFERENCE_SET"]=="True":
		ReadRXStatus("RefSet",Lane)
	if "READ_GAIN_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_GAIN_SET"]=="True":
		ReadRXStatus("GainSet",Lane)
	Output_Print("Complete Collecting Jitter / Status Reads for Given Point")
	Status_Write("Complete Collecting Jitter / Status Reads for Given Point")			

def BinaryCalculation(Holder,DefaultValueBinary,ValueBinary):
	ReturnString=""
	i=0
	k=0
	while i<len(Holder):
		if Holder[i]=="X":
			ReturnString=ReturnString+DefaultValueBinary[i]
		else:
			ReturnString=ReturnString+ValueBinary[k]
			k=k+1
		i=i+1
	return ReturnString
	

def ModifyRegister(Channel,Address,Holder,Value):
	ChannelArray=Channel.split(":")
	if len(ChannelArray)==2:
		if ChannelArray[1]=="*":
			for LaneKeys in LaneHash.keys():
				for TXRXKey in LaneHash[LaneKeys].keys():
					if TXRXKey==ChannelArray[0]:
						LaneVal=LaneHash[LaneKeys][TXRXKey]["Lane"]
						ID=LaneHash[LaneKeys][TXRXKey]["Name"]
						Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
						Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
						Board_exists = 'Board' in locals() or 'Board' in globals() 				
						if Board_X.ID==ID:
							DefaultValue=Board_X.Read(LaneVal,Address)
							DefaultValueBinary=hex2bin(DefaultValue,"00000000")
							valHex=hex2bin(dec2hex(Value),Holder)
							ValueString=BinaryCalculation(Holder,DefaultValueBinary,valHex)
							UpdateValue='{:0{}X}'.format(int(ValueString,2),len(ValueString)//4)
							UpdateValue="0x"+str(UpdateValue)
							Board_X.Write(LaneVal,Address,UpdateValue)
							Output_Print("Modifying Register Complete for Board:%s"%Board_X.ID)
							Status_Write("Modifying Register Complete for Board:%s"%Board_X.ID)	
						elif Board_Y.ID==ID:
							DefaultValue=Board_Y.Read(LaneVal,Address)
							DefaultValueBinary=hex2bin(DefaultValue,"00000000")
							valHex=hex2bin(dec2hex(Value),Holder)
							ValueString=BinaryCalculation(Holder,DefaultValueBinary,valHex)
							UpdateValue='{:0{}X}'.format(int(ValueString,2),len(ValueString)//4)
							UpdateValue="0x"+str(UpdateValue)
							Board_Y.Write(LaneVal,Address,UpdateValue)
							Output_Print("Modifying Register Complete for Board:%s"%Board_Y.ID)
							Status_Write("Modifying Register Complete for Board:%s"%Board_Y.ID)		
						elif Board.ID==ID:
							Board.selectChip(LaneVal)
							DefaultValue=Board.Read(Address)
							DefaultValueBinary=hex2bin(DefaultValue,"00000000")
							valHex=hex2bin(dec2hex(Value),Holder)
							ValueString=BinaryCalculation(Holder,DefaultValueBinary,valHex)
							UpdateValue='{:0{}X}'.format(int(ValueString,2),len(ValueString)//4)
							UpdateValue="0x"+str(UpdateValue)
							Board.Write(Address,UpdateValue)
							sleep(1)
							Output_Print("Modifying Register Complete for Board:%s"%Board.ID)
							Status_Write("Modifying Register Complete for Board:%s"%Board.ID)
		else:
			LaneVal=LaneHash[int(ChannelArray[1])][ChannelArray[0]]["Lane"]
			ID=LaneHash[int(ChannelArray[1])][ChannelArray[0]]["Name"]
			Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
			Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
			Board_exists = 'Board' in locals() or 'Board' in globals() 				
			if Board_X.ID==ID:
				DefaultValue=Board_X.Read(LaneVal,Address)
				DefaultValueBinary=hex2bin(DefaultValue,"00000000")
				valHex=hex2bin(dec2hex(Value),Holder)
				ValueString=BinaryCalculation(Holder,DefaultValueBinary,valHex)
				UpdateValue='{:0{}X}'.format(int(ValueString,2),len(ValueString)//4)
				UpdateValue="0x"+str(UpdateValue)
				Board_X.Write(LaneVal,Address,UpdateValue)
				Output_Print("Modifying Register Complete for Board:%s"%Board_X.ID)
				Status_Write("Modifying Register Complete for Board:%s"%Board_X.ID)	
				return True
			elif Board_Y.ID==ID:
				DefaultValue=Board_Y.Read(LaneVal,Address)
				DefaultValueBinary=hex2bin(DefaultValue,"00000000")
				valHex=hex2bin(dec2hex(Value),Holder)
				ValueString=BinaryCalculation(Holder,DefaultValueBinary,valHex)
				UpdateValue='{:0{}X}'.format(int(ValueString,2),len(ValueString)//4)
				UpdateValue="0x"+str(UpdateValue)
				Board_Y.Write(LaneVal,Address,UpdateValue)
				Output_Print("Modifying Register Complete for Board:%s"%Board_Y.ID)
				Status_Write("Modifying Register Complete for Board:%s"%Board_Y.ID)
				return True		
			elif Board.ID==ID:
				Board.selectChip(LaneVal)
				DefaultValue=Board.Read(Address)
				DefaultValueBinary=hex2bin(DefaultValue,"00000000")
				valHex=hex2bin(dec2hex(Value),Holder)
				ValueString=BinaryCalculation(Holder,DefaultValueBinary,valHex)
				UpdateValue='{:0{}X}'.format(int(ValueString,2),len(ValueString)//4)
				UpdateValue="0x"+str(UpdateValue)
				Board.Write(Address,UpdateValue)
				sleep(1)
				Output_Print("Modifying Register Complete for Board:%s"%Board.ID)
				Status_Write("Modifying Register Complete for Board:%s"%Board.ID)
				return True		   

def SetPowerSupply(Value):
	Korad.OFF()
	SetVoltage=float(Value)
	Korad.SET_VOLTAGE(SetVoltage)
	Korad.SET_CURRENT(0.900)
	Korad.ON()
	sleep(5)


def SetOnBoardVDD(Value):
	Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
	Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
	for BrdKey in BoardConfigHash.keys():
		if BoardConfigHash[BrdKey]["Type"]=="SLTBoard":
			if Board_X_exists and Board_X.ID==BrdKey:
				Board_X.SetVDD(int(Value))
			if Board_Y_exists and Board_Y.ID==BrdKey:
				Board_Y.SetVDD(int(Value))

def SetOnBoardVDDQ(Value):
	Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
	Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
	for BrdKey in BoardConfigHash.keys():
		if BoardConfigHash[BrdKey]["Type"]=="SLTBoard":
			if Board_X_exists and Board_X.ID==BrdKey:
				Board_X.SetVDDQ(int(Value))
			if Board_Y_exists and Board_Y.ID==BrdKey:
				Board_Y.SetVDDQ(int(Value))
	for BrdKey in BoardConfigHash.keys():
		if BoardConfigHash[BrdKey]["Type"]=="SLTBoard":
			if Board_X_exists and Board_X.ID==BrdKey:
				Board_X.SetVDD(int(Value))
			if Board_Y_exists and Board_Y.ID==BrdKey:
				Board_Y.SetVDD(int(Value))

def SetTemperature(Value): #soaktime in munutes
	TemperatureChamber.WRITE_TEMP(float(Value))
	if "TEMPCHAMBER_SOAKTIME" in OtherValuesHash.keys():
		SoakTime=int(OtherValuesHash["TEMPCHAMBER_SOAKTIME"])
	else:
		SoakTime=0;
	for i in range (1,SoakTime):
		sleep(60)
		Output_Print("TempChamber is Soaking .... Please Wait")
		Status_Write("TempChamber is Soaking .... Please Wait")

def SetHumidity(Value):
	TemperatureChamber.WRITE_HUMIDITY(float(Value))
	if "TEMPCHAMBER_SOAKTIME" in OtherValuesHash.keys():
		SoakTime=int(OtherValuesHash["TEMPCHAMBER_SOAKTIME"])
	else:
		SoakTime=0;
	for i in range (1,SoakTime):
		sleep(60)
		Output_Print("HumidChamber is Soaking .... Please Wait")
		Status_Write("HumidChamber is Soaking .... Please Wait")




def MeasureDSAJitter(Lane,File="Default"):
	Output_Print("Measuring Jitter on Lane: %d\tSetupFile: %s"%(Lane,File))
	Status_Write("Measuring Jitter on Lane: %d\tSetupFile: %s"%(Lane,File))
	Scope_exists='Scope' in locals() or 'Scope' in globals()
	if not Scope_exists:
		global Scope 
		if "DSA_IPADDRESS" in OtherValuesHash.keys():
			Scope=Agilent(OtherValuesHash["DSA_IPADDRESS"])
		else:
			Scope=Agilent()
		sleep(1)
	if not "DSA_Retry" in globals() or "DSA_Retry" in locals():
		global DSA_Retry
		DSA_Retry=1
	Scope.Reset()
	Output_Print("Scope Reset Sucessful")
	Status_Write("Scope Reset Sucessful")
	if "Bert" in locals() or "Bert" in globals():
		if "DATA_ELECIDLE" in OtherValuesHash.keys() and OtherValuesHash["DATA_ELECIDLE"]=="True":
			Korad_exists='Korad' in locals() or 'Korad' in globals()
			if not Korad_exists:
				global Korad
				Korad=KA3005P(OtherValuesHash["POWERSUPPLY_COMPORT"])
			Bert.SetElectricalIdle("ON")
			Korad.OFF()
			Korad.SET_VOLTAGE(3.0)
			Korad.SET_CURRENT(0.200)
			sleep(1)
			Korad.ON()
			Bert.TurnOn()
			sleep(10)
			Korad.OFF()
			Output_Print("Electrical Idle Successful")
			Status_Write("Electrical Idle Successful")
	
	if "LS_Bert" in locals() or "LS_Bert" in globals():
		if "DATA_ELECIDLE" in OtherValuesHash.keys() and OtherValuesHash["DATA_ELECIDLE"]=="True":
			LS_Bert.TurnON("1")
			Output_Print("Electrical Idle Successful")
			Status_Write("Electrical Idle Successful")
	sleep(3)
 
	if Lane==1:
		if File!="Default":
			if not(Scope.LoadSetupFile(File)):
				print "Load Setup File Returned False Exiting...."
				sys.exit(1)
		else:
			if "DSA_SETUP_FILE_1" in OtherValuesHash.keys():
				if not(Scope.LoadSetupFile(OtherValuesHash["DSA_SETUP_FILE_1"])):
					print "Load Setup File Returned False Exiting...."
					sys.exit(1)
			else:
				if not(Scope.LoadSetupFile('C:\scope\setups\Jitter_Meas_Channel1.set')):
					print "Load Setup File Returned False Exiting...."
					sys.exit(1)
	elif Lane==2:
		if File!="Default":
			if not(Scope.LoadSetupFile(File)):
				print "Load Setup File Returned False Exiting...."
				sys.exit(1)
		else:
			if "DSA_SETUP_FILE_2" in OtherValuesHash.keys():
				if not(Scope.LoadSetupFile(OtherValuesHash["DSA_SETUP_FILE_2"])):
					print "Load Setup File Returned False Exiting...."
					sys.exit(1)
			else:
				if not(Scope.LoadSetupFile('C:\scope\setups\Jitter_Meas_Channel2.set')):
					print "Load Setup File Returned False Exiting...."
					sys.exit(1)
	Output_Print("Load Setup File Successful")
	Status_Write("Load Setup File Successful")
	sleep(2)
	#if DSA_Retry==1:
		#SetRegisterThread.join()
	ReadRXRegisterStatusThread=FuncThread(ReadRXRegisterStatus,Lane)
	ReadRXRegisterStatusThread.start()  
	sleep(2)
	if not(Scope.AutoScaleVertical(Lane)):
		sys.exit(1)
	sleep(5)
	Output_Print("AutoScale Vertical Successful")
	Status_Write("AutoScale Vertical Successful")

	if not(Scope.AcquireAndDigitize(3000000)):
		sys.exit(1)
	Output_Print("Acquire and Digitize Samples Successful")
	Status_Write("Acquire and Digitize Samples Successful")

	sleep(20)
	JitterValue=Scope.MeasureJitter(Lane)

	TJ=-1
	RJ=-1
	DJ=-1
	ReadRXRegisterStatusThread.join()	
	if (JitterValue):
		JitterArray=JitterValue.split(',')
		TJ=float(JitterArray[1])*1000000000000
		RJ=float(JitterArray[4])*1000000000000
		DJ=float(JitterArray[7])*1000000000000
		if ((TJ>10000)or(TJ<20)) or RJ>10000 or DJ>10000:
			if "DSA_RETRY" in OtherValuesHash.keys(): 
				MaxCount=int(OtherValuesHash["DSA_RETRY"])
				if DSA_Retry<MaxCount:
					DSA_Retry=DSA_Retry+1
					Output_Print("Unable to Capture Jitter Retrying Current: %d Maximum Allowed: %d"%(DSA_Retry,int(OtherValuesHash["DSA_RETRY"])))
					Status_Write("Unable to Capture Jitter Retrying Current: %d Maximum Allowed: %d"%(DSA_Retry,int(OtherValuesHash["DSA_RETRY"])))
					Scope.Reset()
					Bert_exists='Bert' in locals() or 'Bert' in globals()
					if Bert_exists:
						Bert.TurnOff()
						sleep(1)
						Bert.TurnOn()
					MeasureDSAJitter(Lane,File)
					return 0
			TJ=-1
			RJ=-1
			DJ=-1
		DSA_Retry=1
	else:
		if "DSA_RETRY" in OtherValuesHash.keys(): 
			MaxCount=int(OtherValuesHash["DSA_RETRY"])
			if DSA_Retry<MaxCount:
				DSA_Retry=DSA_Retry+1
				Output_Print("Unable to Capture Jitter Retrying Current: %d Maximum Allowed: %d"%(DSA_Retry,int(OtherValuesHash["DSA_RETRY"])))
				Status_Write("Unable to Capture Jitter Retrying Current: %d Maximum Allowed: %d"%(DSA_Retry,int(OtherValuesHash["DSA_RETRY"])))
				Scope.Reset()
				Bert_exists='Bert' in locals() or 'Bert' in globals()
				if Bert_exists:
					Bert.TurnOff()
					sleep(2)
					Bert.TurnOn()
				MeasureDSAJitter(Lane,File)
				return 0
		
	Output_Print("Jitter Value: TJ= %.2f ps\tRJ=%.2f ps\tDJ=%.2f ps"%(TJ,RJ,DJ))
	Status_Write("Jitter Value: TJ= %.2f ps\tRJ=%.2f ps\tDJ=%.2f ps"%(TJ,RJ,DJ))
	
	OUTPUT_DATA_HASH["TJ"]=TJ
	OUTPUT_DATA_HASH["RJ"]=RJ
	OUTPUT_DATA_HASH["DJ"]=DJ
				
	OUTPUT.write("%.2f,%.2f,%.2f,"%(float(TJ), float(RJ), float(DJ)))
	
	if "READ_MISC_STATUS" in OtherValuesHash.keys() and OtherValuesHash["READ_MISC_STATUS"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["MiscStatus"])
		Output_Print("Reading MiscStatus at %s"%OUTPUT_DATA_HASH["MiscStatus"])
		Status_Write("Reading MiscStatus at %s"%OUTPUT_DATA_HASH["MiscStatus"])

	if "READ_REPLICA_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_REPLICA_OFFSET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["ReplicaOffset"])
		Output_Print("Reading ReplicaOffset at %s"%OUTPUT_DATA_HASH["ReplicaOffset"])
		Status_Write("Reading ReplicaOffset at %s"%OUTPUT_DATA_HASH["ReplicaOffset"])

	if "READ_EYE_HEIGHT" in OtherValuesHash.keys() and OtherValuesHash["READ_EYE_HEIGHT"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["EyeHeight"])
		Output_Print("Reading EyeHeight at %s"%OUTPUT_DATA_HASH["EyeHeight"])
		Status_Write("Reading EyeHeight at %s"%OUTPUT_DATA_HASH["EyeHeight"])
				 
	if "READ_UPPER_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_UPPER_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["UpperSet"])
		Output_Print("Reading UpperSet at %s"%OUTPUT_DATA_HASH["UpperSet"])
		Status_Write("Reading UpperSet at %s"%OUTPUT_DATA_HASH["UpperSet"])
				 
	if "READ_SUMM_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_SUMM_OFFSET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["SummOff"])
		Output_Print("Reading SummOff at %s"%OUTPUT_DATA_HASH["SummOff"])
		Status_Write("Reading SummOff at %s"%OUTPUT_DATA_HASH["SummOff"])
				 
	if "READ_REFERENCE_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_REFERENCE_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["RefSet"])
		Output_Print("Reading RefSet at %s"%OUTPUT_DATA_HASH["RefSet"])
		Status_Write("Reading RefSet at %s"%OUTPUT_DATA_HASH["RefSet"])
		 
	if "READ_GAIN_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_GAIN_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["GainSet"])
		Output_Print("Reading GainSet at %s"%OUTPUT_DATA_HASH["GainSet"])
		Status_Write("Reading GainSet at %s"%OUTPUT_DATA_HASH["GainSet"])		 

def MeasureDSAJitterReTimerON(Lane,File="Default"):

	TXPassAccu,RXPassAccu = checkTXRXRetimer(Lane,RunTimeHash[0])	

	Output_Print("Measuring Jitter on Lane: %d\tSetupFile: %s"%(Lane,File))
	Status_Write("Measuring Jitter on Lane: %d\tSetupFile: %s"%(Lane,File))
	Scope_exists='Scope' in locals() or 'Scope' in globals()
	if not Scope_exists:
		global Scope 
		if "DSA_IPADDRESS" in OtherValuesHash.keys():
			Scope=Agilent(OtherValuesHash["DSA_IPADDRESS"])
		else:
			Scope=Agilent()
		sleep(1)
	if not "DSA_Retry" in globals() or "DSA_Retry" in locals():
		global DSA_Retry
		DSA_Retry=1
	Scope.Reset()
	Output_Print("Scope Reset Sucessful")
	Status_Write("Scope Reset Sucessful")
	if "Bert" in locals() or "Bert" in globals():
		if "DATA_ELECIDLE" in OtherValuesHash.keys() and OtherValuesHash["DATA_ELECIDLE"]=="True":
			Korad_exists='Korad' in locals() or 'Korad' in globals()
			if not Korad_exists:
				global Korad
				Korad=KA3005P(OtherValuesHash["POWERSUPPLY_COMPORT"])
			Bert.SetElectricalIdle("ON")
			Korad.OFF()
			Korad.SET_VOLTAGE(3.0)
			Korad.SET_CURRENT(0.200)
			sleep(1)
			Korad.ON()
			Bert.TurnOn()
			sleep(10)
			Korad.OFF()
			Output_Print("Electrical Idle Successful")
			Status_Write("Electrical Idle Successful")
	
	if "LS_Bert" in locals() or "LS_Bert" in globals():
		if "DATA_ELECIDLE" in OtherValuesHash.keys() and OtherValuesHash["DATA_ELECIDLE"]=="True":
			LS_Bert.TurnON("1")
			Output_Print("Electrical Idle Successful")
			Status_Write("Electrical Idle Successful")
	sleep(3)
 
	if Lane==1:
		if File!="Default":
			if not(Scope.LoadSetupFile(File)):
				print "Load Setup File Returned False Exiting...."
				sys.exit(1)
		else:
			if "DSA_SETUP_FILE_1" in OtherValuesHash.keys():
				if not(Scope.LoadSetupFile(OtherValuesHash["DSA_SETUP_FILE_1"])):
					print "Load Setup File Returned False Exiting...."
					sys.exit(1)
			else:
				if not(Scope.LoadSetupFile('C:\scope\setups\Jitter_Meas_Channel1.set')):
					print "Load Setup File Returned False Exiting...."
					sys.exit(1)
	elif Lane==2:
		if File!="Default":
			if not(Scope.LoadSetupFile(File)):
				print "Load Setup File Returned False Exiting...."
				sys.exit(1)
		else:
			if "DSA_SETUP_FILE_2" in OtherValuesHash.keys():
				if not(Scope.LoadSetupFile(OtherValuesHash["DSA_SETUP_FILE_2"])):
					print "Load Setup File Returned False Exiting...."
					sys.exit(1)
			else:
				if not(Scope.LoadSetupFile('C:\scope\setups\Jitter_Meas_Channel2.set')):
					print "Load Setup File Returned False Exiting...."
					sys.exit(1)
	Output_Print("Load Setup File Successful")
	Status_Write("Load Setup File Successful")
	#if DSA_Retry==1:
		#SetRegisterThread.join()
	ReadRXRegisterStatusThread=FuncThread(ReadRXRegisterStatus,Lane)
	ReadRXRegisterStatusThread.start()  
	sleep(2)
	if not(Scope.AutoScaleVertical(Lane)):
		sys.exit(1)
	sleep(5)
	Output_Print("AutoScale Vertical Successful")
	Status_Write("AutoScale Vertical Successful")

	if not(Scope.AcquireAndDigitize(3000000)):
		sys.exit(1)
	Output_Print("Acquire and Digitize Samples Successful")
	Status_Write("Acquire and Digitize Samples Successful")

	sleep(20)
	JitterValue=Scope.MeasureJitter(Lane)

	TJ=-1
	RJ=-1
	DJ=-1
	ReadRXRegisterStatusThread.join()	
	if (JitterValue):
		JitterArray=JitterValue.split(',')
		TJ=float(JitterArray[1])*1000000000000
		RJ=float(JitterArray[4])*1000000000000
		DJ=float(JitterArray[7])*1000000000000
		if ((TJ>10000)or(TJ<20)) or RJ>10000 or DJ>10000:
			if "DSA_RETRY" in OtherValuesHash.keys(): 
				MaxCount=int(OtherValuesHash["DSA_RETRY"])
				if DSA_Retry<MaxCount:
					DSA_Retry=DSA_Retry+1
					Output_Print("Unable to Capture Jitter Retrying Current: %d Maximum Allowed: %d"%(DSA_Retry,int(OtherValuesHash["DSA_RETRY"])))
					Status_Write("Unable to Capture Jitter Retrying Current: %d Maximum Allowed: %d"%(DSA_Retry,int(OtherValuesHash["DSA_RETRY"])))
					Scope.Reset()
					Bert_exists='Bert' in locals() or 'Bert' in globals()
					if Bert_exists:
						Bert.TurnOff()
						sleep(1)
						Bert.TurnOn()
					MeasureDSAJitter(Lane,File)
					return 0
			TJ=-1
			RJ=-1
			DJ=-1
		DSA_Retry=1
	else:
		if "DSA_RETRY" in OtherValuesHash.keys(): 
			MaxCount=int(OtherValuesHash["DSA_RETRY"])
			if DSA_Retry<MaxCount:
				DSA_Retry=DSA_Retry+1
				Output_Print("Unable to Capture Jitter Retrying Current: %d Maximum Allowed: %d"%(DSA_Retry,int(OtherValuesHash["DSA_RETRY"])))
				Status_Write("Unable to Capture Jitter Retrying Current: %d Maximum Allowed: %d"%(DSA_Retry,int(OtherValuesHash["DSA_RETRY"])))
				Scope.Reset()
				Bert_exists='Bert' in locals() or 'Bert' in globals()
				if Bert_exists:
					Bert.TurnOff()
					sleep(2)
					Bert.TurnOn()
				MeasureDSAJitter(Lane,File)
				return 0
		
	Output_Print("Jitter Value: TJ= %.2f ps\tRJ=%.2f ps\tDJ=%.2f ps"%(TJ,RJ,DJ))
	Status_Write("Jitter Value: TJ= %.2f ps\tRJ=%.2f ps\tDJ=%.2f ps"%(TJ,RJ,DJ))
	
	OUTPUT_DATA_HASH["TJ"]=TJ
	OUTPUT_DATA_HASH["RJ"]=RJ
	OUTPUT_DATA_HASH["DJ"]=DJ 
	
	if RXPassAccu == "FAIL" and TJ != "-1":
		TJ = (TJ * -1)

	OUTPUT.write("%.2f,%.2f,%.2f,%s,%s,"%( float(OUTPUT_DATA_HASH["TJ"]), float(OUTPUT_DATA_HASH["RJ"]), float(OUTPUT_DATA_HASH["DJ"]),TXPassAccu, RXPassAccu))
	
	if "READ_MISC_STATUS" in OtherValuesHash.keys() and OtherValuesHash["READ_MISC_STATUS"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["MiscStatus"])
		Output_Print("Reading MiscStatus at %s"%OUTPUT_DATA_HASH["MiscStatus"])
		Status_Write("Reading MiscStatus at %s"%OUTPUT_DATA_HASH["MiscStatus"])

	if "READ_REPLICA_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_REPLICA_OFFSET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["ReplicaOffset"])
		Output_Print("Reading ReplicaOffset at %s"%OUTPUT_DATA_HASH["ReplicaOffset"])
		Status_Write("Reading ReplicaOffset at %s"%OUTPUT_DATA_HASH["ReplicaOffset"])

	if "READ_EYE_HEIGHT" in OtherValuesHash.keys() and OtherValuesHash["READ_EYE_HEIGHT"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["EyeHeight"])
		Output_Print("Reading EyeHeight at %s"%OUTPUT_DATA_HASH["EyeHeight"])
		Status_Write("Reading EyeHeight at %s"%OUTPUT_DATA_HASH["EyeHeight"])
				 
	if "READ_UPPER_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_UPPER_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["UpperSet"])
		Output_Print("Reading UpperSet at %s"%OUTPUT_DATA_HASH["UpperSet"])
		Status_Write("Reading UpperSet at %s"%OUTPUT_DATA_HASH["UpperSet"])
				 
	if "READ_SUMM_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_SUMM_OFFSET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["SummOff"])
		Output_Print("Reading SummOff at %s"%OUTPUT_DATA_HASH["SummOff"])
		Status_Write("Reading SummOff at %s"%OUTPUT_DATA_HASH["SummOff"])
				 
	if "READ_REFERENCE_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_REFERENCE_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["RefSet"])
		Output_Print("Reading RefSet at %s"%OUTPUT_DATA_HASH["RefSet"])
		Status_Write("Reading RefSet at %s"%OUTPUT_DATA_HASH["RefSet"])
		 
	if "READ_GAIN_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_GAIN_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["GainSet"])
		Output_Print("Reading GainSet at %s"%OUTPUT_DATA_HASH["GainSet"])
		Status_Write("Reading GainSet at %s"%OUTPUT_DATA_HASH["GainSet"])

def MeasureDSAFrequency(Channel):
	Output_Print("Measuring Frequency Now on Lane: %d"%Channel)
	Status_Write("Measuring Frequency Now on Lane: %d"%Channel)
	Scope_exists='Scope' in locals() or 'Scope' in globals()
	if not Scope_exists:
		global Scope 
		if "DSA_IPADDRESS" in OtherValuesHash.keys():
			Scope=Agilent(OtherValuesHash["DSA_IPADDRESS"])
		else:
			Scope=Agilent()
		sleep(2)
	Scope.Reset()
	Output_Print("Scope Reset Sucessful")
	Status_Write("Scope Reset Sucessful")

	sleep(1)
	Scope.WriteCommand(":AUToscale")
	ReadRXRegisterStatusThread=FuncThread(ReadRXRegisterStatus,Channel)
	ReadRXRegisterStatusThread.start()
	if Channel==1:
		Scope.WriteCommand(":SYSTem:HEADer OFF")
		Scope.WriteCommand(":CHANnel1:DISPlay ON")
		Scope.WriteCommand(":CHANnel2:DISPlay OFF")
		Scope.WriteCommand(":CHANnel3:DISPlay ON")
		Scope.WriteCommand(":CHANnel4:DISPlay OFF")   
		Scope.WriteCommand(":CHANnel1:DIFFerential ON")		 
		Scope.WriteCommand(":MEASure:SOURce CHANnel1")
		Scope.WriteCommand(":TIMebase:SCALe 100e-9")
		Scope.WriteCommand(":MEASure:FREQuency")
		sleep(2)
		Scope.WriteCommand(":ACQUIRE:AVERAGE ON")
		if "DSA_AVERAGE_COUNT" in OtherValuesHash.keys():
			Command=":ACQUIRE:COUNT "+OtherValuesHash["DSA_AVERAGE_COUNT"]
			Scope.WriteCommand(Command)
		else:
			Scope.WriteCommand(":ACQUIRE:COUNT 1024")	
		sleep(1)
		Scope.WriteCommand(":HISTOgram:MODE MEASurement")
		sleep(5)
		Scope.WriteCommand(":MEASure:HISTogram:MEAN CHANnel1")
	elif Channel ==2:
		Scope.WriteCommand(":SYSTem:HEADer OFF")
		Scope.WriteCommand(":CHANnel1:DISPlay OFF")
		Scope.WriteCommand(":CHANnel2:DISPlay ON")
		Scope.WriteCommand(":CHANnel3:DISPlay OFF")
		Scope.WriteCommand(":CHANnel4:DISPlay ON")
		Scope.WriteCommand(":CHANnel2:DIFFerential ON")		   
		Scope.WriteCommand(":MEASure:SOURce CHANnel2")
		Scope.WriteCommand(":TIMebase:SCALe 100e-9")
		Scope.WriteCommand(":MEASure:FREQuency")
		sleep(2)
		Scope.WriteCommand(":ACQUIRE:AVERAGE ON")
		if "DSA_AVERAGE_COUNT" in OtherValuesHash.keys():
			Command=":ACQUIRE:COUNT "+OtherValuesHash["DSA_AVERAGE_COUNT"]
			Scope.WriteCommand(Command)
		else:
			Scope.WriteCommand(":ACQUIRE:COUNT 1024")	
		sleep(1)
		Scope.WriteCommand(":HISTOgram:MODE MEASurement")
		sleep(5)
		Scope.WriteCommand(":MEASure:HISTogram:MEAN CHANnel2")

	sleep(1)
	val=Scope.QueryValues(":MEASure:HISTOgram:MEAN?")
	FreqValue=float(val)
	Output_Print("Frequency value is: %.2f"%FreqValue)
	Status_Write("Frequency value is: %.2f"%FreqValue)
	
	OUTPUT_DATA_HASH["Freq"]=FreqValue
	OUTPUT.write("%.2f,"%OUTPUT_DATA_HASH["Freq"])
	ReadRXRegisterStatusThread.join()
	if "READ_MISC_STATUS" in OtherValuesHash.keys() and OtherValuesHash["READ_MISC_STATUS"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["MiscStatus"])
		Output_Print("Reading MiscStatus at %s"%OUTPUT_DATA_HASH["MiscStatus"])
		Status_Write("Reading MiscStatus at %s"%OUTPUT_DATA_HASH["MiscStatus"])

	if "READ_REPLICA_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_REPLICA_OFFSET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["ReplicaOffset"])
		Output_Print("Reading ReplicaOffset at %s"%OUTPUT_DATA_HASH["ReplicaOffset"])
		Status_Write("Reading ReplicaOffset at %s"%OUTPUT_DATA_HASH["ReplicaOffset"])

	if "READ_EYE_HEIGHT" in OtherValuesHash.keys() and OtherValuesHash["READ_EYE_HEIGHT"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["EyeHeight"])
		Output_Print("Reading EyeHeight at %s"%OUTPUT_DATA_HASH["EyeHeight"])
		Status_Write("Reading EyeHeight at %s"%OUTPUT_DATA_HASH["EyeHeight"])
				 
	if "READ_UPPER_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_UPPER_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["UpperSet"])
		Output_Print("Reading UpperSet at %s"%OUTPUT_DATA_HASH["UpperSet"])
		Status_Write("Reading UpperSet at %s"%OUTPUT_DATA_HASH["UpperSet"])
				 
	if "READ_SUMM_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_SUMM_OFFSET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["SummOff"])
		Output_Print("Reading SummOff at %s"%OUTPUT_DATA_HASH["SummOff"])
		Status_Write("Reading SummOff at %s"%OUTPUT_DATA_HASH["SummOff"])
				 
	if "READ_REFERENCE_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_REFERENCE_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["RefSet"])
		Output_Print("Reading RefSet at %s"%OUTPUT_DATA_HASH["RefSet"])
		Status_Write("Reading RefSet at %s"%OUTPUT_DATA_HASH["RefSet"])
		 
	if "READ_GAIN_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_GAIN_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["GainSet"])
		Output_Print("Reading GainSet at %s"%OUTPUT_DATA_HASH["GainSet"])
		Status_Write("Reading GainSet at %s"%OUTPUT_DATA_HASH["GainSet"])
	
def MeasureDSAAmplitude(Channel):
	Output_Print("Measuring Amplitude Now on Lane: %d"%Channel)
	Status_Write("Measuring Amplitude Now on Lane: %d"%Channel)
	Scope_exists='Scope' in locals() or 'Scope' in globals()
	if not Scope_exists:
		global Scope 
		if "DSA_IPADDRESS" in OtherValuesHash.keys():
			Scope=Agilent(OtherValuesHash["DSA_IPADDRESS"])
		else:
			Scope=Agilent()
		sleep(2)
	Scope.Reset()
	Output_Print("Scope Reset Sucessful")
	Status_Write("Scope Reset Sucessful")
	sleep(1)
	Scope.WriteCommand("*CLS")
	Scope.WriteCommand(":AUToscale")
	ReadRXRegisterStatusThread=FuncThread(ReadRXRegisterStatus,Channel)
	ReadRXRegisterStatusThread.start()
	if Channel==1:
		Scope.WriteCommand(":CHANnel1:DISPlay ON")
		Scope.WriteCommand(":CHANnel2:DISPlay OFF")
		Scope.WriteCommand(":CHANnel3:DISPlay OFF")
		Scope.WriteCommand(":CHANnel4:DISPlay OFF")				
		Scope.WriteCommand(":CHANnel1:SCALe 1.0")
		Scope.WriteCommand(":CHANnel1:OFFSet 0")
		Scope.WriteCommand(":MEASure:SOURce CHANnel1")
		Scope.WriteCommand(":MEASure:VMAX CHANNEL1")
		Scope.WriteCommand(":ACQUIRE:AVERAGE ON")
		if "DSA_AVERAGE_COUNT" in OtherValuesHash.keys():
			Command=":ACQUIRE:COUNT "+OtherValuesHash["DSA_AVERAGE_COUNT"]
			Scope.WriteCommand(Command)
		else:
			Scope.WriteCommand(":ACQUIRE:COUNT 1024")	
		sleep(2)
		Scope.WriteCommand(":HISTOgram:MODE MEASurement")
		Scope.WriteCommand(":MEASure:HISTogram:MEAN CHANnel1")
	elif Channel ==2:
		Scope.WriteCommand(":CHANnel1:DISPlay OFF")
		Scope.WriteCommand(":CHANnel2:DISPlay ON")
		Scope.WriteCommand(":CHANnel3:DISPlay OFF")
		Scope.WriteCommand(":CHANnel4:DISPlay OFF")
				
		Scope.WriteCommand(":CHANnel2:SCALe 1.0")
		Scope.WriteCommand(":CHANnel2:OFFSet 0")
		Scope.WriteCommand(":MEASure:SOURce CHANnel2")
		Scope.WriteCommand(":MEASure:VMAX CHANNEL2")
		Scope.WriteCommand(":ACQUIRE:AVERAGE ON")
		if "DSA_AVERAGE_COUNT" in OtherValuesHash.keys():
			Command=":ACQUIRE:COUNT "+OtherValuesHash["DSA_AVERAGE_COUNT"]
			Scope.WriteCommand(Command)
		else:
			Scope.WriteCommand(":ACQUIRE:COUNT 1024")	
		sleep(2)
		Scope.WriteCommand(":HISTOgram:MODE MEASurement")
		Scope.WriteCommand(":MEASure:HISTogram:MEAN CHANnel2")

	sleep(1)
	val=Scope.QueryValues(":MEASure:HISTOgram:MEAN?")
	Amplitude=float(val)
	Output_Print("Amplitude value is: %.2f"%Amplitude)
	Status_Write("Amplitude value is: %.2f"%Amplitude)
	
	OUTPUT_DATA_HASH["Amplitude"]=Amplitude
	OUTPUT.write("%.2f,"%OUTPUT_DATA_HASH["Amplitude"])
	ReadRXRegisterStatusThread.join()
	if "READ_MISC_STATUS" in OtherValuesHash.keys() and OtherValuesHash["READ_MISC_STATUS"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["MiscStatus"])
		Output_Print("Reading MiscStatus at %s"%OUTPUT_DATA_HASH["MiscStatus"])
		Status_Write("Reading MiscStatus at %s"%OUTPUT_DATA_HASH["MiscStatus"])

	if "READ_REPLICA_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_REPLICA_OFFSET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["ReplicaOffset"])
		Output_Print("Reading ReplicaOffset at %s"%OUTPUT_DATA_HASH["ReplicaOffset"])
		Status_Write("Reading ReplicaOffset at %s"%OUTPUT_DATA_HASH["ReplicaOffset"])

	if "READ_EYE_HEIGHT" in OtherValuesHash.keys() and OtherValuesHash["READ_EYE_HEIGHT"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["EyeHeight"])
		Output_Print("Reading EyeHeight at %s"%OUTPUT_DATA_HASH["EyeHeight"])
		Status_Write("Reading EyeHeight at %s"%OUTPUT_DATA_HASH["EyeHeight"])
				 
	if "READ_UPPER_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_UPPER_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["UpperSet"])
		Output_Print("Reading UpperSet at %s"%OUTPUT_DATA_HASH["UpperSet"])
		Status_Write("Reading UpperSet at %s"%OUTPUT_DATA_HASH["UpperSet"])
				 
	if "READ_SUMM_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_SUMM_OFFSET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["SummOff"])
		Output_Print("Reading SummOff at %s"%OUTPUT_DATA_HASH["SummOff"])
		Status_Write("Reading SummOff at %s"%OUTPUT_DATA_HASH["SummOff"])
				 
	if "READ_REFERENCE_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_REFERENCE_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["RefSet"])
		Output_Print("Reading RefSet at %s"%OUTPUT_DATA_HASH["RefSet"])
		Status_Write("Reading RefSet at %s"%OUTPUT_DATA_HASH["RefSet"])
		 
	if "READ_GAIN_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_GAIN_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["GainSet"])
		Output_Print("Reading GainSet at %s"%OUTPUT_DATA_HASH["GainSet"])
		Status_Write("Reading GainSet at %s"%OUTPUT_DATA_HASH["GainSet"])


def Meas_BertScope():
	Output_Print("Measuring BertScope for BER and Jitter")
	Status_Write("Measuring BertScope for BER and Jitter")
	BSA_exists='BSA' in locals() or 'BSA' in globals()
	if not BSA_exists:
		global BSA
		BSA=BertScope("10.1.40.55")
		Output_Print("Initialization of Bertscope for First Time will take some time")
		Status_Write("Initialization of Bertscope for First Time will take some time")
		BSA.cmdBert("VIEW GEN")
		BSA.setGenClockRate(6000000000)
		BSA.setGenClockDivisor(1)
		BSA.enGenSSC(0)
		BSA.loadGenPatt('PN7')
		BSA.LinkPosNegClocks(0)
		BSA.setClockPosOutputLevels(200,-200)
		BSA.setClockNegOutputLevels(200,-200)
		BSA.LinkPosNegClocks(1)
		Output_Print("Complete Initialization of Bertscope for First Time")
		Status_Write("Complete Initialization of Bertscope for First Time")

	Output_Print("Collecting Bit Error Rate of the point")
	Status_Write("Collecting Bit Error Rate of the point")	
	BER_Value=BSA.MeasureBER()
	OUTPUT.write("%s,"%BER_Value)
	Output_Print("BER Value is %s"%BER_Value)
	Status_Write("BER Value is %s"%BER_Value)
	Output_Print("Collecting Jitter Values of the point")
	Status_Write("Collecting Jitter Values of the point")	
	Jitter=BSA.MeasureJitter()
	Output_Print("Jitter Value is %s"%Jitter)
	Status_Write("Jitter Value is %s"%Jitter)
	OUTPUT.write("%s,"%Jitter)
	BSA.ShowEye()
	
	ReadRXRegisterStatus(1)

	if "READ_MISC_STATUS" in OtherValuesHash.keys() and OtherValuesHash["READ_MISC_STATUS"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["MiscStatus"])
		Output_Print("Reading MiscStatus at %s"%OUTPUT_DATA_HASH["MiscStatus"])
		Status_Write("Reading MiscStatus at %s"%OUTPUT_DATA_HASH["MiscStatus"])

	if "READ_REPLICA_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_REPLICA_OFFSET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["ReplicaOffset"])
		Output_Print("Reading ReplicaOffset at %s"%OUTPUT_DATA_HASH["ReplicaOffset"])
		Status_Write("Reading ReplicaOffset at %s"%OUTPUT_DATA_HASH["ReplicaOffset"])

	if "READ_EYE_HEIGHT" in OtherValuesHash.keys() and OtherValuesHash["READ_EYE_HEIGHT"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["EyeHeight"])
		Output_Print("Reading EyeHeight at %s"%OUTPUT_DATA_HASH["EyeHeight"])
		Status_Write("Reading EyeHeight at %s"%OUTPUT_DATA_HASH["EyeHeight"])
				 
	if "READ_UPPER_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_UPPER_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["UpperSet"])
		Output_Print("Reading UpperSet at %s"%OUTPUT_DATA_HASH["UpperSet"])
		Status_Write("Reading UpperSet at %s"%OUTPUT_DATA_HASH["UpperSet"])
				 
	if "READ_SUMM_OFFSET" in OtherValuesHash.keys() and OtherValuesHash["READ_SUMM_OFFSET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["SummOff"])
		Output_Print("Reading SummOff at %s"%OUTPUT_DATA_HASH["SummOff"])
		Status_Write("Reading SummOff at %s"%OUTPUT_DATA_HASH["SummOff"])
				 
	if "READ_REFERENCE_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_REFERENCE_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["RefSet"])
		Output_Print("Reading RefSet at %s"%OUTPUT_DATA_HASH["RefSet"])
		Status_Write("Reading RefSet at %s"%OUTPUT_DATA_HASH["RefSet"])
		 
	if "READ_GAIN_SET" in OtherValuesHash.keys() and OtherValuesHash["READ_GAIN_SET"]=="True":
		OUTPUT.write("%s,"%OUTPUT_DATA_HASH["GainSet"])
		Output_Print("Reading GainSet at %s"%OUTPUT_DATA_HASH["GainSet"])
		Status_Write("Reading GainSet at %s"%OUTPUT_DATA_HASH["GainSet"])	



def MeasureMultimeter(Task):
	Output_Print("Measuring Multimeter Now for Task %s"%Task)
	Status_Write("Measuring Multimeter Now for Task %s"%Task)
	
	Multi_VDD_exists='Multi_VDD' in locals() or 'Multi_VDD' in globals()
	if not Multi_VDD_exists:
		global Multi_VDD 
		Multi_VDD=Keithley_2110("USB0::0x05E6::0x2110::1421277::INSTR")
		sleep(2)
	Multi_VDD.Reset()
	sleep(1)
	if Task=="Voltage":
		Voltage=float(Multi_VDD.MeasVolt())
		Output_Print("Voltage Measured is: %.5f"%Voltage)
		Status_Write("Voltage Measured is: %.5f"%Voltage)
		OUTPUT.write("%.5f,"%Voltage)
	Multi_LDO_exists='Multi_LDO' in locals() or 'Multi_LDO' in globals()
	if not Multi_VDD_exists:
		global Multi_LDO 
		Multi_LDO=Keithley_2110("USB0::0x05E6::0x2110::1424501::INSTR")

	ReadLDOStatus("RF_LDO",2)
	Multi_LDO.Reset()
	sleep(1)
	Voltage=float(Multi_LDO.MeasVolt())
	Output_Print("RF LDO Measured is: %.5f"%Voltage)
	Status_Write("RF LDO Measured is: %.5f"%Voltage)
	OUTPUT.write("%.5f,"%Voltage)
	
	ReadLDOStatus("BB_LDO",2)
	sleep(2)
	Multi_LDO.Reset()
	sleep(1)
	Voltage=float(Multi_LDO.MeasVolt())
	Output_Print("BB LDO Measured is: %.5f"%Voltage)
	Status_Write("BB LDO Measured is: %.5f"%Voltage)
	OUTPUT.write("%.5f,"%Voltage)

	ReadLDOStatus("OD_LDO",2)
	Multi_LDO.Reset()
	sleep(1)
	Voltage=float(Multi_LDO.MeasVolt())
	Output_Print("OD LDO Measured is: %.5f"%Voltage)
	Status_Write("OD LDO Measured is: %.5f"%Voltage)
	OUTPUT.write("%.5f,"%Voltage)


def PreConditionFunction(Key):
	Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
	Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
	Board_exists='Board' in locals() or 'Board' in globals()
	Status_Write("Setting TX Side")
	Output_Print("Setting TX Side")
	if Key in PreCondHash.keys():
		for TXRX in PreCondHash[Key].keys():
			if TXRX=='TX':
				for Lane in PreCondHash[Key][TXRX].keys():
					for Counter in PreCondHash[Key][TXRX][Lane].keys():
						if Lane=='1':
							for TEST_BOARD in BoardConfigHash.keys():
								if BoardConfigHash[TEST_BOARD]["Type"]=="SLTBoard":						 
									if "Port_1" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_1"]==TXRX:
										if Board_X_exists and TEST_BOARD==Board_X.ID:
											Board_X.Write("L1",PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])
										elif Board_Y_exists and TEST_BOARD==Board_X.ID:
											Board_Y.Write("L1",PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])
								elif BoardConfigHash[TEST_BOARD]["Type"]=="HIDBoard":						 
									if "Port_1" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_1"]==TXRX:
										if Board_exists and TEST_BOARD==Board.ID:
											Board.selectChip("L1")
											Board.Write(PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])
									elif "Port_2" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_2"]==TXRX:
										if Board_exists and TEST_BOARD==Board.ID:
											Board.selectChip("L2")
											Board.Write(PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])
						elif Lane=='2':
							for TEST_BOARD in BoardConfigHash.keys():
								if BoardConfigHash[TEST_BOARD]["Type"]=="SLTBoard":						 
									if "Port_2" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_2"]==TXRX:
										if Board_X_exists and TEST_BOARD==Board_X.ID:
											Board_X.Write("L2",PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])
										elif Board_Y_exists and TEST_BOARD==Board_X.ID:
											Board_Y.Write("L2",PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])


	Status_Write("Complete Setting TX Side")
	Output_Print("Complete Setting TX Side")
	sleep(10)
	Status_Write("Setting RX Side")
	Output_Print("Setting RX Side")
	if Key in PreCondHash.keys():
		for TXRX in PreCondHash[Key].keys():
			if TXRX=='RX':
				for Lane in PreCondHash[Key][TXRX].keys():
					for Counter in PreCondHash[Key][TXRX][Lane].keys():
						if Lane=='1':
							for TEST_BOARD in BoardConfigHash.keys():
								if BoardConfigHash[TEST_BOARD]["Type"]=="SLTBoard":						 
									if "Port_1" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_1"]==TXRX:
										if Board_X_exists and TEST_BOARD==Board_X.ID:
											Board_X.Write("L1",PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])
										elif Board_Y_exists and TEST_BOARD==Board_X.ID:
											Board_Y.Write("L1",PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])
								elif BoardConfigHash[TEST_BOARD]["Type"]=="HIDBoard":						 
									if "Port_1" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_1"]==TXRX:
										if Board_exists and TEST_BOARD==Board.ID:
											Board.selectChip("L1")
											Board.Write(PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])
									elif "Port_2" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_2"]==TXRX:
										if Board_exists and TEST_BOARD==Board.ID:
											Board.selectChip("L2")
											Board.Write(PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])
						elif Lane=='2':
							for TEST_BOARD in BoardConfigHash.keys():
								if BoardConfigHash[TEST_BOARD]["Type"]=="SLTBoard":						 
									if "Port_2" in BoardConfigHash[TEST_BOARD].keys() and BoardConfigHash[TEST_BOARD]["Port_2"]==TXRX:
										if Board_X_exists and TEST_BOARD==Board_X.ID:
											Board_X.Write("L2",PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])
										elif Board_Y_exists and TEST_BOARD==Board_X.ID:
											Board_Y.Write("L2",PreCondHash[Key][TXRX][Lane][Counter]["Address"],PreCondHash[Key][TXRX][Lane][Counter]["Value"])				
	Status_Write("Complete Setting RX Side")
	Output_Print("Complete Setting RX Side")

def SetData(Type,SubType,DataRate,DataLevel):
	Bert_exists='Bert' in locals() or 'Bert' in globals()
	if not Bert_exists:
		global Bert 
		if "BERT_IPADDRESS" in OtherValuesHash.keys():
			Bert=JBert(OtherValuesHash["BERT_IPADDRESS"])
		else:
			Bert=JBert()
	Bert.TurnOff()
	Bert.SelectPattern(Type,SubType)
	Bert.SetVoltage(DataLevel)
	Bert.SetDataRate(DataRate)
	Bert.TurnOn()

def SetLSData(Type,Freq,DataLevel):
	LS_Bert_exists='LS_Bert' in locals() or 'LS_Bert' in globals()
	if not LS_Bert_exists:
		global LS_Bert 
		if "AGILENT_LS_ADDRESS" in OtherValuesHash.keys():
			LS_Bert=Agilent_LS(OtherValuesHash["AGILENT_LS_ADDRESS"])
		else:
			LS_Bert=Agilent_LS()
	LS_Bert.Reset()
	LS_Bert.TurnOFF()
	if Type=="PRBS7":
		LS_Bert.SetPRBSPattern()
	LS_Bert.SetFrequency(Freq)
	LS_Bert.SetVoltage(DataLevel)
	LS_Bert.TurnON("1")
	
def Plot_Data(fileName=""):
	if fileName=="":
		Status_Write("No File Name has been specified for Plotting")
		Output_Print("No File Name has been specified for Plotting")
		fileName=easygui.fileopenbox()
	else:
		Status_Write("File Name specified is %s"%fileName)
		Output_Print("File Name specified is %s"%fileName)

	DataPlot=[]
	DataPlot.append("CH1_DUAL_TJ")
	DataPlot.append("CH1_DUAL_EyeHeight")
	DataPlot.append("CH1_DUAL_GainSet")
	DataPlot.append("CH1_SINGLE_TJ")
	DataPlot.append("CH1_SINGLE_EyeHeight")
	DataPlot.append("CH1_SINGLE_GainSet")
	DataPlot.append("CH2_DUAL_TJ")
	DataPlot.append("CH2_DUAL_EyeHeight")
	DataPlot.append("CH2_DUAL_GainSet")
	DataPlot.append("CH2_SINGLE_TJ")
	DataPlot.append("CH2_SINGLE_EyeHeight")
	DataPlot.append("CH2_SINGLE_GainSet")
	DataPlot.append("TotalJitter")
	DataPlot.append("RF_EyeHeight")
	DataPlot.append("RF_GainSet")
	DataHash={}

	Status_Write("User Selected FileName: %s"%fileName)
	Output_Print("User Selected FileName: %s"%fileName)
	if ('.csv' in fileName):
		regex_var=re.search(r'(^.*\\)(.*)\.csv',fileName)
		Path_Name=regex_var.group(1)
		Folder_Name=regex_var.group(2)
		Status_Write("Path Specified is: %s"%Path_Name)
		Output_Print("Path Specified is: %s"%Path_Name)
		Status_Write("Folder Specified is: %s"%Folder_Name)
		Output_Print("Folder Specified is: %s"%Folder_Name)
	else:
		Status_Write("Please specify *.csv File")
		Output_Print("Please specify *.csv File")
		Plot_Data()
	
	ReadCSV=open(fileName,"rt")
	numlines=len(ReadCSV.readlines())
	ReadCSV.close()
	if (numlines<=2):
		Status_Write("Plotting can only be done in data sets greater than one point")
		Output_Print("Plotting can only be done in data sets greater than one point")
		return False
	ReadCSV=open(fileName,"rt")
	csv_reader=csv.reader(ReadCSV)
	
	Dimension=0
	Dimension_0=0 ##XAxis
	Dimension_1=1 ##YAxis
	Dimension_2=2 ##ZAxis
	axis_x="x_axis"
	axis_y="y_axis"
	for row in csv_reader:
		Line= ','.join(row)
		if "XAxis" in row[0] or "XAxis" in row[1] or "XAxis" in row[2] or "YAxis" in row[0] or "YAxis" in row[1] or "ZAxis" in row[0] or "ZAxis" in row[1]:
			axis_x=row[0]
			axis_y=row[1]
			#print "Header Line Found" 
			if "XAxis" in Line and "YAxis" in Line and "ZAxis" in Line:
				Dimension=3
				Status_Write("Found 3-D Plot")
				Output_Print("Found 3-D Plot")
			elif ("XAxis" in Line and "YAxis" in Line) or ("XAxis" in Line and "ZAxis" in Line) or ("YAxis" in Line and "ZAxis" in Line):
				Dimension=2
				Status_Write("Found 2-D Plot")
				Output_Print("Found 2-D Plot")
			else:
				Status_Write("No Valid 2-D or 3-D Data Set is Specified")
				Output_Print("No Valid 2-D or 3-D Data Set is Specified")
				sys.exit(1)

			for content_csv in range (0,len(row)):
				if row[content_csv] in DataPlot:
					if not content_csv in DataHash.keys():
						DataHash[content_csv]={}
						DataHash[content_csv]["Name"]=row[content_csv]
						DataHash[content_csv]["File"]={}
		elif (Dimension==2 or Dimension==3):
			for InfoKey in DataHash.keys():
				if(Dimension==3):
					ArrayFile=row[2].split('(')
					row[Dimension_2]=ArrayFile[0]
					ArrayX=row[Dimension_0].split('(')
					row[Dimension_0]=ArrayX[0]
					ArrayY=row[Dimension_1].split('(')
					row[Dimension_1]=ArrayY[0]
					if not row[Dimension_2] in DataHash[InfoKey]["File"]:
						DataHash[InfoKey]["File"][row[Dimension_2]]={}
					Yrow=float("{0:.2f}".format(float(row[Dimension_1])))
					if not Yrow in DataHash[InfoKey]["File"][row[Dimension_2]]:
						DataHash[InfoKey]["File"][row[Dimension_2]][Yrow]={}
					Xrow=float("{0:.2f}".format(float(row[Dimension_0])))
					if not Xrow in DataHash[InfoKey]["File"][row[Dimension_2]][Yrow]:
						DataHash[InfoKey]["File"][row[Dimension_2]][Yrow][Xrow]={}
					if "0x" in row[InfoKey]:
						row[InfoKey]=int(row[InfoKey], 16)
					DataHash[InfoKey]["File"][row[Dimension_2]][Yrow][Xrow]=row[InfoKey]					
				elif(Dimension==2):
					ArrayX=row[Dimension_0].split('(')
					row[Dimension_0]=ArrayX[0]
					ArrayY=row[Dimension_1].split('(')
					row[Dimension_1]=ArrayY[0]
					if not 0 in DataHash[InfoKey]["File"]:
						DataHash[InfoKey]["File"][0]={}
					Yrow=float("{0:.2f}".format(float(row[Dimension_1])))
					if not Yrow in DataHash[InfoKey]["File"][0]:
						DataHash[InfoKey]["File"][0][Yrow]={}
					Xrow=float("{0:.2f}".format(float(row[Dimension_0])))
					if not Xrow in DataHash[InfoKey]["File"][0][Yrow]:
						DataHash[InfoKey]["File"][0][Yrow][Xrow]={}
					if "0x" in row[InfoKey]:
						row[InfoKey]=int(row[InfoKey], 16)
					DataHash[InfoKey]["File"][0][Yrow][Xrow]=row[InfoKey]
		else:
			return False;
	if os.path.exists(Path_Name):
		if not os.path.exists(Path_Name+'\\'+Folder_Name):
			os.mkdir(Path_Name+'\\'+Folder_Name)
	ReadCSV.close()					

	for ReqItems in DataHash.keys():
		for EachFile in DataHash[ReqItems]["File"].keys():
			FileName=DataHash[ReqItems]["Name"]+"_"+str(EachFile)
			Status_Write("Plotting Data For %s"%FileName)
			Output_Print("Plotting Data For %s"%FileName)
			Labels=[]
			Figure=plt.figure(figsize=(8,6))
			ax=plt.axes()
			ax.set_xlabel(axis_x)
			ax.set_ylabel(axis_y)
			xlist=[]
			ylist=[]
			datalist=[]
			xcount=0
			MinVal=999
			MaxVal=0
			TotalValue=0
			TotalCount=0
			for YVal in sorted(DataHash[ReqItems]["File"][EachFile].keys()):
				if not YVal in ylist:
					ylist.append(YVal)
				singleList=[]
				for XVal in sorted(DataHash[ReqItems]["File"][EachFile][YVal].keys()):
					if not XVal in xlist:
						xlist.append(XVal)
					singleList.append(DataHash[ReqItems]["File"][EachFile][YVal][XVal])
					
					if int(float(DataHash[ReqItems]["File"][EachFile][YVal][XVal]))<MinVal and int(float(DataHash[ReqItems]["File"][EachFile][YVal][XVal]))!=-1:
						MinVal=int(float(DataHash[ReqItems]["File"][EachFile][YVal][XVal]))
					if int(float(DataHash[ReqItems]["File"][EachFile][YVal][XVal]))>MaxVal and int(float(DataHash[ReqItems]["File"][EachFile][YVal][XVal]))!=-1:
						MaxVal=int(float(DataHash[ReqItems]["File"][EachFile][YVal][XVal]))
					if not int(float(DataHash[ReqItems]["File"][EachFile][YVal][XVal]))==-1:  
						TotalValue=TotalValue+int(float(DataHash[ReqItems]["File"][EachFile][YVal][XVal]))        
						TotalCount=TotalCount+1
				datalist.append(singleList)
				
			
			YNumpy=np.array(ylist)
			XNumpy=np.array(xlist)
			if TotalCount!=0:
				Average=TotalValue/TotalCount
			else:
				Average=-1
			DataNumpy=np.array(datalist)
			Title=DataHash[ReqItems]["Name"]+"_at_"+str(EachFile)
			if "GainSet" in DataHash[ReqItems]["Name"]:
				if "GAINSET_PLOT" in PlotDataHash.keys():
					PlotStartValue=PlotDataHash["GAINSET_PLOT"]["StartValue"]
					PlotEndValue=PlotDataHash["GAINSET_PLOT"]["EndValue"]
					NumberofIntervals=(int)(((PlotEndValue-PlotStartValue)/8)+1)
					levels=np.linspace(PlotStartValue,PlotEndValue,NumberofIntervals,endpoint=True)
				else:
					levels=np.linspace(0,128,17,endpoint=True)
				Cntr=plt.contourf(XNumpy,YNumpy,DataNumpy,levels,cmap=plt.cm.jet)
			elif "EyeHeight" in DataHash[ReqItems]["Name"]:
				if "EYEHEIGHT_PLOT" in PlotDataHash.keys():
					PlotStartValue=PlotDataHash["EYEHEIGHT_PLOT"]["StartValue"]
					PlotEndValue=PlotDataHash["EYEHEIGHT_PLOT"]["EndValue"]
					NumberofIntervals=(int)(((PlotEndValue-PlotStartValue)/4)+1)
					levels=np.linspace(PlotStartValue,PlotEndValue,NumberofIntervals,endpoint=True)
				else:
					levels=np.linspace(0,36,10,endpoint=True)
				Cntr=plt.contourf(XNumpy,YNumpy,DataNumpy,levels,cmap=plt.cm.RdYlGn)
			else:
				if "JITTER_PLOT" in PlotDataHash.keys():
					PlotStartValue=PlotDataHash["JITTER_PLOT"]["StartValue"]
					PlotEndValue=PlotDataHash["JITTER_PLOT"]["EndValue"]
					NumberofIntervals=(int)(((PlotEndValue-PlotStartValue)/5)+1)
					levels=np.linspace(PlotStartValue,PlotEndValue,NumberofIntervals,endpoint=True)
				else:
					levels=np.linspace(20,80,19,endpoint=True)
				Cntr=plt.contourf(XNumpy,YNumpy,DataNumpy,levels,cmap=plt.cm.jet)
			SubTitle="Min= "+str(MinVal)+" Max= "+str(MaxVal)+ " Avg= "+str(Average)
			Figure.colorbar(Cntr,ticks=levels)
			Title=FileName+"\n"+SubTitle
			plt.title(Title,fontsize="14",loc='left',fontweight='bold')
			ImageFile=Path_Name+"\\"+Folder_Name+"\\"+FileName+".jpeg"
			Figure.savefig(ImageFile)
			
			plt.close()
			
def InitializeBoard():
	TempFile_Exists='Board_X' in locals() or 'Board_X' in globals()
	for TEST_BOARD in BoardConfigHash.keys():
		out_temp_file_exists='out_temp_file' in locals() or 'out_temp_file' in globals()
		if BoardConfigHash[TEST_BOARD]["Type"]=="SLTBoard":
			Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
			if not Board_X_exists:
				global Board_X
				
				Board_X=Register(TEST_BOARD,BoardConfigHash[TEST_BOARD]["Comport"])
				Board_X.OpenPort()
				#Board_X.softReset("L1")
				#Board_X.softReset("L2")
				Output_Print("Board Name is: "+TEST_BOARD)
				Output_Print("Comport Connected is: "+BoardConfigHash[TEST_BOARD]["Comport"])
				ReadAllString=Board_X.ReadAll()
				print ReadAllString
				if(out_temp_file_exists):
					OUT_TEMP_FILE=open(out_temp_file,"a")
					OUT_TEMP_FILE.write("\n\n***************************************\n")
					OUT_TEMP_FILE.write("Board Name is: "+TEST_BOARD+"\n")
					OUT_TEMP_FILE.write("Comport Connected is: "+BoardConfigHash[TEST_BOARD]["Comport"]+"\n")
					OUT_TEMP_FILE.write(ReadAllString)
					OUT_TEMP_FILE.write("\n***************************************\n\n")
					OUT_TEMP_FILE.close()
				continue
			Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
			if not Board_Y_exists:
				global Board_Y
				
				Board_Y=Register(TEST_BOARD,BoardConfigHash[TEST_BOARD]["Comport"])
				Board_Y.OpenPort()
				#Board_Y.softReset("L1")
				#Board_Y.softReset("L2")
				Output_Print("Board Name is: Board_Y:"+TEST_BOARD)
				Output_Print("Comport Connected is: "+BoardConfigHash[TEST_BOARD]["Comport"])
				ReadAllString=Board_Y.ReadAll()
				print ReadAllString
				if(out_temp_file_exists):
					OUT_TEMP_FILE=open(out_temp_file,"a")
					OUT_TEMP_FILE.write("\n\n***************************************\n")
					OUT_TEMP_FILE.write("Board Name is: "+TEST_BOARD+"\n")
					OUT_TEMP_FILE.write("Comport Connected is: "+BoardConfigHash[TEST_BOARD]["Comport"]+"\n")
					OUT_TEMP_FILE.write(ReadAllString)
					OUT_TEMP_FILE.write("\n***************************************\n\n")
					OUT_TEMP_FILE.close()
				continue
		if BoardConfigHash[TEST_BOARD]["Type"]=="HIDBoard":
			Board_exists = 'Board' in locals() or 'Board' in globals()		   
			if not Board_exists:
				global Board
				Board=HIDControl(TEST_BOARD)
				continue
def ReadPassAccu():
	A1 = "L1"
	A2 = "L2"

	#Reset Error Accumlators To Clear Possible Intial Errors
	Output_Print("Reseting Accumulators...")
	Board_X.Reset_PassAccu(A1)
	Board_Y.Reset_PassAccu(A2)
	Board_Y.Reset_PassAccu(A1)
	Board_X.Reset_PassAccu(A2)
	Output_Print("Accumulators Reset")
	
	if Board_Y.Read_PassAccu(A1):
		TX1PassAccu = 1
	else:
		TX1PassAccu = 0

	if Board_X.Read_PassAccu(A2):
		RX1PassAccu = 1
	else:
		RX1PassAccu = 0

	if Board_X.Read_PassAccu(A1):
		TX2PassAccu = 1
	else:
		TX2PassAccu = 0

	if Board_Y.Read_PassAccu(A2):
		RX2PassAccu = 1
	else:
		RX2PassAccu = 0

	Output_Print("TX1 PassAccu:" + str(TX1PassAccu) + " CalComplete:" + str(Board_Y.Read_CalComplete(A1)) )	
	Output_Print("RX1 PassAccu:" + str(RX1PassAccu) + " CalComplete:" + str(Board_X.Read_CalComplete(A2)) )	
	Output_Print("TX2 PassAccu:" + str(TX2PassAccu) + " CalComplete:" + str(Board_X.Read_CalComplete(A1)) )	
	Output_Print("RX2 PassAccu:" + str(RX2PassAccu) + " CalComplete:" + str(Board_Y.Read_CalComplete(A2)) )	
						
def checkRetimer(lane,runTime = ""):
	#Chip designation for DEBUG
	A1 = "L1"
	A2 = "L2"
	
	if runTime != "":
		runTimeInt = int(runTime)

	if lane == 1:
		#Check RX1 Retimer Status
		#reset internal error accumulator
		if Board_X.Read_PassAccu(A2) == False: 
			Output_Print("Reseting Accumulator...")
			Board_X.Reset_PassAccu(A2)
			Output_Print("Accumulator Reset")

		#check for intial error, reload retimer script and check again for calibration error
		if Board_X.Read_PassAccu(A2) == False: 
			Output_Print("Error Occured")
			Output_Print("Soft Resting OLCs...")
			Board_Y.softReset(A2)
			Board_X.softReset(A2)
			Output_Print("Soft Reset Complete")
			Output_Print("Reloading Default Registers...")
			SetDefaultRegister()
			SetRXReTimer()
			Output_Print("Default Registers Loaded")
					
		lock = Board_X.Read_LockDetect
		if runTime != "" and runTimeInt != 0:
			Output_Print("Accumulating BER...")
			for i in range(0,(runTimeInt*60)+1): 
				sleep(1)
			
			if Board_X.Read_PassAccu(A2):
				Output_Print("\tBER 1E12 Completed")
				result = "PASS"
				return result 
				#elif not Board_X.Read_PassAccu(A2) or lock != Board_X.Read_LockDetect() or not Board_X.Read_CalComplete():
			elif not Board_X.Read_PassAccu(A2):
				Output_Print("\tBER 1E12 Failed")
				result = "Fail"
				return result
				#elif ((runTimeInt*60-i)%60) == 0:
					#Output_Print("\t" + str( ((runTimeInt*60)-i)/60 ) + " Min Left...")
		else:
			Output_Print("Checking Retimer...")
			if Board_X.Read_PassAccu(A2):
				Output_Print("No BER")
				result = "PASS"
			else: 
				Output_Print("BER Detected")
				result = "FAIL"
			return result 
	
	#Check Channel 2 RX Retimer
	elif lane == 2:
		if Board_Y.Read_PassAccu(A2) == False: 
			Output_Print("Reseting Accumulator...")
			Board_Y.Reset_PassAccu(A2)
			Output_Print("Accumulator Reset")
		
		if Board_Y.Read_PassAccu(A2) == False: 
			Output_Print("Error Occured")
			Output_Print("Soft Resting OLCs...")
			Board_Y.softReset(A2)
			Board_X.softReset(A2)
			Output_Print("Soft Reset Complete")
			Output_Print("Reloading Default Registers...")
			SetDefaultRegister()
			SetRXReTimer()
			Output_Print("Default Registers Loaded")
		
		if runTime != "" and runTimeInt != 0:
			Output_Print("Accumulating BER...")
			for i in range(0,(runTimeInt*60)+1):
				sleep(1) 
				#print Board_X.Read_PassAccu(A2)
				#sleep(0.5)
			if Board_Y.Read_PassAccu(A2):
				Output_Print("\tBER 1E12 Completed")
				result = "PASS"
				return result 
			elif not Board_Y.Read_PassAccu(A2):
				Output_Print("\tBER 1E12 Failed")
				result = "Fail"
				return result
			#elif ( (runTimeInt*60-i) % 60 ) == 0:
				#Output_Print("\t" + str( (runTimeInt*60-i)/60) +" Min Left...")
		else:
			Output_Print("Checking Retimer...")
			if Board_Y.Read_PassAccu(A2):
				result = "PASS"
				Output_Print("No BER")
			else: 
				result = "FAIL"
				Output_Print("BER Detected")
			return result 

def checkTXRetimer(lane,runTime = ""):
	#Chip designation for DEBUG
	A1 = "L1"
	A2 = "L2"
	
	if runTime != "":
		runTimeInt = int(runTime)

	if lane == 1:
		#Check RX1 Retimer Status
		#reset internal error accumulator
		if Board_Y.Read_PassAccu(A1) == False: 
			Output_Print("Reseting Accumulator...")
			Board_Y.Reset_PassAccu(A1)
			Output_Print("Accumulator Reset")

		#check for intial error, reload retimer script and check again for calibration error
		if Board_Y.Read_PassAccu(A1) == False: 
			Output_Print("Error Occured")
			Output_Print("Soft Resting OLCs...")
			Board_Y.softReset(A1)
			Board_X.softReset(A1)
			Output_Print("Soft Reset Complete")
			Output_Print("Reloading Default Registers...")
			SetDefaultRegister()
			SetTXReTimer()
			Output_Print("Default Registers Loaded")
					
		if runTime != "" and runTimeInt != 0:
			Output_Print("Accumulating BER...")
			for i in range(0,(runTimeInt*60)+1): 
				sleep(1)
			
			if Board_Y.Read_PassAccu(A1):
				Output_Print("\tBER 1E12 Completed")
				result = "PASS"
				return result 
				#elif not Board_X.Read_PassAccu(A2) or lock != Board_X.Read_LockDetect() or not Board_X.Read_CalComplete():
			elif not Board_Y.Read_PassAccu(A1):
				Output_Print("\tBER 1E12 Failed")
				result = "Fail"
				return result
				#elif ((runTimeInt*60-i)%60) == 0:
					#Output_Print("\t" + str( ((runTimeInt*60)-i)/60 ) + " Min Left...")
		else:
			Output_Print("Checking Retimer...")
			if Board_Y.Read_PassAccu(A1):
				Output_Print("No BER")
				result = "PASS"
			else: 
				Output_Print("BER Detected")
				result = "FAIL"
			return result 
	
	#Check Channel 2 RX Retimer
	elif lane == 2:
		if Board_X.Read_PassAccu(A1) == False: 
			Output_Print("Reseting Accumulator...")
			Board_X.Reset_PassAccu(A1)
			Output_Print("Accumulator Reset")
		
		if Board_X.Read_PassAccu(A1) == False: 
			Output_Print("Error Occured")
			Output_Print("Soft Resting OLCs...")
			Board_Y.softReset(A1)
			Board_X.softReset(A1)
			Output_Print("Soft Reset Complete")
			Output_Print("Reloading Default Registers...")
			SetDefaultRegister()
			SetTXReTimer()
			Output_Print("Default Registers Loaded")
		
		if runTime != "" and runTimeInt != 0:
			Output_Print("Accumulating BER...")
			for i in range(0,(runTimeInt*60)+1):
				sleep(1) 
				#print Board_X.Read_PassAccu(A2)
				#sleep(0.5)
			if Board_X.Read_PassAccu(A1):
				Output_Print("\tBER 1E12 Completed")
				result = "PASS"
				return result 
			elif not Board_X.Read_PassAccu(A1):
				Output_Print("\tBER 1E12 Failed")
				result = "Fail"
				return result
			#elif ( (runTimeInt*60-i) % 60 ) == 0:
				#Output_Print("\t" + str( (runTimeInt*60-i)/60) +" Min Left...")
		else:
			Output_Print("Checking Retimer...")
			if Board_X.Read_PassAccu(A1):
				result = "PASS"
				Output_Print("No BER")
			else: 
				result = "FAIL"
				Output_Print("BER Detected")
			return result

def checkTXRXRetimer(lane,runTime = ""):
	#Chip designation for DEBUG
	A1 = "L1"
	A2 = "L2"
	
	if runTime != "":
		runTimeInt = int(runTime)

	if lane == 1:
		#Check RX1 Retimer Status
		#reset internal error accumulator
		if Board_Y.Read_PassAccu(A1) == False: 
			Output_Print("Reseting Accumulator...")
			Board_Y.Reset_PassAccu(A1)
			Output_Print("Accumulator Reset")

		if Board_X.Read_PassAccu(A2) == False: 
			Output_Print("Reseting Accumulator...")
			Board_X.Reset_PassAccu(A2)
			Output_Print("Accumulator Reset")

		#check for intial error, reload retimer script and check again for calibration error
		if Board_Y.Read_PassAccu(A1) == False or Board_X.Read_PassAccu(A2) == False: 
			Output_Print("Error Occured")
			Output_Print("Soft Resting OLCs...")
			Board_Y.softReset(A1)
			Board_X.softReset(A2)
			Output_Print("Soft Reset Complete")
			Output_Print("Reloading Default Registers...")
			SetDefaultRegister()
			SetTXReTimer()
			sleep(5)
			SetRXReTimer()
			Output_Print("Default Registers Loaded")
						
		if runTime != "" and runTimeInt != 0:
			Output_Print("Accumulating BER...")
			for i in range(0,(runTimeInt*60)+1): 
				sleep(1)
			
			if Board_Y.Read_PassAccu(A1):
				Output_Print("\tBER 1E12 Completed")
				TXresult = "PASS"
				
			elif not Board_Y.Read_PassAccu(A1):
				Output_Print("\tBER 1E12 Failed")
				TXresult = "Fail"
				
			if Board_X.Read_PassAccu(A2):
				Output_Print("\tBER 1E12 Completed")
				RXresult = "PASS"
				
			elif not Board_X.Read_PassAccu(A2):
				Output_Print("\tBER 1E12 Failed")
				RXresult = "Fail"

			return TXresult, RXresult
		else:
			Output_Print("Checking Retimer...")
			if Board_Y.Read_PassAccu(A1):
				Output_Print("No BER")
				TXresult = "PASS"
			else: 
				Output_Print("BER Detected")
				TXresult = "FAIL"
			
			if Board_X.Read_PassAccu(A2):
				Output_Print("No BER")
				RXresult = "PASS"
			else: 
				Output_Print("BER Detected")
				RXresult = "FAIL"
			return TXresult, RXresult
			
	
	#Check Channel 2 RX Retimer
	elif lane == 2:
		if Board_X.Read_PassAccu(A1) == False: 
			Output_Print("Reseting Accumulator...")
			Board_X.Reset_PassAccu(A1)
			Board_Y.Reset_PassAccu(A2)
			Output_Print("Accumulator Reset")
		
		if Board_X.Read_PassAccu(A1) == False or Board_Y.Read_PassAccu(A2) == False: 
			Output_Print("Error Occured")
			Output_Print("Soft Resting OLCs...")
			Board_Y.softReset(A1)
			Board_X.softReset(A1)
			Output_Print("Soft Reset Complete")
			Output_Print("Reloading Default Registers...")
			SetDefaultRegister()
			
			SetTXReTimer()
			sleep(5)
			SetRXReTimer()
			
			Output_Print("Default Registers Loaded")
		
		if runTime != "" and runTimeInt != 0:
			Output_Print("Accumulating BER...")
			for i in range(0,(runTimeInt*60)+1):
				sleep(1) 
				
				
			if Board_X.Read_PassAccu(A1):
				Output_Print("\tBER 1E12 Completed")
				TXresult = "PASS"
				
			elif not Board_X.Read_PassAccu(A1):
				Output_Print("\tBER 1E12 Failed")
				TXresult = "Fail"
			if Board_Y.Read_PassAccu(A2):
				Output_Print("\tBER 1E12 Completed")
				RXresult = "PASS"
				
			elif not Board_Y.Read_PassAccu(A2):
				Output_Print("\tBER 1E12 Failed")
				RXresult = "Fail"
			
			return TXresult,RXresult	
		
		else:
			Output_Print("Checking Retimer...")
			if Board_X.Read_PassAccu(A1):
				TXresult = "PASS"
			else: 
				TXresult = "FAIL"

			if Board_Y.Read_PassAccu(A2):
				RXresult = "PASS"
			else: 
				RXresult = "FAIL"
				
			
			return TXresult,RXresult

def Meas_DSA_Jitter(ExecKeys):
	if (ExecutionOrderHash[ExecKeys]["Test"]=="CH1_DUAL"):
		Output_Print("Enabling All Lanes...")
		powerOn()
		Output_Print("All Lanes Enabled")
		SoftReset()
		SetTXReTimer()
		SetDefaultRegister()
		if InputDataHash[0]=="Default":
			MeasureDSAJitter(1)
		else:
			if "D10" in InputDataHash[InputDataKey]["DataType"] or "HBR" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitter(1,OtherValuesHash["DSA_SETUP_FILE_DP_1"])
			elif "CP0" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitter(1,OtherValuesHash["DSA_SETUP_FILE_USB_1"])
			else:
				MeasureDSAJitter(1)
		if OtherValuesHash["CURRENT_DRAWN"]=="True":
			CurrentReading=Korad.GET_OUTPUT_CURRENT()
			Output_Print("Current Drawn is %s"%CurrentReading)
			Status_Write("Current Drawn is %s"%CurrentReading)	
			OUTPUT.write("%s,"%(CurrentReading))
																																															
	elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH1_SINGLE"):
		powerOn()
		SetDefaultRegister()
		EnableLane(1)
		DisableLane(2)
		if InputDataHash[0]=="Default":
			MeasureDSAJitter(1)
		else:
			if "D10" in InputDataHash[InputDataKey]["DataType"] or "HBR" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitter(1,OtherValuesHash["DSA_SETUP_FILE_DP_1"])
			elif "CP0" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitter(1,OtherValuesHash["DSA_SETUP_FILE_USB_1"])
			else:
				MeasureDSAJitter(1)
		if OtherValuesHash["CURRENT_DRAWN"]=="True":
			CurrentReading=Korad.GET_OUTPUT_CURRENT()
			Output_Print("Current Drawn is %s"%CurrentReading)
			Status_Write("Current Drawn is %s"%CurrentReading)	
			OUTPUT.write("%s,"%(CurrentReading))
	elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH2_DUAL"):
		Output_Print("Enabling All Lanes...")
		powerOn()
		Output_Print("All Lanes Enabled")
		
		SoftReset()
		SetDefaultRegister()
		SetTXReTimer()
																									
		if InputDataHash[0]=="Default":
			MeasureDSAJitter(2)
		else:
			if "D10" in InputDataHash[InputDataKey]["DataType"] or "HBR" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitter(2,OtherValuesHash["DSA_SETUP_FILE_DP_2"])
			elif "CP0" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitter(2,OtherValuesHash["DSA_SETUP_FILE_USB_2"])
			else:
				MeasureDSAJitter(2)
		if OtherValuesHash["CURRENT_DRAWN"]=="True":
			CurrentReading=Korad.GET_OUTPUT_CURRENT()
			Output_Print("Current Drawn is %s"%CurrentReading)
			Status_Write("Current Drawn is %s"%CurrentReading)	
			OUTPUT.write("%s,"%(CurrentReading))
																							
	elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH2_SINGLE"):
		powerOn()
		SetDefaultRegister()
		EnableLane(2)
		DisableLane(1)
		if InputDataHash[0]=="Default":
			MeasureDSAJitter(2)
		else:
			if "D10" in InputDataHash[InputDataKey]["DataType"] or "HBR" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitter(2,OtherValuesHash["DSA_SETUP_FILE_DP_2"])
			elif "CP0" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitter(2,OtherValuesHash["DSA_SETUP_FILE_USB_2"])
			else:
				MeasureDSAJitter(2)
		if OtherValuesHash["CURRENT_DRAWN"]=="True":
			CurrentReading=Korad.GET_OUTPUT_CURRENT()
			Output_Print("Current Drawn is %s"%CurrentReading)
			Status_Write("Current Drawn is %s"%CurrentReading)	
			OUTPUT.write("%s,"%(CurrentReading))

def Meas_DSA_JitterReTimerOn(ExecKeys):
	if (ExecutionOrderHash[ExecKeys]["Test"]=="CH1_DUAL"):
		powerOn()
		SetDefaultRegister()
		#SetRXReTimer()
		if InputDataHash[0]=="Default":
			MeasureDSAJitterReTimerON(1)
		else:
			if "D10" in InputDataHash[InputDataKey]["DataType"] or "HBR" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitterReTimerON(1,OtherValuesHash["DSA_SETUP_FILE_DP_1"])
			elif "CP0" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitterReTimerON(1,OtherValuesHash["DSA_SETUP_FILE_USB_1"])
			else:
				MeasureDSAJitterReTimerON(1)
		if OtherValuesHash["CURRENT_DRAWN"]=="True":
			CurrentReading=Korad.GET_OUTPUT_CURRENT()
			Output_Print("Current Drawn is %s"%CurrentReading)
			Status_Write("Current Drawn is %s"%CurrentReading)	
			OUTPUT.write("%s,"%(CurrentReading))
																																															
	elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH1_SINGLE"):
		powerOn()
		DisableLane(2)
		EnableLane(1)
		if InputDataHash[0]=="Default":
			MeasureDSAJitterReTimerON(1)
		else:
			if "D10" in InputDataHash[InputDataKey]["DataType"] or "HBR" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitterReTimerON(1,OtherValuesHash["DSA_SETUP_FILE_DP_1"])
			elif "CP0" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitterReTimerON(1,OtherValuesHash["DSA_SETUP_FILE_USB_1"])
			else:
				MeasureDSAJitterReTimerON(1)
		if OtherValuesHash["CURRENT_DRAWN"]=="True":
			CurrentReading=Korad.GET_OUTPUT_CURRENT()
			Output_Print("Current Drawn is %s"%CurrentReading)
			Status_Write("Current Drawn is %s"%CurrentReading)	
			OUTPUT.write("%s,"%(CurrentReading))
	elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH2_DUAL"):
		powerOn()
		SetDefaultRegister()
		#SetRXReTimer()
																									
		if InputDataHash[0]=="Default":
			MeasureDSAJitterReTimerON(2)
		else:
			if "D10" in InputDataHash[InputDataKey]["DataType"] or "HBR" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitterReTimerON(2,OtherValuesHash["DSA_SETUP_FILE_DP_2"])
			elif "CP0" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitterReTimerON(2,OtherValuesHash["DSA_SETUP_FILE_USB_2"])
			else:
				MeasureDSAJitterReTimerON(2)
		if OtherValuesHash["CURRENT_DRAWN"]=="True":
			CurrentReading=Korad.GET_OUTPUT_CURRENT()
			Output_Print("Current Drawn is %s"%CurrentReading)
			Status_Write("Current Drawn is %s"%CurrentReading)	
			OUTPUT.write("%s,"%(CurrentReading))
																							
	elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH2_SINGLE"):
		Output_Print("Enabling All Lanes...")
		powerOn()
		Output_Print("All Lanes Enabled")

		DisableLane(1)
		EnableLane(2)

		if InputDataHash[0]=="Default":
			MeasureDSAJitterReTimerON(2)
		else:
			if "D10" in InputDataHash[InputDataKey]["DataType"] or "HBR" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitterReTimerON(2,OtherValuesHash["DSA_SETUP_FILE_DP_2"])
			elif "CP0" in InputDataHash[InputDataKey]["DataType"]:
				MeasureDSAJitterReTimerON(2,OtherValuesHash["DSA_SETUP_FILE_USB_2"])
			else:
				MeasureDSAJitterReTimerON(2)
		if OtherValuesHash["CURRENT_DRAWN"]=="True":
			CurrentReading=Korad.GET_OUTPUT_CURRENT()
			Output_Print("Current Drawn is %s"%CurrentReading)
			Status_Write("Current Drawn is %s"%CurrentReading)	
			OUTPUT.write("%s,"%(CurrentReading))
def powerOn():
	Board_X.PDN_ON()
	Board_Y.PDN_ON()
################################################################################
##Main Routine
################################################################################
def main(argv):
	global Points
	MeasurementCount=1
	CurrentDate=strftime("%d%m%y_%HH_%MM")
	TodayDate=strftime("%m%d%y")
	INPUT_FILE="Input.txt"
	OUT_FILE_NAME="OutputFile_"+CurrentDate+".csv"
	BigPrint=Figlet(font=u'6x10')
	print BigPrint.renderText("Analysis")
	MacAddress= ':'.join(re.findall('..', '%012x' % uuid.getnode()))
	HostName=socket.gethostname()
	IPAddress=socket.gethostbyname(socket.gethostname())

	global STATUS
	global StatusFile
	StatusFile=".tempStatus"
	STATUS=open(StatusFile,"wb")
	STATUS.write("___________Automation Program Status::%.2f___________"%Version)
	Status_Write("Status File Successfully Created")
	Status_Write("MacAddress is %s"%MacAddress)
	Status_Write("HostName is %s"%HostName)
	Status_Write("IPAddress is %s"%IPAddress)
	try:
		opts,args=getopt.getopt(sys.argv[1:],'i:o:n:r:vpas:',['ifile=','ofile='])
	except getopt.GetoptError:
		print "\nTo Specify input and output file explicitly"
		print "\tpython AnalysisProgram.py -i <inputfile> -o <outputfile>"
		
		print "\nTo Specify Fixed Output File Name"
		print "\tpython AnalysisProgram.py -n <FileAcronym>"
		
		print "\nTo Perform Plotting on Previously Taken Data"
		print "\tpython AnalysisProgram.py -p"

		print "\nEnable All Lanes on the Board to TX/RX"
		print "\tpython AnalysisProgram.py -a"
		print "Enable Lane 1 on the Board to TX/RX"
		print "\tpython AnalysisProgram.py -s 1"
		print "Enable Lane 2 on the Board to TX/RX"
		print "\tpython AnalysisProgram.py -s 2"
		print "Soft Reset All Lanes"
		print "\tpython AnalysisProgram.py -a reset"

		print "\nEnable TX/RX ReTimer"
		print "\tpython AnalysisProgram.py -r a"
		print "Enable TX ReTimer"
		print "\tpython AnalysisProgram.py -r tx"
		print "Enable RX ReTimer"
		print "\tpython AnalysisProgram.py -r rx"
		print "Read All ReTimer Accumulators"
		print "\tpython AnalysisProgram.py -r rd"

		
		sys.exit()


	for opt,arg in opts:
		if opt in ("-i","--ifile"):
			INPUT_FILE=arg
			Status_Write("Option Selected with -i %s"%INPUT_FILE)
		elif opt in ("-o","--ofile"):
			OUT_FILE_NAME=arg
			Status_Write("Option Selected with -o %s"%OUT_FILE_NAME)
		elif opt=="-n":
			FileAcronym=arg
			OUT_FILE_NAME=FileAcronym+".csv"
			Status_Write("Option Selected with -n %s"%FileAcronym)
			Output_Print("FileAcronym is %s"%FileAcronym)
		elif opt=="-v":
			print "AnalysisProgram Version: %.2f"%Version
			sys.exit()
		elif opt =="-p":
			ReadInputFile(INPUT_FILE)
			print BigPrint.renderText("Plot Data")
			Plot_Data()
			print BigPrint.renderText("Complete")
			sys.exit()
		elif opt =="-a":
			ReadInputFile(INPUT_FILE)
			Output_Print("Reading Input File Complete")
			SetupOtherValues()
			Output_Print("Reading Other Values/Variables Complete")
			SetupBoardConfig()
			Output_Print("Reading BoardConfig Complete")
			InitializeBoard()
			Output_Print("Initialization of Boards Complete")
			
			SoftReset()
			SetDefaultRegister()
			
			if arg == "reset":
				Output_Print("Soft Resetting Boards")
				SoftReset()
				Output_Print("Soft Reset Complete")
				sys.exit()

			SetupTXRX()
			Output_Print("Reading Default Transmitter/Receiver Complete")
			SetDefaultRegister()
			Output_Print("Set Default Register Complete")
			print BigPrint.renderText("TX/RX")
			sys.exit()

		elif opt =="-r":
			ReadInputFile(INPUT_FILE)
			Output_Print("Reading Input File Complete")
			SetupOtherValues()
			Output_Print("Reading Other Values/Variables Complete")
			SetupBoardConfig()
			Output_Print("Reading BoardConfig Complete")
			InitializeBoard()
			Output_Print("Initialization of Boards Complete")
			
			if arg == "rd":
				Output_Print("Reading Pass Accu...")
				ReadPassAccu()
				sys.exit()

			Output_Print("Reading Default Transmitter/Receiver...")
			SetupTXRX()
			Output_Print("Reading Default Transmitter/Receiver Complete")
			
			Output_Print("Setting Default Registers...")
			SetDefaultRegister()
			Output_Print("Set Default Registers Complete")

			Output_Print("Reading ReTimer Script...")
			SetupReTimer()
			Output_Print("Reading ReTimer Script Complete")

			if arg == "s1":
				powerOn()
				Output_Print("PDN Off")
				Output_Print("Soft Resetting...")
				SoftReset()		
				Output_Print("Soft Reset Complete")
				SetRXReTimer()		
				EnableLane(1)
				DisableLane(2)
				sys.exit()

			if arg == "s2":
				powerOn()
				Output_Print("PDN Off")				
				Output_Print("Soft Resetting...")
				SoftReset()	
				Output_Print("Soft Reset Complete")		
				SetRXReTimer()
				EnableLane(2)
				DisableLane(1)
				sys.exit()

			if arg == "a":
				Output_Print("Enabling TX ReTimer...")
				SetTXReTimer()
				Output_Print("TX ReTimer On")
				Output_Print("Enabling RX ReTimer...")
				SetRXReTimer()
				Output_Print("RX ReTimer On")
				print BigPrint.renderText("TX/RX RETIMER")

			elif arg == "tx":
				Output_Print("Enabling TX ReTimer...")
				SetTXReTimer()
				print BigPrint.renderText("TX RETIMER")

			elif arg == "rx":
				Output_Print("Enabling RX ReTimer...")
				SetRXReTimer()
				print BigPrint.renderText("RX RETIMER")
			sys.exit()
					
		elif opt =="-s":
			Lane_Option=arg
			ReadInputFile(INPUT_FILE)
			Output_Print("Reading Input File Complete")
			SetupOtherValues()
			Output_Print("Reading Other Values/Variables Complete")
			SetupBoardConfig()
			Output_Print("Reading BoardConfig Complete")
			InitializeBoard()
			Output_Print("Initialization of Boards Complete")
			SetupTXRX()
			SetupReTimer()
			Output_Print("Reading Default Transmitter/Receiver Complete")
			Output_Print("LaneOption is :%s"%Lane_Option)
			if (Lane_Option=="1"):
				powerOn()				
				EnableLane(1)
				DisableLane(2)
			if (Lane_Option=="2"):
				powerOn()
				EnableLane(2)
				DisableLane(1)				
			Output_Print("Set Default Register Complete")
			print BigPrint.renderText("TX/RX")
			sys.exit()

	###Case Conditions for Multiple Execution Conditions Complete
			
				
	ReadInputFile(INPUT_FILE)
	Output_Print("Reading Input File Complete")
	Status_Write("Reading Input_File Successful")
	
	SetupOtherValues()
	Output_Print("Reading Other Values/Variables Complete")
	Status_Write("Reading Other Values/Variables Complete")


		
	SetupTXRX()
	Output_Print("Reading Default Transmitter/Receiver Complete")
	Status_Write("Reading Default Transmitter/Receiver Complete")

	if "DATA_OUTPUT_DIRECTORY" in OtherValuesHash.keys():
		FolderName=OtherValuesHash["DATA_OUTPUT_DIRECTORY"]
		if os.path.exists(OtherValuesHash["DATA_OUTPUT_DIRECTORY"]):
			FolderName=OtherValuesHash["DATA_OUTPUT_DIRECTORY"]+"\\"+TodayDate
			if not os.path.exists(FolderName):
				os.mkdir(FolderName)
			OUT_FILE_NAME=FolderName+"\\"+OUT_FILE_NAME
		Output_Print("Creating Output File Complete")
		Status_Write("Creating Output File Complete")
	outfilename,outfile_extension=os.path.splitext(OUT_FILE_NAME)
	global out_temp_file
	out_temp_file=outfilename+".txt"
	os.system("copy %s %s >NULL"%(INPUT_FILE,out_temp_file))
	
	global HEADER_OUTPUT
	HEADER_OUTPUT=open(OUT_FILE_NAME,"wb")

	SetupPreCond()
	Output_Print("Reading PreCondition Values Complete")
	Status_Write("Reading PreCondition Values Complete")
	
	SetupTemperature()
	Output_Print("Reading Temperature Complete")
	Status_Write("Reading Temperature Complete")

	SetupHumidity()
	Output_Print("Reading Humidity Complete")
	Status_Write("Reading Humidity Complete")

	SetupInputData()
	Output_Print("Reading InputData Complete")
	Status_Write("Reading InputData Complete")

	SetupInputLSData()
	Output_Print("Reading InputData Complete")
	Status_Write("Reading InputData Complete")
			
	SetupPowerSupply()	
	Output_Print("Reading PowerSupply Complete")
	Status_Write("Reading PowerSupply Complete")
	
	SetupVDD()
	Output_Print("Reading ONBoard_VDD Complete")
	Status_Write("Reading ONBoard_VDD Complete")

	SetupVDDQ()
	Output_Print("Reading ONBoard_VDDQ Complete")
	Status_Write("Reading ONBoard_VDDQ Complete")

	SetupOPTBench()
	Output_Print("Reading OPTBench Complete")
	Status_Write("Reading OPTBench Complete")

	SetupRegisterSweep()
	Output_Print("Reading RegisterSweep Complete")
	Status_Write("Reading RegisterSweep Complete")

	SetupBoardConfig()
	Output_Print("Reading BoardConfig Complete")
	Status_Write("Reading BoardConfig Complete")


	SetupExecutionOrder()
	Output_Print("Reading Execution Order Complete")
	Status_Write("Reading Execution Order Complete")

	SetupRunTime()
	Output_Print("Reading Run Time Values Complete")
	Status_Write("Reading Run Time Values Complete")

	SetupReTimer()
	Output_Print("Reading ReTimer Script Complete")
	Status_Write("Reading ReTimer Script Complete")



	HEADER_OUTPUT.write("\n")
	HEADER_OUTPUT.close()

	if (DEBUG):
		DebugReadLog()

	for TEST_BOARD in BoardConfigHash.keys():
		out_temp_file_exists='out_temp_file' in locals() or 'out_temp_file' in globals()
		if BoardConfigHash[TEST_BOARD]["Type"]=="SLTBoard":
			Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
			if not Board_X_exists:
				global Board_X
				Board_X=Register(TEST_BOARD,BoardConfigHash[TEST_BOARD]["Comport"])
				Board_X.OpenPort()
				Output_Print("Board Name is: "+TEST_BOARD)
				Output_Print("Comport Connected is: "+BoardConfigHash[TEST_BOARD]["Comport"])
				ReadAllString=Board_X.ReadAll()
				print ReadAllString
				if(out_temp_file_exists):
					OUT_TEMP_FILE=open(out_temp_file,"a")
					OUT_TEMP_FILE.write("\n\n***************************************\n")
					OUT_TEMP_FILE.write("Board Name is: "+TEST_BOARD+"\n")
					OUT_TEMP_FILE.write("Comport Connected is: "+BoardConfigHash[TEST_BOARD]["Comport"]+"\n")
					OUT_TEMP_FILE.write(ReadAllString)
					OUT_TEMP_FILE.write("\n***************************************\n\n")
					OUT_TEMP_FILE.close()
				continue
			Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
			if not Board_Y_exists:
				global Board_Y
				Board_Y=Register(TEST_BOARD,BoardConfigHash[TEST_BOARD]["Comport"])
				Board_Y.OpenPort()
				Output_Print("Board Name is: "+TEST_BOARD)
				Output_Print("Comport Connected is: "+BoardConfigHash[TEST_BOARD]["Comport"])
				ReadAllString=Board_Y.ReadAll()
				print ReadAllString
				if(out_temp_file_exists):
					OUT_TEMP_FILE=open(out_temp_file,"a")
					OUT_TEMP_FILE.write("\n\n***************************************\n")
					OUT_TEMP_FILE.write("Board Name is: "+TEST_BOARD+"\n")
					OUT_TEMP_FILE.write("Comport Connected is: "+BoardConfigHash[TEST_BOARD]["Comport"]+"\n")
					OUT_TEMP_FILE.write(ReadAllString)
					OUT_TEMP_FILE.write("\n***************************************\n\n")
					OUT_TEMP_FILE.close()
				continue
		if BoardConfigHash[TEST_BOARD]["Type"]=="HIDBoard":
			Board_exists = 'Board' in locals() or 'Board' in globals()		   
			if not Board_exists:
				global Board
				Board=HIDControl(TEST_BOARD)
				continue
	
	Output_Print("Initialization of Boards Complete")
	Status_Write("Initialization of Boards Complete")
	
	LoopCount=1
	Points=LoopCount*Points	
	Output_Print("Total Number of Points to be Tested is %d"%Points)
	Status_Write("Total Number of Points to be Tested is %d"%Points)
	
	if (TemperatureHash.has_key(0)):
		Output_Print("Temperature Options Have Been Defined")
		Status_Write("Temperature Options Have Been Defined")
	
	else:
		TemperatureHash[0]="Default"
	
	for TempKey in sorted(TemperatureHash.keys()):
		if not TemperatureHash[TempKey]=="Default":
			SetTemperature(TemperatureHash[TempKey])
			Output_Print("Temperature Successfully set to %s"%TemperatureHash[TempKey])
			Status_Write("Temperature Successfully set to %s"%TemperatureHash[TempKey])


		if (HumidityHash.has_key(0)):
			Output_Print("Humidity Options Have Been Defined")
			Status_Write("Humidity Options Have Been Defined")
		else:
			HumidityHash[0]="Default"

		for HumidKey in sorted(HumidityHash.keys()):
			if not HumidityHash[HumidKey]=="Default":
				SetHumidity(HumidityHash[HumidKey])
				Output_Print("Humidity Successfully set to %s"%HumidityHash[HumidKey])
				Status_Write("Humidity Successfully set to %s"%HumidityHash[HumidKey])

			if InputDataHash.has_key(0):
				Output_Print("InputData Options Have Been Defined")
				Status_Write("InputData Options Have Been Defined")
			else:
				InputDataHash[0]="Default"
			for InputDataKey in sorted(InputDataHash.keys()):
				if not InputDataHash[InputDataKey]=="Default":
					SetData(InputDataHash[InputDataKey]["Type"],InputDataHash[InputDataKey]["DataType"],InputDataHash[InputDataKey]["DataRate"],InputDataHash[InputDataKey]["VoltageLevel"])
					Output_Print("Input Data set to %s,%s,%d,%f"%(InputDataHash[InputDataKey]["Type"],InputDataHash[InputDataKey]["DataType"],InputDataHash[InputDataKey]["DataRate"],InputDataHash[InputDataKey]["VoltageLevel"]))
					Status_Write("Input Data set to %s,%s,%d,%f"%(InputDataHash[InputDataKey]["Type"],InputDataHash[InputDataKey]["DataType"],InputDataHash[InputDataKey]["DataRate"],InputDataHash[InputDataKey]["VoltageLevel"]))
				
				if InputLSDataHash.has_key(0):
					Output_Print("InputLSData Options Have Been Defined")
					Status_Write("InputLSData Options Have Been Defined")
				else:
					InputLSDataHash[0]="Default"
				for InputLSDataKey in sorted(InputLSDataHash.keys()):
					if not InputLSDataHash[InputLSDataKey]=="Default":
						SetLSData(InputLSDataHash[InputLSDataKey]["Type"],InputLSDataHash[InputLSDataKey]["Frequency"],InputLSDataHash[InputLSDataKey]["VoltageLevel"])
						Output_Print("Input LS Data set to %s,%s,%s"%(InputLSDataHash[InputLSDataKey]["Type"],InputLSDataHash[InputLSDataKey]["Frequency"],InputLSDataHash[InputLSDataKey]["VoltageLevel"]))
						Status_Write("Input LS Data set to %s,%s,%s"%(InputLSDataHash[InputLSDataKey]["Type"],InputLSDataHash[InputLSDataKey]["Frequency"],InputLSDataHash[InputLSDataKey]["VoltageLevel"]))
				
					if (PowerSupplyHash.has_key(0)):
						Output_Print("PowerSupply Options Have Been Defined")
						Status_Write("PowerSupply Options Have Been Defined")
					else:
						PowerSupplyHash[0]="Default"
	
					for PSKey in sorted(PowerSupplyHash.keys()):
						if not PowerSupplyHash[PSKey] == "Default":
							SetPowerSupply(PowerSupplyHash[PSKey])
							Output_Print("PowerSupply Successfully set to %s"%PowerSupplyHash[PSKey])
							Status_Write("PowerSupply Successfully set to %s"%PowerSupplyHash[PSKey])

					
						Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
						Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
						for BrdKey in BoardConfigHash.keys():
							if BoardConfigHash[BrdKey]["Type"]=="SLTBoard":
								if Board_X_exists and Board_X.ID==BrdKey:
									Board_X.ClosePort()
									sleep(2)
									Board_X=Register(Board_X.ID,BoardConfigHash[Board_X.ID]["Comport"])
									Board_X.OpenPort()
								if Board_Y_exists and Board_Y.ID==BrdKey:
									Board_Y.ClosePort()
									sleep(2)
									Board_Y=Register(Board_Y.ID,BoardConfigHash[Board_Y.ID]["Comport"])
									Board_Y.OpenPort()
					
						if(VDDHash.has_key(0)):
							Output_Print("ON BOARD VDD Options are Defined")
							Status_Write("ON BOARD VDD Options are Defined")
						else:
							VDDHash[0]="Default"
					
						for VDDKey in sorted(VDDHash.keys()):
							if not VDDHash[VDDKey] == "Default":
								SetOnBoardVDD(VDDHash[VDDKey])
								Output_Print("ON BOARD VDD Successfully set to %s"%VDDHash[VDDKey])
								Status_Write("ON BOARD VDD Successfully set to %s"%VDDHash[VDDKey])

							if(VDDQHash.has_key(0)):
								Output_Print("ON BOARD VDDQ Options are Defined")
								Status_Write("ON BOARD VDDQ Options are Defined")
							else:
								VDDQHash[0]="Default"
						
							for VDDQKey in sorted(VDDQHash.keys()):
								if not VDDQHash[VDDQKey] == "Default":
									SetOnBoardVDDQ(VDDQHash[VDDQKey])
									Output_Print("ON BOARD VDDQ Successfully set to %s"%VDDQHash[VDDQKey])
									Status_Write("ON BOARD VDDQ Successfully set to %s"%VDDQHash[VDDQKey])

								
								XValue=0
								XEndValue=0
								YValue=0
								YEndValue=0
								ZValue=0
								ZEndValue=0
								XRunLoop=True
								YRunLoop=True
								ZRunLoop=True
								if 'XAxis' in OPTBenchHash.keys():
									XMotor=OpticalBench(int(OPTBenchHash['XAxis'][0]),31)
									if OPTBenchStartPos[0] is not None:
										XMotor.SetValue(OPTBenchStartPos[0],MotorSpeed)
										Original_XAxis=OPTBenchStartPos[0]
										Output_Print("XAxis Original Position set to %.2f"%Original_XAxis)
										Status_Write("XAxis Original Position set to %.2f"%Original_XAxis)
										sleep(2)
									else: 
										Original_XAxis=XMotor.GetCurrentPosition()
									Original_XAxis=round(Original_XAxis,2)
									XValue=Original_XAxis+float(OPTBenchHash['XAxis'][1])
									XValue=round(XValue,2)
									XEndValue=Original_XAxis+float(OPTBenchHash['XAxis'][2])
									XEndValue=round(XEndValue,2)
									XStep=float(OPTBenchHash['XAxis'][3])
									XStep=round(XStep,2)
								if 'YAxis' in OPTBenchHash.keys():
									YMotor=OpticalBench(int(OPTBenchHash['YAxis'][0]),31)
									if OPTBenchStartPos[1] is not None:
										YMotor.SetValue(OPTBenchStartPos[1],MotorSpeed)
										Original_YAxis=OPTBenchStartPos[1]
										Output_Print("YAxis Original Position set to %.2f"%Original_YAxis)
										Status_Write("YAxis Original Position set to %.2f"%Original_YAxis)
										sleep(2)
									else:
										Original_YAxis=YMotor.GetCurrentPosition()
									Original_YAxis=round(Original_YAxis,2)
									YValue=Original_YAxis+float(OPTBenchHash['YAxis'][1])
									YValue=round(YValue,2)
									YEndValue=Original_YAxis+float(OPTBenchHash['YAxis'][2])
									YEndValue=round(YEndValue,2)
									YStep=float(OPTBenchHash['YAxis'][3])
									YStep=round(YStep,2)
								if 'ZAxis' in OPTBenchHash.keys():
									ZMotor=OpticalBench(int(OPTBenchHash['ZAxis'][0]),31)
									if OPTBenchStartPos[2] is not None:
										ZMotor.SetValue(OPTBenchStartPos[2],MotorSpeed)
										Original_ZAxis=OPTBenchStartPos[2]
										Output_Print("ZAxis Original Position set to %.2f"%Original_ZAxis)
										Status_Write("ZAxis Original Position set to %.2f"%Original_ZAxis)
										sleep(2)
									else:
										Original_ZAxis=ZMotor.GetCurrentPosition()
									Original_ZAxis=round(Original_ZAxis,2)
									ZValue=Original_ZAxis+float(OPTBenchHash['ZAxis'][1])
									ZValue=round(ZValue,2)
									ZEndValue=Original_ZAxis+float(OPTBenchHash['ZAxis'][2])
									ZEndValue=round(ZEndValue,2)
									ZStep=float(OPTBenchHash['ZAxis'][3])
									ZStep=round(ZStep,2)
								if 'XAxis' in OPTBenchHash.keys():
									XValue=Original_XAxis+float(OPTBenchHash['XAxis'][1])
									XValue=round(XValue,2)
								else:
									XRunLoop=True
								while (XValue<=XEndValue and XRunLoop==True):
									if 'XAxis' in OPTBenchHash.keys():
										XMotor.SetValue(XValue,MotorSpeed)
										Output_Print("XAxis Successfully set to %.2f"%XValue)
										Status_Write("XAxis Successfully set to %.2f"%XValue)
										XValue=XValue+XStep
										XValue=round(XValue,2)
									else:
										XRunLoop=False
									if 'YAxis' in OPTBenchHash.keys():
										YValue=Original_YAxis+float(OPTBenchHash['YAxis'][1])
										YValue=round(YValue,2)
									else:
										YRunLoop=True
									while (YValue<=YEndValue and YRunLoop==True):
										if 'YAxis' in OPTBenchHash.keys():
											YMotor.SetValue(YValue,MotorSpeed)
											Output_Print("YAxis Successfully set to %.2f"%YValue)
											Status_Write("YAxis Successfully set to %.2f"%YValue)
											YValue=YValue+YStep
											YValue=round(YValue,2)
										else:
											YRunLoop=False
										if 'ZAxis' in OPTBenchHash.keys():
											ZValue=Original_ZAxis+float(OPTBenchHash['ZAxis'][1])
											ZValue=round(ZValue,2)
										else:
											ZRunLoop=True			
										while (ZValue<=ZEndValue and ZRunLoop==True):
											if 'ZAxis' in OPTBenchHash.keys():
												ZMotor.SetValue(ZValue,MotorSpeed)
												Output_Print("ZAxis Successfully set to %.2f"%ZValue)
												Status_Write("ZAxis Successfully set to %.2f"%ZValue)
												ZValue=ZValue+ZStep
												ZValue=round(ZValue,2)
											else:
												ZRunLoop=False	

											if len(PreCondHash.keys())==0:
												PreCondHash["PLACEHOLDER"]={}
											for PreCondKey in PreCondHash.keys():
												if PreCondKey!="PLACEHOLDER":
													##POWERSUPPLY
													Output_Print("Executing Setting of: %s"%PreCondKey)
													Status_Write("Executing Setting of: %s"%PreCondKey)
													Korad_exists='Korad' in locals() or 'Korad' in globals()
													if  not Korad_exists:
														global Korad
														Korad=KA3005P(OtherValuesHash["POWERSUPPLY_COMPORT"])
													Korad.OFF()
													Korad.SET_VOLTAGE(1.8)
													Korad.SET_CURRENT(1.00)
													Korad.ON()
													sleep(3)
													PreConditionFunction(PreCondKey)
												##################################################################
												##Register Sweep 0
												#################################################################
												if 0 in RegisterSweepHash.keys():
													Reg_0=RegisterSweepHash[0][4]
													EndReg_0=RegisterSweepHash[0][6]
													SweepReg_0=True
												else:
													Reg_0=0
													EndReg_0=0
													SweepReg_0=True
												while(Reg_0<=EndReg_0 and SweepReg_0==True):
													if 0 in RegisterSweepHash.keys():
														ModifyRegister(RegisterSweepHash[0][1],RegisterSweepHash[0][2],RegisterSweepHash[0][7],Reg_0)
														Output_Print("Setting Register: %s (%s) == %d"%(RegisterSweepHash[0][0],RegisterSweepHash[0][1],Reg_0))
														Status_Write("Setting Register: %s (%s) == %d"%(RegisterSweepHash[0][0],RegisterSweepHash[0][1],Reg_0))
														Reg_0=Reg_0+RegisterSweepHash[0][8]
													else:
														SweepReg_0=False															
													##################################################################
													##Register Sweep 1
													#################################################################
													if 1 in RegisterSweepHash.keys():
														Reg_1=RegisterSweepHash[1][4]
														EndReg_1=RegisterSweepHash[1][6]
														SweepReg_1=True
													else:
														Reg_1=0
														EndReg_1=0
														SweepReg_1=True
													while(Reg_1<=EndReg_1 and SweepReg_1==True):
														if 1 in RegisterSweepHash.keys():
															ModifyRegister(RegisterSweepHash[1][1],RegisterSweepHash[1][2],RegisterSweepHash[1][7],Reg_1)
															Output_Print("Setting Register: %s (%s) == %d"%(RegisterSweepHash[1][0],RegisterSweepHash[1][1],Reg_1))
															Status_Write("Setting Register: %s (%s) == %d"%(RegisterSweepHash[1][0],RegisterSweepHash[1][1],Reg_1))	
															Reg_1=Reg_1+RegisterSweepHash[1][8]
														else:
															SweepReg_1=False															
														##################################################################
														##Register Sweep 2
														#################################################################
														if 2 in RegisterSweepHash.keys():
															Reg_2=RegisterSweepHash[2][4]
															EndReg_2=RegisterSweepHash[2][6]
															SweepReg_2=True
														else:
															Reg_2=0
															EndReg_2=0
															SweepReg_2=True
														while(Reg_2<=EndReg_2 and SweepReg_2==True):
															if 2 in RegisterSweepHash.keys():
																ModifyRegister(RegisterSweepHash[2][1],RegisterSweepHash[2][2],RegisterSweepHash[2][7],Reg_2)
																Output_Print("Setting Register: %s (%s) == %d"%(RegisterSweepHash[2][0],RegisterSweepHash[2][1],Reg_2))
																Status_Write("Setting Register: %s (%s) == %d"%(RegisterSweepHash[2][0],RegisterSweepHash[2][1],Reg_2))	
																Reg_2=Reg_2+RegisterSweepHash[2][8]
															else:
																SweepReg_2=False	
															##################################################################
															##Register Sweep 3
															#################################################################
															if 3 in RegisterSweepHash.keys():
																Reg_3=RegisterSweepHash[3][4]
																EndReg_3=RegisterSweepHash[3][6]
																SweepReg_3=True
															else:
																Reg_3=0
																EndReg_3=0
																SweepReg_3=True
															while(Reg_3<=EndReg_3 and SweepReg_3==True):
																if 3 in RegisterSweepHash.keys():
																	ModifyRegister(RegisterSweepHash[3][1],RegisterSweepHash[3][2],RegisterSweepHash[3][7],Reg_3)
																	Output_Print("Setting Register: %s (%s) == %d"%(RegisterSweepHash[3][0],RegisterSweepHash[3][1],Reg_3))
																	Status_Write("Setting Register: %s (%s) == %d"%(RegisterSweepHash[3][0],RegisterSweepHash[3][1],Reg_3))	
																	Reg_3=Reg_3+RegisterSweepHash[3][8]
																else:
																	SweepReg_3=False	
																##################################################################
																##Register Sweep 4
																#################################################################
																if 4 in RegisterSweepHash.keys():
																	Reg_4=RegisterSweepHash[4][4]
																	EndReg_4=RegisterSweepHash[4][6]
																	SweepReg_4=True
																else:
																	Reg_4=0
																	EndReg_4=0
																	SweepReg_4=True
																while(Reg_4<=EndReg_4 and SweepReg_4==True):
																	if 4 in RegisterSweepHash.keys():
																		ModifyRegister(RegisterSweepHash[4][1],RegisterSweepHash[4][2],RegisterSweepHash[4][7],Reg_4)
																		Output_Print("Setting Register: %s (%s) == %d"%(RegisterSweepHash[4][0],RegisterSweepHash[4][1],Reg_4))
																		Status_Write("Setting Register: %s (%s) == %d"%(RegisterSweepHash[4][0],RegisterSweepHash[4][1],Reg_4))	
																		Reg_4=Reg_4+RegisterSweepHash[4][8]
																	else:
																		SweepReg_4=False	
																	##################################################################
																	##Register Sweep 5
																	#################################################################
																	if 5 in RegisterSweepHash.keys():
																		Reg_5=RegisterSweepHash[5][4]
																		EndReg_5=RegisterSweepHash[5][6]
																		SweepReg_5=True
																	else:
																		Reg_5=0
																		EndReg_5=0
																		SweepReg_5=True
																	while(Reg_5<=EndReg_5 and SweepReg_5==True):
																		if 5 in RegisterSweepHash.keys():
																			ModifyRegister(RegisterSweepHash[5][1],RegisterSweepHash[5][2],RegisterSweepHash[5][7],Reg_5)
																			Output_Print("Setting Register: %s (%s) == %d"%(RegisterSweepHash[5][0],RegisterSweepHash[5][1],Reg_5))
																			Status_Write("Setting Register: %s (%s) == %d"%(RegisterSweepHash[5][0],RegisterSweepHash[5][1],Reg_5))	
																			Reg_5=Reg_5+RegisterSweepHash[5][8]
																		else:
																			SweepReg_5=False   
																
																		for x in range (0,LoopCount):
																			global OUTPUT
																			OUTPUT=open(OUT_FILE_NAME,"a")
																			###################################################################
																			##Execution Control
																			###################################################################
																			if (TemperatureHash[0] !="Default"):
																				OUTPUT.write("%s,"%TemperatureHash[TempKey])
																			if (HumidityHash[0] !="Default"):
																				OUTPUT.write("%s,"%HumidityHash[HumidKey])
																			if (InputDataHash[0]!="Default"):
																				OUTPUT.write("%s,%s,%s,"%(InputDataHash[InputDataKey]["DataType"],str(InputDataHash[InputDataKey]["DataRate"]),str(InputDataHash[InputDataKey]["VoltageLevel"])))
																			if (PowerSupplyHash[0] !="Default"):
																				OUTPUT.write("%s,"%PowerSupplyHash[PSKey])
																			if (VDDHash[0] !="Default"):
																				OUTPUT.write("%s,"%VDDHash[VDDKey])
																			if (VDDQHash[0] !="Default"):
																				OUTPUT.write("%s,"%VDDQHash[VDDQKey])
																			if('XAxis' in OPTBenchHash.keys()):
																				OUTPUT.write("%.2f(%.2f),"%((XValue-XStep-Original_XAxis),XValue-XStep))
																			if('YAxis' in OPTBenchHash.keys()):
																				OUTPUT.write("%.2f(%.2f),"%((YValue-YStep-Original_YAxis),YValue-YStep))
																			if('ZAxis' in OPTBenchHash.keys()):
																				OUTPUT.write("%.2f(%.2f),"%((ZValue-ZStep-Original_ZAxis),ZValue-ZStep))
																			if (PreCondKey !="PLACEHOLDER"):
																				OUTPUT.write("%s,"%PreCondKey)
																			if (0 in RegisterSweepHash.keys()):
																				OUTPUT.write("%d,"%(Reg_0-RegisterSweepHash[0][8]))
																			if (1 in RegisterSweepHash.keys()):
																				OUTPUT.write("%d,"%(Reg_1-RegisterSweepHash[1][8]))
																			if (2 in RegisterSweepHash.keys()):
																				OUTPUT.write("%d,"%(Reg_2-RegisterSweepHash[2][8]))
																			if (3 in RegisterSweepHash.keys()):
																				OUTPUT.write("%d,"%(Reg_3-RegisterSweepHash[3][8]))
																			if (4 in RegisterSweepHash.keys()):
																				OUTPUT.write("%d,"%(Reg_4-RegisterSweepHash[4][8]))
																			if (5 in RegisterSweepHash.keys()):
																				OUTPUT.write("%d,"%(Reg_5-RegisterSweepHash[5][8]))
																			for ExecKeys in sorted(ExecutionOrderHash.keys()):
																				start_time_global_defined='start_time' in locals() or 'start_time' in globals()
																				if not start_time_global_defined:
																					global start_time 
																					start_time=int(time.time())
																				Output_Print("Enter Execution: %s :: %s"%(ExecutionOrderHash[ExecKeys]["Type"],ExecutionOrderHash[ExecKeys]["Test"]))
																				Status_Write("Enter Execution: %s :: %s"%(ExecutionOrderHash[ExecKeys]["Type"],ExecutionOrderHash[ExecKeys]["Test"]))																				
																				
																				Output_Print("Measurement Count is: %d out of %d"%(MeasurementCount,Points))
																				Status_Write("Measurement Count is: %d out of %d"%(MeasurementCount,Points))																				
																				
																				global OUTPUT_DATA_HASH
																				OUTPUT_DATA_HASH={}
																				if "Bert" in locals() or "Bert" in globals():
																					if "DATA_ELECIDLE" in OtherValuesHash.keys() and OtherValuesHash["DATA_ELECIDLE"]=="True":
																						Bert.TurnOff()
																				if "LS_Bert" in locals() or "LS_Bert" in globals():
																					if "DATA_ELECIDLE" in OtherValuesHash.keys() and OtherValuesHash["DATA_ELECIDLE"]=="True":
																						InputSwingVoltage=Set_VDDQ_Val/2
																						WriteInputSwingVoltage=str(InputSwingVoltage)+"V"
																						LS_Bert.SetVoltage(WriteInputSwingVoltage)
																						LS_Bert.TurnOFF()
																					
																				if ExecutionOrderHash[ExecKeys]["Type"]=="Meas_DSA_Jitter":
																					Meas_DSA_Jitter(ExecKeys)
																				if ExecutionOrderHash[ExecKeys]["Type"]=="Meas_DSA_JitterReTimerOn":
																					Meas_DSA_JitterReTimerOn(ExecKeys)
																				if ExecutionOrderHash[ExecKeys]["Type"]=="Meas_DSA_Frequency":
																					if (ExecutionOrderHash[ExecKeys]["Test"]=="CH1_DUAL"):
																						SetDefaultRegister()
																						MeasureDSAFrequency(1)
																						if OtherValuesHash["CURRENT_DRAWN"]=="True":
																							CurrentReading=Korad.GET_OUTPUT_CURRENT()
																							Output_Print("Current Drawn is %s"%CurrentReading)
																							Status_Write("Current Drawn is %s"%CurrentReading)	
																							OUTPUT.write("%s,"%(CurrentReading))
																					elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH1_SINGLE"):
																						DisableLane(2)
																						EnableLane(1)
																						MeasureDSAFrequency(1)
																						if OtherValuesHash["CURRENT_DRAWN"]=="True":
																							CurrentReading=Korad.GET_OUTPUT_CURRENT()
																							Output_Print("Current Drawn is %s"%CurrentReading)
																							Status_Write("Current Drawn is %s"%CurrentReading)	
																							OUTPUT.write("%s,"%(CurrentReading))
																					elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH2_DUAL"):
																						SetDefaultRegister()
																						MeasureDSAFrequency(2)
																						if OtherValuesHash["CURRENT_DRAWN"]=="True":
																							CurrentReading=Korad.GET_OUTPUT_CURRENT()
																							Output_Print("Current Drawn is %s"%CurrentReading)
																							Status_Write("Current Drawn is %s"%CurrentReading)	
																							OUTPUT.write("%s,"%(CurrentReading))
																					elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH2_SINGLE"):
																						DisableLane(1)
																						EnableLane(2)
																						MeasureDSAFrequency(2)
																						if OtherValuesHash["CURRENT_DRAWN"]=="True":
																							CurrentReading=Korad.GET_OUTPUT_CURRENT()
																							Output_Print("Current Drawn is %s"%CurrentReading)
																							Status_Write("Current Drawn is %s"%CurrentReading)	
																							OUTPUT.write("%s,"%(CurrentReading))
																				elif ExecutionOrderHash[ExecKeys]["Type"]=="Meas_DSA_Amplitude":
																					if (ExecutionOrderHash[ExecKeys]["Test"]=="CH1_DUAL"):
																						SetDefaultRegister()
																						MeasureDSAAmplitude(1)
																						if OtherValuesHash["CURRENT_DRAWN"]=="True":
																							CurrentReading=Korad.GET_OUTPUT_CURRENT()
																							Output_Print("Current Drawn is %s"%CurrentReading)
																							Status_Write("Current Drawn is %s"%CurrentReading)	
																							OUTPUT.write("%s,"%(CurrentReading))
																					elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH1_SINGLE"):
																						DisableLane(2)
																						EnableLane(1)
																						MeasureDSAAmplitude(1)
																						if OtherValuesHash["CURRENT_DRAWN"]=="True":
																							CurrentReading=Korad.GET_OUTPUT_CURRENT()
																							Output_Print("Current Drawn is %s"%CurrentReading)
																							Status_Write("Current Drawn is %s"%CurrentReading)	
																							OUTPUT.write("%s,"%(CurrentReading))
																					elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH2_DUAL"):
																						SetDefaultRegister()
																						MeasureDSAAmplitude(2)
																						if OtherValuesHash["CURRENT_DRAWN"]=="True":
																							CurrentReading=Korad.GET_OUTPUT_CURRENT()
																							Output_Print("Current Drawn is %s"%CurrentReading)
																							Status_Write("Current Drawn is %s"%CurrentReading)	
																							OUTPUT.write("%s,"%(CurrentReading))
																					elif (ExecutionOrderHash[ExecKeys]["Test"]=="CH2_SINGLE"):
																						DisableLane(1)
																						EnableLane(2)
																						MeasureDSAAmplitude(2)
																						if OtherValuesHash["CURRENT_DRAWN"]=="True":
																							CurrentReading=Korad.GET_OUTPUT_CURRENT()
																							Output_Print("Current Drawn is %s"%CurrentReading)
																							Status_Write("Current Drawn is %s"%CurrentReading)	
																							OUTPUT.write("%s,"%(CurrentReading))
																				elif ExecutionOrderHash[ExecKeys]["Type"]=="MeasMultimeter":
																					if (ExecutionOrderHash[ExecKeys]["Test"]=="Voltage"):
																						SetDefaultRegister()
																						MeasureMultimeter("Voltage")
																						if OtherValuesHash["CURRENT_DRAWN"]=="True":
																							CurrentReading=Korad.GET_OUTPUT_CURRENT()
																							Output_Print("Current Drawn is %s"%CurrentReading)
																							Status_Write("Current Drawn is %s"%CurrentReading)	
																							OUTPUT.write("%s,"%(CurrentReading))
																					elif (ExecutionOrderHash[ExecKeys]["Test"]=="Temperature"):
																						SetDefaultRegister()
																						MeasureMultimeter("Temperature")
																						if OtherValuesHash["CURRENT_DRAWN"]=="True":
																							CurrentReading=Korad.GET_OUTPUT_CURRENT()
																							Output_Print("Current Drawn is %s"%CurrentReading)
																							Status_Write("Current Drawn is %s"%CurrentReading)	
																							OUTPUT.write("%s,"%(CurrentReading))
																				elif  ExecutionOrderHash[ExecKeys]["Type"]=="Meas_BertScope":
																					Meas_BertScope()
																					if OtherValuesHash["CURRENT_DRAWN"]=="True":
																						CurrentReading=Korad.GET_OUTPUT_CURRENT()
																						Output_Print("Current Drawn is %s"%CurrentReading)
																						Status_Write("Current Drawn is %s"%CurrentReading)	
																						OUTPUT.write("%s,"%(CurrentReading))
																				RemainingHours=0
																				RemainingMinutes=0
																				RemainingSeconds=0
																				ElapsedTime=int(time.time())-start_time
																				RemainingCount=Points-MeasurementCount
																				RemainingTime=(ElapsedTime/(MeasurementCount))*RemainingCount
																				NowTime = datetime.datetime.now()
																				CompletionTime = NowTime + datetime.timedelta(seconds = RemainingTime)
																				RemainingHours=int(RemainingTime/3600)
																				if RemainingTime>3600:
																					RemainingTime=RemainingTime%3600
																				RemainingMinutes=int(RemainingTime/60)
																				if RemainingTime>60:
																					RemainingTime=RemainingTime%60
																				RemainingSeconds=int(RemainingTime)
																				TimeRemaining="Remaining Time: \t"
																			
																				if RemainingHours!=0:
																					TimeRemaining=TimeRemaining+""+str(RemainingHours)+" Hrs:\t"
																				if RemainingMinutes!=0:
																					TimeRemaining=TimeRemaining+""+str(RemainingMinutes)+" Min:\t"
																				if RemainingSeconds!=0:
																					TimeRemaining=TimeRemaining+""+str(RemainingSeconds)+" Sec"
																				Output_Print("*************************************************************")
																				Status_Write("*************************************************************")
																				Output_Print(TimeRemaining)
																				Status_Write(TimeRemaining)																					
																				Output_Print("Program will complete at: %s"%CompletionTime)
																				Status_Write("Program will complete at: %s"%CompletionTime)
																				Output_Print("*************************************************************")
																				Status_Write("*************************************************************")																						
																				MeasurementCount=MeasurementCount+1
																				OUTPUT.flush()
																				os.fsync(OUTPUT.fileno())											
																			OUTPUT.write("\n")
																		OUTPUT.close()
		
			if 'XAxis' in OPTBenchHash.keys():
				XMotor.SetValue(Original_XAxis,MotorSpeed)
			if 'YAxis' in OPTBenchHash.keys():
				YMotor.SetValue(Original_YAxis,MotorSpeed)
			if 'ZAxis' in OPTBenchHash.keys():
				ZMotor.SetValue(Original_ZAxis,MotorSpeed)
	
			if 'XAxis' in OPTBenchHash.keys():
				XMotor.Clean()
			if 'YAxis' in OPTBenchHash.keys():
				YMotor.Clean()
			if 'ZAxis' in OPTBenchHash.keys():
				ZMotor.Clean()
	Board_X_exists='Board_X' in locals() or 'Board_X' in globals()
	Board_Y_exists='Board_Y' in locals() or 'Board_Y' in globals()
	for BrdKey in BoardConfigHash.keys():
		if BoardConfigHash[BrdKey]["Type"]=="SLTBoard":
			if Board_X_exists and Board_X.ID==BrdKey:
				Board_X.ClosePort()
			if Board_Y_exists and Board_Y.ID==BrdKey:
				Board_Y.ClosePort()

	if (OtherValuesHash["PLOT_DATA"]=="True"):
		Output_Print("User Has Chosen to Plot Data")
		Status_Write("User Has Chosen to Plot Data")
		print BigPrint.renderText("Plot Data")
		Plot_Data(OUT_FILE_NAME)		
	Output_Print("Program Completed")
	Status_Write("Program Completed")
	STATUS_exists='STATUS' in locals() or 'STATUS' in globals()
	if (STATUS_exists):
		STATUS.close()	
	print BigPrint.renderText("Complete")
	Korad_exists='Korad' in locals() or 'Korad' in globals()
	if Korad_exists:
		Korad.CLOSE_POWER_SUPPLY()
	BSA_exists='BSA' in locals() or 'BSA' in globals()
	if BSA_exists:
		BSA.closeBert()

if __name__ == '__main__':
	main(sys.argv[1:])

