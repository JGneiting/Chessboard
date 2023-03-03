#ifndef MotorAxis_h
#define MotorAxis_h
#include "Arduino.h"
#include <ezButton.h>

enum stepDirection {LEFT, RIGHT};
enum axisState {HOMING, STEPPING, IDLE};

class MotorAxis
{
public:
  MotorAxis(int enable, int direction, int step, int bumperLeft, int bumperRight);
  ~MotorAxis() = default;

  void homeAxis();
  void moveRelative(float percent, float delay=0);
  bool getBusy();
private:
  int totalSteps;
  int currentSteps;
  int deltaSteps;
  long lastStep;
  // int debounce;
  int minDelay;
  int targetDelay;
  float deltaTime;

  int enablePin;
  int directionPin;
  int stepPin;
  int bumpLeftPin;
  int bumpRightPin;

  // int leftBumperState;
  // int rightBumperState;
  ezButton leftBumper;
  ezButton rightBumper;

  axisState state;
  stepDirection axisDirection;
  bool stepState;

  void move(); 
  void setDirection(stepDirection direction);
  bool step();
  void update();
};

#endif