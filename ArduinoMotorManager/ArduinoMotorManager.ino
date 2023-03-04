#include <Arduino.h>
#include "MotorAxis.h"

MotorAxis xAxis(14, 15, 16, 12, 11);
MotorAxis yAxis(18, 19, 3, 9, 8);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); 
  xAxis.setup();
  yAxis.setup(); 
}

void loop() {
  // We need to block until we receive a command from the serial interface
  if (Serial.available() > 0)
  {
    int delim;
    int commandDelim;
    String commandString = Serial.readStringUntil('\n');
    // Serial.println(commandString);
    do
    {
    commandDelim = commandString.indexOf('|');
    String line = commandString.substring(0, commandDelim);
    commandString = commandString.substring(commandDelim+1);
    // Serial.println(commandString);
    delim = line.indexOf(' ');
    String command = line.substring(0, delim);
    // Serial.println(" ACK");

    if (command == "HOME")
    {
      xAxis.homeAxis();
      yAxis.homeAxis();
    }
    else if (command == "MV")
    {
      float xPercent;
      float yPercent;
      float xDelay;
      float yDelay;
      String arguments = line.substring(delim+1);
      delim = arguments.indexOf(' ');
      xPercent = atof(arguments.substring(0, delim).c_str());

      arguments = arguments.substring(delim+1);
      delim = arguments.indexOf(' ');
      yPercent = atof(arguments.substring(0, delim).c_str());

      arguments = arguments.substring(delim+1);
      delim = arguments.indexOf(' ');
      xDelay = atof(arguments.substring(0, delim).c_str());

      yDelay = atof(arguments.substring(delim+1).c_str());

      xAxis.moveRelative(xPercent, xDelay);
      yAxis.moveRelative(yPercent, yDelay);
    }

    while (xAxis.getBusy() || yAxis.getBusy())
    {
      xAxis.update();
      yAxis.update();
    }
    } while (commandDelim >= 0);

    Serial.println(" READY");
  }

}
