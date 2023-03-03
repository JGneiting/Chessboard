#include "Arduino.h"
#include "MotorAxis.h"
#include <ezButton.h>

MotorAxis::MotorAxis(int enable, int direction, int step, int bumperLeft, int bumperRight) : 
enablePin(enable), directionPin(direction), stepPin(step), bumpLeftPin(bumperLeft), bumpRightPin(bumperRight), leftBumper(bumpLeftPin), rightBumper(bumpRightPin)
{
  pinMode(enablePin, OUTPUT);
  pinMode(directionPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
  // pinMode(bumpLeftPin, INPUT_PULLUP);
  // pinMode(bumpRightPin, INPUT_PULLUP);

  // Start the button loops
  leftBumper.loop();
  rightBumper.loop();

  minDelay = 2;
  targetDelay = minDelay;
  totalSteps = 0;
  currentSteps = 0;
  deltaSteps = 0;
  // debounce = 50;
  lastStep = millis();
  state = IDLE;
  axisDirection = LEFT;
  stepState = false;

  // leftButtonState = digitalRead(bumpLeftPin);
  // rightButtonState = digitalRead(bumpRightPin);

  homeAxis();
}

bool MotorAxis::getBusy()
{
  return state == IDLE;
}

void MotorAxis::setDirection(stepDirection direction)
{
  if (direction == LEFT)
  {
    axisDirection = LEFT;
    digitalWrite(directionPin, 0);
  }
  else
  {
    axisDirection = RIGHT;
    digitalWrite(directionPin, 1);
  }
}

bool MotorAxis::step()
{
  // Check to see if the proper time delta has passed
  if (millis() - lastStep >= targetDelay)
  {
    // We need to pulse the step pin, then change our internal step counter in the correct direction
    int delta = 1;
    if (axisDirection == LEFT)
    {
      delta = -1;
    }
    currentSteps = currentSteps + delta;
    stepState = !stepState;
    digitalWrite(stepPin, stepState);
    lastStep = millis();
    return true;
  }
  return false;
}

void MotorAxis::homeAxis()
{
  if (state == IDLE)
  {
    // We need to find the left bumper
    setDirection(LEFT);
    state = HOMING;
    targetDelay = 10;
  }
  else if (axisDirection == LEFT)
  {
      // Check to see if the button has been pressed
      if (leftBumper.isPressed())
      {
        currentSteps = 0;
        setDirection(RIGHT);
      }
  }
  else if (axisDirection == RIGHT)
  {
    // Check to see if we have hit the right bumper
    if (rightBumper.isPressed())
    {
      totalSteps = currentSteps;
      state = IDLE;
    }
  }
  else
  {
    step();
  }
}

void MotorAxis::moveRelative(float percent, float delay=0)
{
  // Make sure we are in an idle state
  if (state == IDLE)
  {
    targetDelay = max(delay, minDelay);

    // Calculate what step value we need to arrive to
    int target = round(1.0 * totalSteps * percent);

    // Determine the step delta from where we currently are and properly set the direction pin
    int delta = target - currentSteps;
    if (delta < 0)
    {
      delta = abs(delta);
      setDirection(LEFT);
    }
    else if (delta > 0)
    {
      setDirection(RIGHT);
    }
    else
    {
      return;
    }

    deltaSteps = delta;
    state = STEPPING;
  }
}

void MotorAxis::move()
{
  if (deltaSteps > 0)
  {
    if (step());
    {
      --deltaSteps;
    }
  }
  else
  {
    state = IDLE;
  }
}

void MotorAxis::update()
{
  switch (state)
  {
    case HOMING:
    {
      homeAxis();
      break;
    }
    case STEPPING:
    {
      move();
      break;      
    }
  }  
}
