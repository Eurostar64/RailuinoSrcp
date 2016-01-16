import serial
import DataObjects
import Generators
import srcpserver
import threading
import controlstation

def startServer():
    print('Starting SRCP Server v0.7.1')
    cs = controlstation.controlstation('COM4', '')
    
    Server = srcpserver.tcpSrcpServer(cs)
    cs.infocb = Server.enqueue

    cs.start()
    Server.start()


print('Starting Railuino 2 Srcp')
#t1  = threading._start_new_thread(startServer, ())
startServer()


#print('Starting Serial Conn')
#ser = serial.Serial(port = 'COM5', baudrate = 500000, bytesize=8, parity='N', stopbits=1, timeout=None, rtscts=1)
#print('Opening: ')
#print(ser.name)

#i = 0;
#while i < 2:
#    dp = DataObjects.DataPackage()
#    dp.setFromIncomingPackage(ser.read(13))
#    print(dp.getString())
#    i += 1

#gc = Generators.CommandGenerator

#packageStop = gc.SystemGo()
#ser.write(packageStop.getBytesToSend())

#packageStop2 = gc.LocoSetDirection(gc.getLocoAddressDCC(18), 3)
#ser.write(packageStop2.getBytesToSend())

#packageF2 = gc.LocoSetFunction(gc.getLocoAddressDCC(18), 0, 1)
#ser.write(packageF2.getBytesToSend())

#packageF3 = gc.SwitchSet(gc.getAccAddressDCC(0), 1, 1);
#ser.write(packageF3.getBytesToSend())
#print(packageF3.getString())

#packageF4 = gc.SwitchSet(gc.getAccAddressDCC(0), 1, 0);
#ser.write(packageF4.getBytesToSend())
#print(packageF4.getString())



#i = 0
#while i < 100:
#    dp = DataObjects.DataPackage()
#    dp.setFromIncomingPackage(ser.read(13))
#    print(dp.getString())
#    i += 1

#ser.close()




            


