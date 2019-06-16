import DataObjects
import struct

class CommandGenerator:

    @staticmethod
    def SystemStop():
        d1 = bytearray([0x0, 0x0, 0x0, 0x0, 0x0])
        db = DataObjects.DataPackage()
        db.setFields(0,0,d1)
        return db

    @staticmethod
    def SystemGo():
        d1 = bytearray([0x0, 0x0, 0x0, 0x0, 0x01])
        db = DataObjects.DataPackage()
        db.setFields(0,0,d1)
        return db

    @staticmethod
    def LocoEmergencyStop(addressBytes):
        d1 = bytearray([addressBytes[0], addressBytes[1],addressBytes[2], addressBytes[3], 0x03])
        db = DataObjects.DataPackage()
        db.setFields(0,0,d1)
        return db

    @staticmethod
    def LocoRemoveFromList(addressBytes):
        d1 = bytearray([addressBytes[0], addressBytes[1],addressBytes[2], addressBytes[3], 0x04])
        db = DataObjects.DataPackage()
        db.setFields(0,0,d1)
        return db

    #Track Param values
    # MM2 / DCC according to specification in protocol
    @staticmethod
    def LocoChangeFormat(addressBytes, trackParam):
        d1 = bytearray([addressBytes[0], addressBytes[1],addressBytes[2], addressBytes[3], 0x04, trackParam])
        db = DataObjects.DataPackage()
        db.setFields(0,0,d1)
        return db

    @staticmethod
    def LocoSetSpeed(addressBytes, speed):
        speed = max(0, min(1000, speed))
        d1 = bytearray([addressBytes[0], addressBytes[1],addressBytes[2], addressBytes[3], CommandGenerator.getXthByte(speed, 2), CommandGenerator.getXthByte(speed, 3)])
        db = DataObjects.DataPackage()
        db.setFields(0x04,0,d1)
        #print('speed bytes are 4:{} 5:{}'.format(d1[4], d1[5]))
        return db

    #directionParam according to protocol (0: stay the same, 1: forward, 2:
    #backward)
    @staticmethod
    def LocoSetDirection(addressBytes, directionParam):
        d1 = bytearray([addressBytes[0], addressBytes[1],addressBytes[2], addressBytes[3], directionParam])
        db = DataObjects.DataPackage()
        db.setFields(0x05,0,d1)
        return db

    @staticmethod
    def LocoSetFunction(addressBytes, fIdx, fVal):
        d1 = bytearray([addressBytes[0], addressBytes[1],addressBytes[2], addressBytes[3], fIdx, fVal])
        db = DataObjects.DataPackage()
        db.setFields(0x06,0,d1)
        return db

    ### Acc

    @staticmethod
    def SwitchSet(addressBytes, port, on):
        d1 = bytearray([addressBytes[0], addressBytes[1],addressBytes[2], addressBytes[3], port, on, 0, 0])
        db = DataObjects.DataPackage()
        db.setFields(0x0B,0,d1)
        return db


    ### HELPERS
    
    @staticmethod
    def getLocoAddressMM2(addr):
        return CommandGenerator.getAddressBytes(addr)

    @staticmethod
    def getLocoAddressDCC(addr):
        return CommandGenerator.getAddressBytes(0xC000 + addr)

    @staticmethod
    def getAccAddressMM2(addr):
        return CommandGenerator.getAddressBytes(0x3000 + addr)

    @staticmethod
    def getAccAddressDCC(addr):
        return CommandGenerator.getAddressBytes(0x3800 + addr)

    @staticmethod 
    def getAddressBytes(addr):
        bb = bytearray([CommandGenerator.getXthByte(addr, 0), 
                        CommandGenerator.getXthByte(addr, 1), 
                        CommandGenerator.getXthByte(addr, 2), 
                        CommandGenerator.getXthByte(addr, 3)])
        #print('addr bytes are 0:{} 1:{} 2:{} 3:{}'.format(bb[0], bb[1], bb[2],
        #bb[3]))
        return bb

    @staticmethod 
    def getAddressBackFromBytes(data):
        bb = bytearray([data[0], data[1], data[2], data[3]])
        return struct.unpack(">I", bb)

    @staticmethod 
    def getSpeedBackFromBytes(data):
        bb = bytearray([data[4], data[5]])
        return struct.unpack(">H", bb)

    @staticmethod 
    def get4thBackFromBytes(data):
        bb = bytearray([data[4]])
        return struct.unpack(">B", bb)

    @staticmethod 
    def get5thBackFromBytes(data):
        bb = bytearray([data[5]])
        return struct.unpack(">B", bb)

    #0 is 'lowest' byte
    @staticmethod
    def getXthByte(val, idx):
        bb = bytes(struct.pack('>I', val))
        if idx < len(bb):
            return bb[idx]
        else:
            return 0


