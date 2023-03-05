#ifndef MotorAxis_h
#define MotorAxis_h
#include "Arduino.h"
// #include <ezButton.h>

enum stepDirection {LEFT, RIGHT};
enum axisState {HOMING, STEPPING, IDLE};

class MotorAxis
{
public:
  MotorAxis(int direction, int step, int enable, int bumperLeft, int bumperRight);
  ~MotorAxis() = default;

  void homeAxis();
  void setup();
  void moveRelative(float percent, unsigned long delay=0);
  bool getBusy();
  void update();
private:
  long totalSteps;
  long currentSteps;
  long targetSteps;
  unsigned long lastStep;
  unsigned long minDelay;
  unsigned long targetDelay;

  int enablePin;
  int directionPin;
  int stepPin;
  int bumpLeftPin;
  int bumpRightPin;

  // int leftBumperState;
  // int rightBumperState;
  // ezButton leftBumper;
  // ezButton rightBumper;

  axisState state;
  stepDirection axisDirection;
  bool stepState;

  void move(); 
  void setDirection(stepDirection direction);
  bool step();
};

#endif