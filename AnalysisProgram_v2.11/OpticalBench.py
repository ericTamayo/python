from time import sleep
from sys import exit

from ctypes import c_long, c_buffer, c_float, windll, pointer
Version=0.1
DEBUG=True
MotorSpeed=1.0 #1mm/sec
#################################################################
##Version 0.1 --Dhileepan Thamotharam Release 05/01/2015
##              Keyssa Inc.
##				Base First Version
#################################################################

class OpticalBench:

    def __init__(self,Serial,HwType):
        '''
        HWTYPE_BSC001		11	// 1 Ch benchtop stepper driver
        HWTYPE_BSC101		12	// 1 Ch benchtop stepper driver
        HWTYPE_BSC002		13	// 2 Ch benchtop stepper driver
        HWTYPE_BDC101		14	// 1 Ch benchtop DC servo driver
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000        HWTYPE_SCC001		21	// 1 Ch stepper driver card (used within BSC102,103 units)
        HWTYPE_DCC001		22	// 1 Ch DC servo driver card (used within BDC102,103 units)
        HWTYPE_ODC001		24	// 1 Ch DC servo driver cube
        HWTYPE_OST001		25	// 1 Ch stepper driver cube
        HWTYPE_MST601		26	// 2 Ch modular stepper driver module
        HWTYPE_TST001		29	// 1 Ch Stepper driver T-Cube
        HWTYPE_TDC001		31	// 1 Ch DC servo driver T-Cube
        HWTYPE_LTSXXX		42	// LTS300/LTS150 Long Travel Integrated Driver/Stages
        HWTYPE_L490MZ		43	// L490MZ Integrated Driver/Labjack
        HWTYPE_BBD10X		44	// 1/2/3 Ch benchtop brushless DC servo driver
        '''
        try:
            self.aptdll = windll.LoadLibrary("APT.dll")
            self.aptdll.EnableEventDlg(True)
            self.aptdll.APTInit()
            self.HWType = c_long(HwType)
            self.SerialNum = c_long(Serial)
            self.initializeHardwareDevice()
            
        except:
            print "Error Creating object with Serial Number: %s"%(Serial)
            exit(1)
    
    def initializeHardwareDevice(self):
        try:
            self.aptdll.InitHWDevice(self.SerialNum)
            return True
        except:
            print "Error Initializing Hardware Device"
            return False

    def GetCurrentPosition(self):
        position=c_float()
        self.aptdll.MOT_GetPosition(self.SerialNum,pointer(position))
        return position.value

    def SetValue(self,Value,Speed=MotorSpeed):
        try:
            minVel, acc, maxVel = self.getVelocityParameters()
            if(self.setVelocityParameters(minVel,acc,Speed)):
                absolutePosition = c_float(Value)
                self.aptdll.MOT_MoveAbsoluteEx(self.SerialNum, absolutePosition, True)
                return True
            else:
                return False
        except:
            print "Error Setting Value at: %2f"%Value
            return False

    def getVelocityParameters(self):
        minimumVelocity = c_float()
        acceleration = c_float()
        maximumVelocity = c_float()
        self.aptdll.MOT_GetVelParams(self.SerialNum, pointer(minimumVelocity), pointer(acceleration), pointer(maximumVelocity))
        velocityParameters = [minimumVelocity.value, acceleration.value, maximumVelocity.value]
        return velocityParameters

    def setVelocityParameters(self, minVel, acc, maxVel):
        minimumVelocity = c_float(minVel)
        acceleration = c_float(acc)
        maximumVelocity = c_float(maxVel)
        self.aptdll.MOT_SetVelParams(self.SerialNum, minimumVelocity, acceleration, maximumVelocity)
        return True
    
    def Clean(self):
        self.aptdll.APTCleanUp()
        self.aptdll.APTCleanUp()
        self.aptdll.APTCleanUp()
        self.aptdll.APTCleanUp()




def main():
    from time import sleep
    from sys import exit
    XControlAmount=1.0
    YControlAmount=1.0
    ZControlAmount=1.0

    XRes=0.5
    YRes=0.5
    ZRes=0.5


    

    #####################################################
    ## Please Update to match the correct motor S/N Value
    #####################################################
    XMotorID=83860486
    YMotorID=83860484
    ZMotorID=83860488
  
    XMotor=OpticalBench(XMotorID,31)
    YMotor=OpticalBench(YMotorID,31)
    ZMotor=OpticalBench(ZMotorID,31)


    #####################################################
    ### Obtain current position of motor
    #####################################################
    Original_XAxis=XMotor.GetCurrentPosition()
    Original_YAxis=YMotor.GetCurrentPosition()
    Original_ZAxis=ZMotor.GetCurrentPosition()

    print "Original Coordinates Set X= %.2f, Y=%.2f, Z=%.2f"%(Original_XAxis,Original_YAxis,Original_ZAxis)
    XMotor.Clean()
    YMotor.Clean()
    ZMotor.Clean()

    #####################################################
    ## Example Set Values
    ##################################################### 
    XMotor.SetValue(1.0)
    YMotor.SetValue(2.0)
    ZMotor.SetValue(3.0)



if __name__ == '__main__':
	if (DEBUG):
		print "***********************************************************"
		print "Optical Bench Control Program"
		print "***********************************************************"	
		print "Debug Routine Being Called"
		print "Libary Version %.2f"%Version
		main()
	else:
		print "Loaded OpticalBench Libraries %.2f Successfully"%Version
	
