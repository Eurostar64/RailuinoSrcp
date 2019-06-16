#include "TrackMessage.h"

TrackMessage message;
TrackController ctrl;


int counter = 1;


void setup()
{
  Serial.begin(115200);
  ctrl.setDebugging(true);
    ctrl.begin();
}


void loop()
{
    if(ctrl.receiveMessage(message)){
      counter++;
    }

    if(counter % 20 == 0){
        Serial.println("sending power off command");

        message.clear();
        message.command = 0x00;
        message.length = 0x05;
        message.data[4] = 0x00;

        ctrl.sendMessage(message);       
    }

}
