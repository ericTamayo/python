import serial
import io
from time import sleep
import sys
from time import strftime

Version=0.1
DEBUG=True

#################################################################
##Version 0.1 --Dhileepan Thamotharam Release 05/01/2015
##				Base First Version
#################################################################

class Register:
	def __init__(self,Identification,Port):
		try:
			self.ID=Identification
			self.Object=serial.Serial()
			self.Object.port=Port
			self.Object.baudrate=9600
			self.Object.bytesize=8
			self.Object.stopbits=1
			self.Object.parity='N'
			self.Object.timeout=5
			self.Object.xonxoff=False
		except:
			print "Error Initializing Board: %s Connected at Port: %s"%(Identification,Port)
			exit(1)
    
	def OpenPort(self):
		try:
			OPENED=self.Object.isOpen()
			if not(OPENED):
				self.Object.open()
		except:
			print "Error Opening Port"
			exit(1)

	def ReadAll(self):
		self.Object.flush()
		self.Object.write("a \x0D")
		sleep(1)
		Value=self.Object.read(5000)
		return Value
		
	def ClosePort(self):
		OPENED=self.Object.isOpen()
		if (OPENED):
			self.Object.close()
	
	def Write(self,Lane,Address,Value):
		Value=Value.lower()
		self.Object.flush()
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		
		#print (Address + ":" + Value)
		self.Object.write("w %s %s %s\x0D"%(Address,Value,Lane))
		sleep(0.5)
		ReadBack=self.Read(Lane,Address)
		if (ReadBack!=Value):
			print "Error Writing Register at Port: %s\tLane: %s\tAddress: %s\tValue: %s"%(self.ID,Lane,Address,Value)
			self.ClosePort()
			sleep(1)
			self.OpenPort()
			sleep(1)
			print "Read Value Failed Retrying" 
			self.Write(Lane,Address,Value)
		return True
	
	def dumbWrite(self,Lane,Address,Value):
		Value=Value.lower()
		self.Object.flush()
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		
		#print (Address + ":" + Value)
		self.Object.write("w %s %s %s\x0D"%(Address,Value,Lane))
		sleep(0.5)
				
	def Read(self,Lane,Address):
		self.Object.flush()
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Object.flushInput()
		self.Object.flushOutput()
		self.Object.write("r %s %s \x0D"%(Address,Lane))
		sleep(0.5)
		ReadBack=self.Object.readline()
		if (ReadBack !=""):
			ReadArr=ReadBack.split()
			return ReadArr[6]
		else:
			return ""
	
	def Reset_PassAccu(self,Lane):
		self.Write(Lane,'0x2e','0x0a')
		self.Write(Lane,'0x2e','0x4a')
		self.Write(Lane,'0x2e','0xca')
			
		
	def Read_PassAccu(self, Lane):
		#reads register 0x2a 
		passAccu = self.Read(Lane, '0x2a')
		#print Lane + " 0x2e:" + passAccu
		#converts hex to binary string for bit manipulation
		passAccuBinStr = self.hex2bin(passAccu)
		#converts binary string to binary 
		passAccuBin = int(passAccuBinStr,2)
		#checks passAccu Reg and shifts to LSB
		passAccuBin = (passAccuBin & 0x40) >> 6
		if passAccuBin == 1:
			return True 
		else: 
			return False 
	
	def Read_CalComplete(self, Lane):
		#reads register 0x2a 
		calComplete = self.Read(Lane, '0x2a')
		#print Lane + " 0x2e:" + passAccu
		#converts hex to binary string for bit manipulation
		calCompleteBinStr = self.hex2bin(calComplete)
		#converts binary string to binary 
		calCompleteBin = int(calCompleteBinStr,2)
		#checks passAccu Reg and shifts to LSB
		calCompleteBin = (calCompleteBin & 0x08) >> 3
		returnStr = str(calCompleteBin)
		return returnStr 
		
	
	def Read_LockDetect(self, lane):
		#reads register 0x2a 
		lockDetect = self.Read(lane, '0x2a')
		#converts hex to binary string for bit manipulation
		lockDetectBinStr = self.hex2bin(lockDetect)
		
		#converts binary string to binary 
		lockDetectBin = int(lockDetectBinStr,2)
		#checks passAccu Reg and shifts to LSB
		lockDetectBin = (lockDetectBin & 0x80) >> 7
		return lockDetectBin 

	def Write_Register(self,Lane,Address,StartBit,EndBit,Value):
		Value=Value.lower()
		self.Object.flush()
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"       
		sleep(1)
		ReadOriginal=self.Read(Lane,Address)
		ReadOriginalBin=hex2bin(ReadOriginal)
		ValueBin=bin(int(Value,16))[2:].zfill(EndBit-StartBit+1)
		startLoc=abs(7-EndBit)
		EndLoc=abs(7-StartBit)
		ReplaceStringBin=ReadOriginalBin
		k=0
		for i in range (startLoc,EndLoc+1):
			byte_ReplaceString=bytearray(ReplaceStringBin)
			byte_ReplaceString[i]=ValueBin[k]
			ReplaceStringBin=str(byte_ReplaceString)  
			k=k+1
		UpdateValue='{:0{}X}'.format(int(ReplaceStringBin,2),len(ReplaceStringBin)//4).lower()
		UpdateValue="0x"+UpdateValue
		self.Write(Lane,Address,UpdateValue)

	def hex2bin(self,hex):
		scale=16
		num_of_bits=8
		returnval=bin(int(hex,scale))[2:].zfill(num_of_bits)
		return returnval               

	def Set_Receiver(self,Lane,Char="Default"):
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		if(Char=="Default"):
			self.Write(Lane,"0x10","0x36")
			self.Write(Lane,"0x1b","0x20") 
		elif(Char=="Max"):
			self.Write(Lane,"0x10","0x76")
			self.Write(Lane,"0x1b","0x20") 

	def Set_Transmitter(self,Lane,Char="Default"):
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		if(Char=="Default"):
			self.Write(Lane,"0x10","0xa1")
			self.Write(Lane,"0x1b","0x00") 
		elif(Char=="Max"):
			self.Write(Lane,"0x10","0xc1")
			self.Write(Lane,"0x1b","0x00") 

	def Disable_Lane(self,Lane,Char="Default"):
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Write(Lane,"0x10","0x0f")
		self.Write(Lane,"0x1b","0x20")

	def Read_MiscStatus(self,Lane):
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Write(Lane,"0x1b","0x20")
		sleep(1)
		Value=self.Read(Lane,"0x1c")
		return Value  

	def Read_ReplicaOffset(self,Lane):
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Write(Lane,"0x1b","0x21")
		sleep(1)
		Value=self.Read(Lane,"0x1c")
		return Value  

	def Read_EyeHeight(self,Lane):
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Write(Lane,"0x1b","0x22")
		sleep(1)
		Value=self.Read(Lane,"0x1c")
		ValueInt=int(Value,16)
		if ValueInt>36:
			Value="0x24"
		return Value  

	def Read_UpperSet(self,Lane):
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Write(Lane,"0x1b","0x23")
		sleep(1)
		Value=self.Read(Lane,"0x1c")
		return Value

	def Read_SummOff(self,Lane):
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Write(Lane,"0x1b","0x24")
		sleep(1)
		Value=self.Read(Lane,"0x1c")
		return Value

	def Read_RefSet(self,Lane):
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Write(Lane,"0x1b","0x25")
		sleep(1)
		Value=self.Read(Lane,"0x1c")
		return Value       
		
	def softReset(self,Lane):
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.dumbWrite(Lane, '0x15', '0x91')
		sleep(2)
		
	def Read_GainSet(self,Lane):
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Write(Lane,"0x1b","0x26")
		sleep(1)
		Value=self.Read(Lane,"0x1c")
		return Value

	def Reset(self):
		self.Object.flush()
		self.Object.write("z\x0D")
		sleep(2)
		return True
	
	def SetVDD(self,setValue):
		self.Object.flush()
		Value=str(setValue)
		self.Object.write("p vdd %s\x0D"%Value)
		self.Object.flushInput()
		self.Object.flushOutput()
		self.Reset()
		ReadBack=self.Object.readline()
		return True

	def SetVDDQ(self,setValue):
		self.Object.flush()
		Value=str(setValue)
		self.Object.write("p vddq %s\x0D"%Value)
		self.Object.flushInput()
		self.Object.flushOutput()
		self.Reset()
		ReadBack=self.Object.readline()
		return True
	
	def LDO_RF(self,Lane):
		self.Object.flush();
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Write(Lane,"0x11","0x12")
		self.Write(Lane,"0x17","0xff")
		return True

	def LDO_OD(self,Lane):
		self.Object.flush();
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Write(Lane,"0x11","0x13")
		self.Write(Lane,"0x17","0xff")
		return True

	def LDO_BB(self,Lane):
		self.Object.flush();
		if(Lane=="L1"):
			Lane="0"
		elif(Lane=="L2"):
			Lane="1"
		elif(Lane=="L3"):
			Lane="2"
		self.Write(Lane,"0x11","0x14")
		self.Write(Lane,"0x17","0xff")
		return True

def main():
	Board_A=Register("Board_Right","COM13")
	Board_B=Register("Board_Left","COM14")
	Board_A.OpenPort()
	Board_B.OpenPort()
	
	case = input("Enter debug case to run: ")
	
	
	if case == 1:
		Board_A.SetVDD(1200)
		Board_A.SetVDDQ(1200)
		for k in range(1,20):
			print "*******************************************************"
			print "Regression Testing Count: %d"%k
			Board_A.Write("L1","0x10","0xa1")
			Board_A.Write("L1","0x1b","0x00")
			print "Success Setting Transmitter"	
			Board_A.Write("L2","0x10","0x36")
			Board_A.Write("L2","0x1b","0x20")
			print "Success Setting Receiver"
			print "EyeHeight Value is : %s"%Board_A.Read_EyeHeight("L2")
			print "GainSet Value is : %s"%Board_A.Read_GainSet("L2")
			Val=Board_A.ReadAll()
			print Val
			Board_A.Disable_Lane("L1")
			print "Success Disabling Lane 1"
			Board_A.Disable_Lane("L2")
			print "Success Disabling Lane 2"
			print "*******************************************************\n"
			sleep(5)
	#ReTimer Debug
	elif case == 2:
		run = True
		while (run == True):
			print "Resetting All Accumulators..."
			print "Resetting TX1..."
			Board_A.Reset_PassAccu("L1")
			print "Resetting TX2..."
			Board_B.Reset_PassAccu("L1")
			print "Resetting RX1..."
			Board_A.Reset_PassAccu("L2")
			print "Resetting RX2..."
			Board_B.Reset_PassAccu("L2")
			print "Accumulators Reset"

			if Board_A.Read_PassAccu("L1"):
				print ("TX1 PASS," + " CalComplete:" + Board_A.Read_CalComplete("L1"))
			else:
				print ("TX1 FAIL," + " CalComplete:" + Board_A.Read_CalComplete("L1"))
			
			if Board_B.Read_PassAccu("L2"):
				print ("RX1 PASS," + " CalComplete:" + Board_B.Read_CalComplete("L2"))
			else:
				print ("RX1 FAIL," + " CalComplete:" + Board_B.Read_CalComplete("L2"))
			
			if Board_B.Read_PassAccu("L1"):
				print ("TX2 PASS," + " CalComplete:" + Board_B.Read_CalComplete("L1"))
			else:
				print("TX2 FAIL," + " CalComplete:" + Board_B.Read_CalComplete("L1"))
				
			if Board_A.Read_PassAccu("L2"):
				print("RX2 PASS," + " CalComplete:" + Board_A.Read_CalComplete("L2"))
			else:
				print("RX2 FAIL," + " CalComplete:" + Board_A.Read_CalComplete("L2"))
			
			runAgain = raw_input("Run again?")
			
			if runAgain == 'n':
				break
	
	elif case == 3:
		Board_B.softReset("L1")
		sleep(2)
		Board_B.softReset("L2")
		sleep(2)
		Board_A.softReset("L1")
		sleep(2)
		Board_A.softReset("L2")
		sleep(2)
		
	print "Closing Ports"
	Board_A.ClosePort()
	Board_B.ClosePort()

if __name__ == '__main__':
	if (DEBUG):
		print "Debug Routine Being Called"
		print "SLT Board Libary Version %.2f"%Version
		main()
	else:
		print "Loaded SLTBoard %.2f Successfully"%Version	
