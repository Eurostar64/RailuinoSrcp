import socket
import threading
import time
import queue
import controlstation

class tcpSrcpServer:
    def __init__(self, controlstation):
        self.TCP_IP = '0.0.0.0'
        self.TCP_PORT = 4304
        self.BUFFER_SIZE = 1024
        self.cu = controlstation
        self.conns = []

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.TCP_IP, self.TCP_PORT))
        while(1):
            s.listen(1)
            conn, addr = s.accept()
            t = threading.Thread(target=tcpSrcpServer.doSingle, args =(self, conn, self.cu))
            t.start()

    def doSingle(self, conn, cu):
        print('Accepted new conn')
        conn = srcpConnection(conn, cu)
        self.conns.append(conn)
        try:
            conn.start()
        except:
            print ("connection closed");

    def enqueue(self, code, codeMsg, Msg):
        print ('INFO_ALL OUT: {} {} {}'.format(code, codeMsg, Msg))
        for conn in self.conns:
            conn.infoqueue.put((code, codeMsg, Msg))
        
            

class srcpConnection:
    clientCount = 0

    def __init__(self, conn, controlstation):
        self.f = conn.makefile("rwb", buffering = 0)
        self.modeIsInfo = -1
        self.handshakeDone = 0
        self.controlstation = controlstation
        self.infoqueue = queue.Queue()

    def sendStringMessage(self, message):
        self.f.write(bytes(message+'\n', 'UTF-8'))

    def sendSrcpAnswer(self, code, codeMessage, message):
        current = time.time()
        self.sendStringMessage('{} {} {} {}'.format(current, code, codeMessage, message))

    def processHandshakeCommand(self, line):
        if line.startswith(b'SET CONNECTIONMODE SRCP'):
            if line.rfind(b'INFO') >= 0:
                self.modeIsInfo = 1
                print('set to info mode')
                return (202, 'OK', 'CONNECTIONMODE')
            if line.rfind(b'COMMAND') >= 0:
                self.modeIsInfo = 0
                print('set to command mode')
                return (202, 'OK', 'CONNECTIONMODE')
        if line.startswith(b'GO'):
            if self.modeIsInfo < 0:
                return (402, 'ERROR', '')
            else:
                srcpConnection.clientCount += 1
                self.handshakeDone = 1
                return (200, 'OK', '{}'.format(srcpConnection.clientCount))
        return (400, 'ERROR', 'unsupported')

    def start(self):
        self.sendStringMessage('Can2SrcpServer 0.1alpha; SRCP 0.8.4;')
        self.controlstation.gatherInfoExisting(self.infoqueue)
        self.infoqueue.put((100, "INFO", '1 POWER {}'.format('ON' if self.controlstation.power else 'OFF')))
        while 1:
            if self.handshakeDone == 0:
                line = self.f.readline().upper()
                code, codeMsg, Msg = self.processHandshakeCommand(line)
                self.sendSrcpAnswer(code, codeMsg, Msg)
            else:
                if self.modeIsInfo == 0:
                    line = self.f.readline().upper()
                    start_time = time.time()
                    print('CMD IN:   {}'.format(line))
                    code, codeMsg, Msg = self.controlstation.handleSrcpCommandString(line)
                    print('INFO OUT: {} {} {}'.format(code, codeMsg, Msg))
                    self.sendSrcpAnswer(code, codeMsg, Msg)
                    print("processed and sent back within %s sec" % (time.time() - start_time))  
                elif self.modeIsInfo == 1:
                    while (not self.infoqueue.empty()) :
                        (code, codeMsg, Msg) = self.infoqueue.get()
                        self.sendSrcpAnswer(code, codeMsg, Msg)
                    time.sleep(0.01)



    
    
