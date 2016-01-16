import sys
import threading
import serial
import time
import DataObjects
import Generators

class GenericLoco:
    
    def __init__(self, addr, prot, protversion, decoderspeedsteps, numberoffunctions):
        self.addr = addr
        self.prot = prot
        self.protversion = protversion
        self.decoderspeedsteps = int(decoderspeedsteps)
        self.numberoffunctions = numberoffunctions    
        self.drivemode = 0
        self.v = 0
        self.vmax = decoderspeedsteps
        self.functions = [False] * numberoffunctions

        #pace width is according to maerklin spec
        paceWidth = 0
        if self.decoderspeedsteps == 14:
            paceWidth = 77
        elif self.decoderspeedsteps == 27:
            paceWidth = 38
        elif self.decoderspeedsteps == 28:
            paceWidth = 37
        elif self.decoderspeedstepss == 31:
            paceWidth = 33
        elif self.decoderspeedsteps == 126:
            paceWidth = 8
        else:
            paceWidth = int(round(1000 / loco.decoderspeedsteps))

        self.paceWidth = paceWidth

class GenericSwitch:

    def __init__(self, addr, prot):
        self.addr = addr
        self.prot = prot
        self.port = 0
        self.value = 0


class controlstation:
    
    def __init__(self, portnameCAN, portnameFB):
        self.portnameCAN = portnameCAN
        self.portnameFB = portnameFB
        self.locos = {}
        self.acc = {}
        self.fbs = {}
        self.power = False
        self.infocb = None
        
    def start(self):
        #open CAN connection and start listening
        self.ser = serial.Serial(port = self.portnameCAN, baudrate = 500000, bytesize=8, parity='N', stopbits=1, timeout=None, rtscts=1)
        print('serial conn to arduino (CAN) open')
        t = threading.Thread(target=controlstation.serialListener, args=(self,))
        t.start()
        #if set -> open connection to FB arduino
        if not self.portnameFB == '' :
            self.serFB = serial.Serial(port = self.portnameFB, baudrate = 9600, bytesize=8, parity='N', stopbits=1, timeout=None, rtscts=1)
            print('serial conn to arduino (FB) open')
            t = threading.Thread(target=controlstation.serialListenerFB, args=(self,))
            t.start()

    def serialListener(self):
        while 1:
            #print(self.ser.readline())
            dp = DataObjects.DataPackage()
            dp.setFromIncomingPackage(self.ser.read(13))
            if dp.isResponse or True:
                print("CAN :"+dp.getString())
                print("CAN :"+dp.getString2())
                s = '';
                #handle packet
                if dp.Command == 0x00:
                    if   dp.data[4] == 0x00: self.powerEvent(0)
                    elif dp.data[4] == 0x01: self.powerEvent(1)
                    elif dp.data[4] == 0x02: s+= "Halt"
                    elif dp.data[4] == 0x03: self.glEventSpeed(dp.getAddressAsNumber(), 0)
                elif dp.Command == 0x04:
                    self.glEventSpeed(dp.getAddressAsNumber(), dp.getSpeedAsNumber())
                elif dp.Command == 0x05:
                    self.glEventDirection(dp.getAddressAsNumber(), dp.getDirectionAsNumber())
                elif dp.Command == 0x06:
                    self.glEventFunction(dp.getAddressAsNumber(), dp.getFunctionNoAsNumber(), dp.getFunctionValAsNumber())
                elif dp.Command == 0x0B:
                    self.gaEvent(dp.getAddressAsNumber()+1, dp.getGAPort(), dp.getGAValue());

    def serialListenerFB(self):
        while 1:
            line = str(self.serFB.readline())
            if line.startswith('FB'):
                spl = line.split(':')
                address = spl[1]
                value = int(spl[2]) > 0
                self.fbEvent(address, value)
            elif line.startswith('RFID'):
                spl = line.split('#')
                rfidtag = spl[1]
                self.rfidEvent(rfidtag)


    # TRACK OPERATIONS

    def writeToTrack(self, package):
        print("SELF:"+package.getString())
        print("SELF:"+package.getString2())
        self.ser.write(package.getBytesToSend())
    
    def setLocoSpeed(self, loco, newSpeed):
        gc = Generators.CommandGenerator
        trackSpeed = 1 + (newSpeed - 1) * loco.paceWidth
        trackSpeed = max(0, min(1000, trackSpeed))
        if loco.prot == 'M':
            package = gc.LocoSetSpeed(gc.getLocoAddressMM2(loco.addr), trackSpeed)
            self.writeToTrack(package)
            return 1
        elif loco.prot == 'N':
            package = gc.LocoSetSpeed(gc.getLocoAddressDCC(loco.addr), trackSpeed)
            self.writeToTrack(package)
            return 1
        else:
            return 0

    def setLocoEmergencyStop(self, loco):
        gc = Generators.CommandGenerator
        if loco.prot == 'M':
            package = gc.LocoEmergencyStop(gc.getLocoAddressMM2(loco.addr))
            self.writeToTrack(package)
            return 1
        elif loco.prot == 'N':
            package = gc.LocoEmergencyStop(gc.getLocoAddressDCC(loco.addr))
            self.writeToTrack(package)
            return 1
        else:
            return 0

    def setLocoDirection(self, loco, newDirection_SrcpParam):
        gc = Generators.CommandGenerator
        newDir_CanParam = 0 #stay the same
        if newDirection_SrcpParam == 0: #backward
            newDir_CanParam = 2
        elif newDirection_SrcpParam == 1: #forward
            newDir_CanParam = 1

        if loco.prot == 'M':
            package = gc.LocoSetDirection(gc.getLocoAddressMM2(loco.addr), newDir_CanParam)
            self.writeToTrack(package)
            return 1
        elif loco.prot == 'N':
            package = gc.LocoSetDirection(gc.getLocoAddressDCC(loco.addr), newDir_CanParam)
            self.writeToTrack(package)
            return 1
        else:
            return 0

    def setLocoFunction(self, loco, fIdx, fVal):
        gc = Generators.CommandGenerator
        if fIdx >= len(loco.functions):
            return 0

        if loco.prot == 'M':
            package = gc.LocoSetFunction(gc.getLocoAddressMM2(loco.addr), fIdx, fVal)
            self.writeToTrack(package)
            return 1
        elif loco.prot == 'N':
            package = gc.LocoSetFunction(gc.getLocoAddressDCC(loco.addr), fIdx, fVal)
            self.writeToTrack(package)
            return 1
        else:
            return 0

    # ACC OPERATIONS

    def setSwitch(self, acc, port, delay):
        gc = Generators.CommandGenerator
        start_time = time.time()           
        if acc.prot == 'M':
            package = gc.SwitchSet(gc.getAccAddressMM2(acc.addr-1), port, 1);
            self.writeToTrack(package)
            time.sleep(1.0)
            package2 = gc.SwitchSet(gc.getAccAddressMM2(acc.addr-1), port, 0);
            self.writeToTrack(package2)
        elif acc.prot == 'N':
            package = gc.SwitchSet(gc.getAccAddressDCC(acc.addr-1), port, 1);
            self.writeToTrack(package)
            time.sleep(1.0)
            package2 = gc.SwitchSet(gc.getAccAddressDCC(acc.addr-1), port, 0);
            self.writeToTrack(package2)
        print("setSwitch completed within %s sec" % (time.time() - start_time)) 
        return 1

    #Power

    def POWER_SET(self, status):
        gc = Generators.CommandGenerator
        if status:
            package = gc.SystemGo()
            self.writeToTrack(package)
            return 1
        else:
            package = gc.SystemStop()
            self.writeToTrack(package)
            return 1

    # Events / FB / RFID

    def fbEvent(self, address, value):
        self.FB_SET(address, value)

    def rfidEvent(self, tag):
        self.infocb(100, 'INFO', '1 RFID {}'.format(tag))

    def FB_SET(self, address, value):
        self.infocb(100, 'INFO', '1 FB {} {}'.format(address, value))
        self.fbs[address] = value
        return 1

    # Events / GL / GA fromTrack

    def glEventSpeed(self, addr, speed):
        if addr in self.locos:
            loco = self.locos[addr]
            if speed > 0:
                loco.v = int(round((speed - 1 + loco.paceWidth)/loco.paceWidth, 0))
            else:
                loco.v = 0
            self.infocb(100, 'INFO', self.GL_GET(addr))

    def glEventDirection(self, addr, direction):
        if addr in self.locos:
            loco = self.locos[addr]
            newDrivemode = 0
            if direction == 1:
                newDrivemode = 1
            elif direction == 2:
                newDrivemode = 0
            elif direction == 3:
                newDrivemode = 1 if loco.drivemode == 0 else 0

            if newDrivemode != loco.drivemode:
                loco.drivemode = newDrivemode
                loco.v = 0
                self.infocb(100, 'INFO', self.GL_GET(addr))

    def glEventFunction(self, addr, functionNo, functionOn):
        functionOnBool = functionOn == 1
        if addr in self.locos:
            loco = self.locos[addr]
            if loco.numberoffunctions > functionNo:
                if loco.functions[functionNo] != functionOnBool:
                    loco.functions[functionNo] = functionOnBool
                    self.infocb(100, 'INFO', self.GL_GET(addr))
                 
    def gaEvent(self, addr, port, value):
        #port = 1 if port == 0 else 0
        if addr in self.acc:
            ga = self.acc[addr]
            if port != ga.port or value != ga.value:
                ga.port = port
                ga.value = value
                self.infocb(100, 'INFO', self.GA_GET(addr))

    def powerEvent(self, on):
        if on == 1:
            self.infocb(101, 'INFO', '1 POWER ON')
        else:
            self.infocb(101, 'INFO', '1 POWER OFF')


    # COMMANDS

    def GL_INIT(self, addr, prot, protversion, decoderspeedsteps, numberfunctions):
        if addr in self.locos:
            return 0
        else:
            loco = GenericLoco(addr, prot, protversion, decoderspeedsteps, numberfunctions)
            self.locos[addr] = loco
            (code, codeMsg, Msg) = self.getSingleInfoTupleGL(loco)
            self.infocb(code, codeMsg, Msg)
            return 1

    def GL_GET(self, addr):
        if addr in self.locos:
            loco = self.locos[addr]
            s = '1 GL {} {} {} {}'.format(loco.addr, loco.drivemode, loco.v, loco.vmax)
            for i in range(0, len(loco.functions)):
                s += ' {}'.format('1' if loco.functions[i] else '0')
            return s
        else:
            return 0

    def GL_SET(self, addr, drivemode, v, vmax, fargs):
        if addr in self.locos:
            loco = self.locos[addr]
            
            if loco.drivemode != drivemode:
                if drivemode == 2:
                    self.setLocoEmergencyStop(loco)

                else:
                    if self.setLocoDirection(loco, drivemode):
                        loco.drivemode = drivemode
            
            if loco.v != v and not drivemode == 2:
                self.setLocoSpeed(loco, v)
                    
            if not (fargs is None):
                for i in range(0, len(loco.functions)):
                    if loco.functions[i] != fargs[i]:
                        self.setLocoFunction(loco, i, fargs[i])
                       

            #self.infocb(100, 'INFO', self.GL_GET(addr))
            return 1
        else:
            return 0

    def GL_TERM(self, addr):
        if addr in self.locos:
            #set engine to 0 - stop loco
            loco = self.locos[addr]
            self.setLocoSpeed(loco, 0)
            del self.locos[addr]
            return 1
        else:
            return 0

    def GA_INIT(self, addr, prot):
        if addr in self.acc:
            return 0
        else:
            sw = GenericSwitch(addr, prot)
            self.acc[addr] = sw
            (code, codeMsg, Msg) = self.getSingleInfoTupleGA(sw)
            self.infocb(code, codeMsg, Msg)
            return 1

    def GA_GET(self, addr):
        if addr in self.acc:
            switch = self.acc[addr]
            s = '1 GA {} {} {}'.format(switch.addr, switch.port, switch.value)
            return s
        else:
            return 0

    def GA_SET(self, addr, port, delay):
        if addr in self.acc:
            switch = self.acc[addr]
            if switch.port != port:
                self.setSwitch(switch, port, delay)
            return 1
        else:
            return 0

    def GL_TERM(self, addr):
        if addr in self.acc:
            del self.acc[addr]
            return 1
        else:
            return 0


    


    # dispatch commands
    def handleSrcpCommandString(self, str):
        try:
            res = 0
            msg = ''
            infoMsg = ''
            spl = str.decode("utf-8").split()

            if(spl[2] == 'GL'):
                if(spl[0] == 'INIT'):
                    res = self.GL_INIT(int(spl[3]), spl[4], int(spl[5]), int(spl[6]), int(spl[7]))
                elif(spl[0] == 'TERM'):
                    res = self.GL_TERM(int(spl[3]))
                elif(spl[0] == 'GET'):
                    msg = self.GL_GET(int(spl[3]))
                elif(spl[0] == 'SET'):
                    fnlength = len(spl) - 7
                    if fnlength > 0:
                        dd = [False] * fnlength
                        for i in range(0, fnlength):
                            dd[i] = spl[7+i] == '1'
                        res = self.GL_SET(int(spl[3]), int(spl[4]), int(spl[5]), int(spl[6]), dd)
                    else:
                        res = self.GL_SET(int(spl[3]), int(spl[4]), int(spl[5]), int(spl[6]), None)

            
            elif(spl[2] == 'GA'):
                if(spl[0] == 'INIT'):
                    res = self.GA_INIT(int(spl[3]), spl[4])
                elif(spl[0] == 'TERM'):
                    res = self.GA_TERM(int(spl[3]))
                elif(spl[0] == 'GET'):
                    msg = self.GA_GET(int(spl[3]))
                elif(spl[0] == 'SET'):
                    res = self.GA_SET(int(spl[3]), int(spl[4]), int(spl[5]))

           
            
            elif(spl[2] == 'POWER'):
                if(spl[0] == 'SET'):
                    res = self.POWER_SET(spl[3] == 'ON')

            elif(spl[2] == 'FB'):
                if(spl[0] == 'SET'):
                    res = self.FB_SET(int(spl[3]), int(spl[4]))

            if msg != '':
                return (100, 'INFO', msg)
            elif res:
                return (200, 'OK', '')
            else:
                return (400, 'ERROR', 'unsupported')
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return (400, 'ERROR', 'unsupported')
            raise

    def gatherInfoExisting(self, infoqueue):
        l = []
        for gl_addr in self.locos:
            l.append(self.getSingleInfoTupleGL(self.locos[gl_addr]))
        for ga_addr in self.acc:
            l.append(self.getSingleInfoTupleGA(self.acc[ga_addr]))
        #send messages
        for (code, codeMsg, Msg) in l:
            infoqueue.put((code, codeMsg, Msg))


    def getSingleInfoTupleGL(self, gl):
        return (101, 'INFO', '1 GL {} {} {} {} {}'.format(gl.addr, gl.prot, gl.protversion, gl.decoderspeedsteps, gl.numberoffunctions))

    def getSingleInfoTupleGA(self, ga):
        return (101, 'INFO', '1 GA {} {}'.format(ga.addr, ga.prot))

        
        

            

