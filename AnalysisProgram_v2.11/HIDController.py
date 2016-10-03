
import sys
import string
from mcp2210 import MCP2210
import os
from time import sleep

Version=0.1
DEBUG=False

#################################################################
##Version 0.1 --Dhileepan Thamotharam Release 05/01/2015
##				Base First Version
#################################################################

class HIDControl():
    def __init__(self,Identification):
        self.dev = MCP2210(1240, 222)
        self.ID=Identification
        settings = self.dev.chip_settings
        settings.pin_designations[0] = 0x01  # GPIO 0 to chip select
        self.dev.chip_settings = settings  # Settings are updated on property assignment

        
    def selectChip(self, Val):
        if(Val=="L1" or Val=="0"):
            chipID=0
        elif(Val=="L2" or Val=="0"):
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
        toWrite |= (data & mask)                #data and mask
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

def main():
    Board=HIDControl()
    Board.selectChip(0)
    Board.Write(0x00,0xff)
    MaxCount=41

    for x in range(0,42):
        HexVal=hex(x)
        ReadBackValue=format(Board.Read(x),'#04x')
        print "Value Read at Address: %s\t = %s"%(HexVal,ReadBackValue)


if __name__ == '__main__':
	if (DEBUG):
		print "Debug Routine Being Called"
		print "HID Libary Version %.2f"%Version
		main()
	else:
		print "Loaded HID Libraries %.2f Successfully"%Version
	




   
    
