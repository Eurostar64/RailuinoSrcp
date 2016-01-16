# RailuinoSrcp
A python program plus arduino sketches to connect your märklin model railway to the computer and expose its functionality via the SRCP protocol

## Dependencies
This entire project builds up on the great Railuino library of J. Pleumann which can be found here: https://code.google.com/p/railuino/

### Hardware needed
For this to work you need access to the Märklin CAN-Bus which interconnects the Mobile Station, Boosters etc. The Railuino-Library on which this builds up is using the "TrackBox" (used alongside with the Mobile Station 2) and a special ArduinoShield to connect the Arduino to the CAN-Bus.
This project also offers the availability to include S88 feedbacks. The S88 bus is read on a second arduino device

#### Märklin Mobile Station 2 and TrackBox
The MS2 is usually bundled with the trackbox. 

#### CANdiy-Shield
This shield was specifically designed to connect an Arduino to the CAN-Bus of Märklin. But since it contains "off-the-shelves" components the shield can also be used for other applications. It is available at watterott e-shop: http://www.watterott.com/de/Arduino-CANdiy-Shield to connect the shield to the track box these components are needed as well: http://www.watterott.com/de/Railuino-Komponenten?x58466=4061ae1d88bc6811010f8f9e6428b1df
Unfortunately the assembly of the Shield isn't described very well. The main thing is to solder the outer connections of the shield and the 2x3 shields at the bottom so it can connect to the SPI of the arduino. Only the jumper J1 has to be sticked. The wiring of the cable is described at https://code.google.com/p/railuino/ (errata table on the left).
Just in case i copied the table to this instruction 

| Signal     | RJ45    | Mini-DIN  | Color         |
| ---------- |:-------:| ---------:| -------------:|
| CAN_H      | 1       | 4         | Orange-white  |
| CAN_L      | 2       | 8         | Orange        |
| GND        | 7       | 2         | Brown-white   |
| 12V        | 8       | 1         | Brown         |

After assembly test the Shield and it's wiring with the sniffer sketch included in the examples of the Railuino library.

#### S88 Arduino
The S88 Arduino Sketch is based on the Railuino library as well. The here included library contains some modifications so that the initial states and subsequent changes are written to the Serial bus. The wiring is explained on presentation slides of Railuino:
https://code.google.com/p/railuino/downloads/detail?name=2012-05-16-Railuino-Extended-Edition.pdf&can=2&q=

##### RFID-Reader
I use the same Arduino for the S88 readings and also for an RFID sensor. A good choice is the ID-20 which is available at Sparkfun (https://www.sparkfun.com/products/11828). I use it to identify my rolling stock at one point ni the model railway layout. Each trains contains an RFID-chip somewhere which tag is read out by the ID-20 and then supplied to the Arduino from which it is passed on to the SRCP-server. Right now the tag is then broadcasted with an undocumented `100 INFO RFID XX` broadcast.


### Software
After all wiring has been done connect the Arduinos to your PC and flash the appropriate sketch to each arduino (sketches are located in the ArduinoSketches folder).

#### Python Version and modules
The python script should run on Python >=3.4 and uses the module pySerial (https://pypi.python.org/pypi/pyserial) 

#### Running
Start the server in the "PythonSrcpServer" folder with the command
`python Railuino2Srcp.py`

#### Connecting to the server
The server implements the current 0.8.4 SRCP protocol which is specified over here: http://srcpd.sourceforge.net/srcp/
The server listens on port 4304.