# RailuinoSrcp
A python program plus arduino sketches to connect your maerklin model railway to the computer and expose its functionality via the SRCP protocol

## Dependencies
The project builds up on two libraries:
* the great Railuino library of J. Pleumann which can be found here: https://code.google.com/p/railuino/
* the awesome CAN Bus Shield library of seeedstudio, which can be found here: https://github.com/Seeed-Studio/CAN_BUS_Shield

### Hardware needed
For this to work you need access to the Maerklin CAN-Bus which interconnects the Mobile Station, Boosters etc. The Railuino-Library on which this builds up is using the "TrackBox" (used alongside with the Mobile Station 2) and a special ArduinoShield to connect the Arduino to the CAN-Bus.
This project also offers the availability to include S88 feedbacks. The S88 bus is read on a second arduino device

#### Maerklin Mobile Station 2 and TrackBox
The MS2 is usually bundled with the trackbox. 

#### CAN Arduino Shield
There are multiple shields available to connect an Arduino to a CAN bus. In a first version of this librarry I used the watterott CANDiy shield, however I had multiple issues with it. So i decided to switch to the more widely used CAN Bus Shield by Seedstudio. You can get it here: https://www.seeedstudio.com/CAN-BUS-Shield-V2-p-2921.html

Wiring of the cable is a little bit complicated as the cable and connector isn't that easy to find. The table below shows the correct wiring. Usually you just need the CAN_H and CAN_L signals as GND and 12V is only required if the board should not be powered by the USB.

| Signal     | RJ45    | Mini-DIN  | Color         |
| ---------- |:-------:| ---------:| -------------:|
| CAN_H      | 1       | 4         | Orange-white  |
| CAN_L      | 2       | 8         | Orange        |
| GND        | 7       | 2         | Brown-white   |
| 12V        | 8       | 1         | Brown         |

#### S88 Arduino - UNDER CONSTRUCTION

With the new version this feature is again under construction..

The S88 Arduino Sketch is based on the Railuino library as well. The here included library contains some modifications so that the initial states and subsequent changes are written to the Serial bus. The wiring is explained on presentation slides of Railuino:
https://code.google.com/p/railuino/downloads/detail?name=2012-05-16-Railuino-Extended-Edition.pdf&can=2&q=

##### RFID-Reader - UNDER CONSTRUCTION

With the new version this feature is again under construction..

I use the same Arduino for the S88 readings and also for an RFID sensor. A good choice is the ID-20 which is available at Sparkfun (https://www.sparkfun.com/products/11828). I use it to identify my rolling stock at one point ni the model railway layout. Each trains contains an RFID-chip somewhere which tag is read out by the ID-20 and then supplied to the Arduino from which it is passed on to the SRCP-server. Right now the tag is then broadcasted with an undocumented `100 INFO RFID XX` broadcast.


### Software
* Import the 'CANTrackLib.zip' as a library to Arduino. 
* For testing you can use the 'CANGatewayDebug' sketch as it prints the content of each message as string to the serial bus
* To use it with the python server, please flash the other example sketch 'CANGatewayUDP' to the Arduino

#### Python Version and modules
The python script should run on Python >=3.4 and uses the module pySerial (https://pypi.python.org/pypi/pyserial) 

#### Running
Start the server in the "PythonSrcpServer" folder with the command
`python Railuino2Srcp.py <USB_COMPORT>`

#### Connecting to the server
The server implements the current 0.8.4 SRCP protocol which is specified over here: http://srcpd.sourceforge.net/srcp/
The server listens on port 4304.