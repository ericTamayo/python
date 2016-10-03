#############################################################
## Agilent Programming for Scope
## Keyssa Inc.
#############################################################
import sys
import visa
import string
import struct

from time import sleep
Version=0.1
DEBUG=True

#################################################################
##Version 0.1 --Dhileepan Thamotharam Release 05/01/2015
##				Base First Version
#################################################################




class Agilent:
    def __init__(self,IPAddress="Default"):
        try:
            ResourceManager=visa.ResourceManager()
            if IPAddress=="Default":
                self.Object=ResourceManager.open_resource("TCPIP0::10.1.40.60::inst0::INSTR")
            else:
                Resource="TCPIP0::"+IPAddress+"::inst0::INSTR"
                self.Object=ResourceManager.open_resource(Resource)
            self.Object.timeout=10000
            self.Object.read_termination=""
            self.Object.write_termination=""
        except:
            print "!!! Agilent Scope Cannot Be Reached and connected"
            exit(1)

    def WriteCommand(self,command):
        try:
            self.Object.write("%s\n"% command)
            sleep(2)
            return True
        except:
            print "!!! Agilent Scope Cannot Written"
            return False
    
    def Reset(self):
        try:
            self.WriteCommand("*IFC")
            sleep(1)
            self.WriteCommand("*CLS")
            sleep(1)
            self.WriteCommand("*RST")
            sleep(3)
            return True
        except:
            print "!!! Agilent Scope Reset Error"
            return False
    def AutoScaleVertical(self,Channel):
        try:
            self.Object.write(":AUToscale:VERTical CHAN%d"%Channel)
            sleep(2)
            self.Object.write(":RUN")
            sleep(5)
            return True;
        except:
            print "!!! Agilent Scope AutoScale Error"
            return False

    def Clear(self):
        try:
            self.WriteCommand("*CLS")
            sleep(1)
            print "--- Clear_Routine::Successful"
            return True
        except:
            print "!!! Agilent Scope Clear Error"
            return False

    def LoadSetupFile(self,fileName):
        try:

            self.Object.write(":DISK:LOAD \"%s\""%fileName)
            sleep(2)
            return True
        except:
            print "!!! Agilent Scope Loading File Error"
            return False
    
    def QueryValues(self,query):
        try:
            queryValue=self.Object.query("%s\n"%query)
            return queryValue
        except:
            print "!!! Agilent Scope QueryValues Error"
            return False
    
    def CheckInitialValues(self):
        try:
            Identification=self.QueryValues("*IDN?")
            return True
        except:
            print "!!! Agilent Scope CheckInitialValues Error"
            return False

    def AcquireAndDigitize(self,CaptureCount):
        try:
            self.WriteCommand(":ACQuire:COMPLete:STATe ON")
            self.WriteCommand(":ACQuire:POINts %d"%CaptureCount)
            sleep(4)
            self.WriteCommand(":DIGitize")
            sleep(1)
            return True
        except:
            print "!!! Agilent Scope AcquireAndDigitize Error"
            return False

    def MeasureJitter(self,Channel):
        if (Channel==1):
            self.WriteCommand(":MEASure:SOURce CHANnel1")
            sleep(1)
            self.WriteCommand(":MEASure:RJDJ:SOURce CHANNEL1")
            sleep(1)
        elif (Channel==2):
            self.WriteCommand(":MEASure:SOURce CHANnel2")
            sleep(1)
            self.WriteCommand(":MEASure:RJDJ:SOURce CHANNEL2")
            sleep(1)
        else:
            print "Incorrect Channel Specified"   
        JitterValue= self.QueryValues(":Measure:RJDJ:TJRJDJ?")
        return JitterValue


def main():
    import sys
    import visa
    import string
    import struct

    from time import sleep

    ScopeIP = "10.1.40.60"
    print "Connecting to: " + ScopeIP

    Scope=Agilent(ScopeIP)

    print "Sucessfully"
    sleep(2)
    if not (Scope.Reset()):
        print "Scope Reset Returned False Exiting...."
        sys.exit(1)
    sleep(5)
    if not(Scope.LoadSetupFile('C:\scope\setups\Jitter_Meas_Channel1.set')):
        print "Load Setup File Returned False Exiting...."
        sys.exit(1)

    sleep(5)

    if not(Scope.AcquireAndDigitize(10000000)):
        print "AcquireAndDigitize Returned False Exiting...."
        sys.exit(1)
    sleep(3)
    JitterValue=Scope.MeasureJitter(1)
    JitterArray=JitterValue.split(',')
    print "Total Jitter (TJ) Value: %s"%JitterArray[1]
    print "Random Jitter (RJ) Value: %s"%JitterArray[4]
    print "Deterministic Jitter (DJ) Value: %s"%JitterArray[7]
        
    if not(Scope.Reset()):
        print "Scope Reset Returned False Exiting...."
        sys.exit(1)
    
if __name__ == '__main__':
	if (DEBUG):
		print "Debug Routine Being Called"
		print "Agilent Libary Version %.2f"%Version
		main()
	else:
		print "Loaded Agilent Libraries %.2f Successfully"%Version
	




