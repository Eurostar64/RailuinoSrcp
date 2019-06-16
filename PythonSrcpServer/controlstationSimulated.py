import sys
import threading
import serial
import time
import DataObjects
import Generators
import controlstation



class controlstationSimulated:
    
    def __init__(self):
        self.locos = {}
        self.acc = {}
        self.fbs = {}
        self.power = False
        self.infocb = None
        
    def start(self):
        print('started')

    # SIMULATED TRACK OPERATIONS

    def writeToTrack(self, package):
        print("SELF:"+package.getString())
        print("SELF:"+package.getString2())
        self.ser.write(package.getBytesToSend())
    
    def setLocoSpeed(self, loco, newSpeed):
        trackSpeed = 1 + (newSpeed - 1) * loco.paceWidth
        trackSpeed = max(0, min(1000, trackSpeed))
        if loco.prot == 'M':
            self.glEventSpeed(loco.addr, trackSpeed)
            return 1
        elif loco.prot == 'N':
            self.glEventSpeed(loco.addr, trackSpeed)
            return 1
        else:
            return 0

    def setLocoEmergencyStop(self, loco):
        if loco.prot == 'M':
            self.glEventSpeed(loco.addr, 0)
            return 1
        elif loco.prot == 'N':
            self.glEventSpeed(loco.addr, 0)
            return 1
        else:
            return 0

    def setLocoDirection(self, loco, newDirection_SrcpParam):
        
        newDir_CanParam = 0 #stay the same
        if newDirection_SrcpParam == 0: #backward
            newDir_CanParam = 2
        elif newDirection_SrcpParam == 1: #forward
            newDir_CanParam = 1

        if loco.prot == 'M':
            self.glEventDirection(loco.addr, newDir_CanParam)
            return 1
        elif loco.prot == 'N':
            self.glEventDirection(loco.addr, newDir_CanParam)
            return 1
        else:
            return 0

    def setLocoFunction(self, loco, fIdx, fVal):
        if fIdx >= len(loco.functions):
            return 0

        if loco.prot == 'M':
            self.glEventFunction(loco.addr, fIdx, fVal)
            return 1
        elif loco.prot == 'N':
            self.glEventFunction(loco.addr, fIdx, fVal)
            return 1
        else:
            return 0

    # ACC OPERATIONS

    def setSwitch(self, acc, port, delay):
        time.sleep(1)
        self.gaEvent(acc.addr, port, 1)
        return 1

    #Power

    def POWER_SET(self, status):
        if status:
            self.powerEvent(1)
            return 1
        else:
            self.powerEvent(0)
            return 1

    # Events / FB / RFID

    def fbEvent(self, address, value):
        self.FB_SET(address, value)

    def rfidEvent(self, tag):
        self.infocb(100, 'INFO', '1 RFID {}'.format(tag))

    def FB_SET(self, address, value):
        val2Send = "1" if value else "0"
        self.infocb(100, 'INFO', '1 FB {} {}'.format(address, val2Send))
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
            loco = controlstation.GenericLoco(addr, prot, protversion, decoderspeedsteps, numberfunctions)
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
            sw = controlstation.GenericSwitch(addr, prot)
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
            #if switch.port != port:
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
        for fb_addr in self.fbs:
            if(self.fbs[fb_addr]):
                l.append(self.getSingleInfoTupleFB(fb_addr))
        #send messages
        for (code, codeMsg, Msg) in l:
            infoqueue.put((code, codeMsg, Msg))


    def getSingleInfoTupleGL(self, gl):
        return (101, 'INFO', '1 GL {} {} {} {} {}'.format(gl.addr, gl.prot, gl.protversion, gl.decoderspeedsteps, gl.numberoffunctions))

    def getSingleInfoTupleGA(self, ga):
        return (101, 'INFO', '1 GA {} {}'.format(ga.addr, ga.prot))

    def getSingleInfoTupleFB(self, fb_addr):
        val2Send = "1" if self.fbs[fb_addr] else "0"
        return (100, 'INFO', '1 FB {} {}'.format(fb_addr, val2Send))

        
        

            

