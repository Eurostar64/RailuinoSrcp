import serial
import DataObjects
import Generators
import srcpserver
import threading
import controlstation
import controlstationSimulated
import sys

def startServer():
    print('Starting SRCP Server v0.7.1')

    canport = sys.argv[1] if(len(sys.argv) > 1) else ''
    s88port = sys.argv[2] if(len(sys.argv) > 2) else ''

    print('CAN Arduino Port is: ' + canport)
    print('S88 Arduino Port is: ' + s88port)

    if (not canport == ''):
        print('starting real world controlstation')
        cs = controlstation.controlstation(canport, s88port)
    else:
        print('starting simulated controlstation')
        cs = controlstationSimulated.controlstationSimulated()
    
    Server = srcpserver.tcpSrcpServer(cs)
    cs.infocb = Server.enqueue

    cs.start()
    Server.start()


print('Starting Railuino 2 Srcp')
startServer()






            


