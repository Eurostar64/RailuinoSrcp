import sys
import threading
import serial
import DataObjects
import Generators

class S88RFID:
    
    def __init__(self, portname, modules):
        self.port = portname
        self.totalfbs = (modules * 16) + 1
        self.fbStates = [False] * self.totalfbs
        self.fbStatesChangeHappened = [False] * self.totalfbs
        self.fbStateLastSent = [0] * self.totalfbs
        self.fbLastSentValue = [False] * self.totalfbs
        self.lastrfidtag = ""
        t = threading.Thread(target=S88RFID.open, args=(self,))
        t.start()


    def open(self):
        self.ser = serial.Serial()
        self.ser.port = self.port
        self.ser.baudrate = 9600,
        self.ser.bytesize = 8
        self.ser.parity = 'N'
        self.ser.stopbits=1
        self.ser.timeout=None,
        self.ser.rtscts =1,
        self.ser.setDTR(True)
        self.ser.open()
        
    def serialListener(self):
        while 1:
            readstring = self.ser.readline()
            print(dp.getString())
            if readstring.startswith("FB"):
                spl = readstring.split(":")
                addr = int(spl[1])
                val = bool(spl[2])
                self.fbStates[addr] = val
                self.fbStatesChangeHappened[addr] = true
            elif readstring.startswith("RFID"):
                spl2 = readstring.split("#")
                self.lastrfidtag = spl2[1]

            for i in range(0, self.totalfbs):
                if (self.fbStatesChangeHappened[i] and ( (self.fbStates[i] and (not self.fbLastSentValue[i])) or self.fbStateLastSent[i] == 0)) :
                    # TODO:broadcast fb event
                    fbStatesChangeHappened[i] = false;
                    fbStateLastSent[i] = lastSentFilterMultiplier;
                    fbLastSentValue[i] = fbStates[i];
                elif self.fbStateLastSent[i] > 0:
                    self.fbStateLastSent[i] -= 1

            if self.lastrfidtag != "" :
                # TODO:broadcast rfid event
                self.lastrfidtag = ""






