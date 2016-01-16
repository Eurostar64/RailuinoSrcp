/*********************************************************************
 * Railuino - Hacking your Märklin
 *
 * Copyright (C) 2012 Joerg Pleumann
 * Adapted oct 2013 Bert Havinga
 * 
 * This example is free software; you can redistribute it and/or
 * modify it under the terms of the Creative Commons Zero License,
 * version 1.0, as published by the Creative Commons Organisation.
 * This effectively puts the file into the public domain.
 *
 * This example is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * LICENSE file for more details.
 */

#include <Railuino.h>
#include <SoftwareSerial.h>

TrackController ctrl(0x0000, false);

TrackMessage message;

// RocRail sends always 13 bytes
char sbuffer[13];
byte rbuffer[13];

int i;

void setup() {
  Serial.begin(500000);
  while (!Serial);
  ctrl.begin();
  Serial.setTimeout(20);
}

void loop() {
  
  if (ctrl.receiveMessage(message)) {
    
    rbuffer[0] = ((message.command >> 7) & 0x01);
    rbuffer[1] = ((message.command  & 0x7F) << 1);
    rbuffer[1] |= (message.response & 0x01);
    rbuffer[2] = ((message.hash >> 8) & 0x00ff);
    rbuffer[3] = (message.hash & 0x00ff);
    rbuffer[4] = message.length;
    for (int i = 0; i < message.length; i++) {
      rbuffer[i+5] = message.data[i];
    }
    for (int i=8; i> message.length; i--) {
      rbuffer[i+4] = 0;
    }  
    
    Serial.write(rbuffer, 13);
  }
  

  if (Serial.available()) {
      if (Serial.readBytes(sbuffer, 13) == 13) {
     
      message.clear();
      message.command = (sbuffer[0] << 7);
      message.response = (sbuffer[1] & 0x01);
      message.command |= ((sbuffer[1] & 0xFE) >> 1);
      message.hash = ctrl.getHash();
      message.length = sbuffer[4];
      for (int i=0; i < 8; i++) {
         message.data[i] = sbuffer[i+5];
      } 
      //Serial.println(message);
      //ctrl.exchangeMessage(message, message, 1000);
      ctrl.sendMessage(message);
      
      
    }
  }
}