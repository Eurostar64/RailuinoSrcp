import Generators

class DataPackage:

    def __init__(self):
        self.Command = 0
        self.data = bytes([])
        self.isResponse = 0

    def setFromIncomingPackage(self, databytes):
        self.data = bytearray([])
        self.Command = (databytes[0] << 7) | ((databytes[1] & 0xFE) >> 1)
        self.isResponse = (databytes[1] & 0x01)
        
        for i in range(5,13):
            self.data.append(databytes[i])
            
    def setFields(self, cmd, isResponse, data):
        self.Command = cmd
        self.isResponse = isResponse
        self.data = data   

    def getString(self):
        ds = 'command {} response: {}, systemSubCmd: {} data: '.format(self.Command, self.isResponse, self.getSystemSubcmd())
        for i in range(0, len(self.data)):
            ds += '{} '.format(self.data[i])
        return ds
    def getString2(self):
        s = '';
        if self.Command == 0x00:
            s += "System:"
            if   self.data[4] == 0x00: s+= "Stop"
            elif self.data[4] == 0x01: s+= "Go"
            elif self.data[4] == 0x01: s+= "Halt"
            elif self.data[4] == 0x01: s+= "EmergencyStop"+self.getAddressString()
        elif self.Command == 0x04:
            s += "LokGeschwindigkeit: address:{} V:{}".format(self.getAddressString(), self.getSpeedAsNumber())
        elif self.Command == 0x05:
            s += "LokRichtung: address:{} dir:{}".format(self.getAddressAsNumber(), self.getDirectionAsNumber())
        elif self.Command == 0x06:
            s += "LokFunktion: address:{} funcNo:{} val:{}".format(self.getAddressAsNumber(), self.getFunctionNoAsNumber(), self.getFunctionValAsNumber())
        elif self.Command == 0x0B:
            s += "GA SET Address:{} Port:{} Value:{}".format(self.getAddressAsNumber(), self.getGAPort(), self.getGAValue())
        elif self.Command == 0x18:
            s += "Devices Ping"


        return s;

    def getAddressString(self):
        gc = Generators.CommandGenerator
        add = gc.getAddressBackFromBytes(self.data)[0]
        if (add < 0x03FF):
            return 'MM2 GL: {}'.format(add)
        elif (add < 0x33FF):
            return 'MM2 GA: {}'.format(add-0x3000)
        elif (add < 0x3FFF):
            return 'DCC GA: {}'.format(add-0x3800)
        elif (add < 0x7FFF):
            return 'MFX: {}'.format(add-0x4000)
        elif (add < 0xFFFF):
            return 'DCC GL: {}'.format(add-0xC000)

    def getAddressAsNumber(self):
        gc = Generators.CommandGenerator
        add = gc.getAddressBackFromBytes(self.data)[0]
        if (add < 0x03FF):
            return add
        elif (add < 0x33FF):
            return add-0x3000
        elif (add < 0x3FFF):
            return add-0x3800
        elif (add < 0x7FFF):
            return add-0x4000
        elif (add < 0xFFFF):
            return add-0xC000

    def getSpeedAsNumber(self):
        gc = Generators.CommandGenerator
        return gc.getSpeedBackFromBytes(self.data)[0]

    def getDirectionAsNumber(self):
        gc = Generators.CommandGenerator
        return gc.get4thBackFromBytes(self.data)[0]

    def getFunctionNoAsNumber(self):
        gc = Generators.CommandGenerator
        return gc.get4thBackFromBytes(self.data)[0]

    def getFunctionValAsNumber(self):
        gc = Generators.CommandGenerator
        return gc.get5thBackFromBytes(self.data)[0]

    def getGAPort(self):
        gc = Generators.CommandGenerator
        return gc.get4thBackFromBytes(self.data)[0]

    def getGAValue(self):
        gc = Generators.CommandGenerator
        return gc.get5thBackFromBytes(self.data)[0]

    def getSystemSubcmd(self):
        return self.data[4]

    def getBytesToSend(self):
        bb = bytearray(b'\x00' * 13)
        bb[0] = (self.Command >> 7) & 0x01
        bb[1] = ((self.Command & 0x7F) << 1) | (self.isResponse & 0x01)
        bb[4] = len(self.data) # ev. TODO
        #print('data length is {}'.format(len(self.data)))
        for i in range(0, len(self.data)):
            bb[i+5] = self.data[i]
        
        return bb




