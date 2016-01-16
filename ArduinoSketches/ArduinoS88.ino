#include <Railuino.h>

TrackReporterS88 rprt(4);

void setup()
{
  //because RFID is 9600 we can't change baudrate !!!!
   Serial.begin(9600);
  while(!Serial);
  
}

char val = 0;

void loop()
{
  //S88
  //refresh S88 values (done in TrackReporter)
 rprt.refresh();
  //RFID
  if(Serial.available() > 0)
  {
    Serial.print("RFID#");
    //delay needed to read the full rfid tag into buffer
    delay(50);
    while(Serial.available())
    {
      //this Serial is the one from Rfid
      val = Serial.read();
      //to prevent printing a new line char
      //the Serial we're using is the one connected to the PC
      if(val != 10 && val != 32)
        Serial.print(val);
    }
    Serial.println("#RFID");
  }
}
