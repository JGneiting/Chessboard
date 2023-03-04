#include "Arduino.h"
#include "MotorAxis.h"
// #include <ezButton.h>

MotorAxis::MotorAxis(int direction, int step, int enable, int bumperLeft, int bumperRight) : 
enablePin(enable), directionPin(direction), stepPin(step), bumpLeftPin(bumperLeft), bumpRightPin(bumperRight)
{

  minDelay = 25;
  targetDelay = minDelay;
  totalSteps = 0;
  currentSteps = 0;
  targetSteps = 0;
  lastStep = micros();
  state = IDLE;
  axisDirection = LEFT;
  stepState = false;

  // leftButtonState = digitalRead(bumpLeftPin);
  // rightButtonState = digitalRead(bumpRightPin);
}

void MotorAxis::setup()
{
  pinMode(enablePin, OUTPUT);
  pinMode(directionPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
  pinMode(bumpLeftPin, INPUT_PULLUP);
  pinMode(bumpRightPin, INPUT_PULLUP);

  digitalWrite(enablePin, 0);  

  // Start the button loops
  // leftBumper.loop();
  // rightBumper.loop();

  // homeAxis();
}

bool MotorAxis::getBusy()
{
  return state != IDLE;
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
  if (micros() - lastStep >= targetDelay)
  {
    // We need to pulse the step pin, then change our internal step counter in the correct direction
    if (axisDirection == LEFT)
    {
      currentSteps -= 1;
    }
    else
    {
      currentSteps += 1;
    }
    stepState = !stepState;
    digitalWrite(stepPin, stepState);
    lastStep = micros();
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
    targetDelay = 200;
  }
  else if (axisDirection == LEFT)
  {
    step();
      // Check to see if the button has been pressed
      if (digitalRead(bumpLeftPin) == 0)
      {
        currentSteps = 0;
        setDirection(RIGHT);
      }
  }
  else if (axisDirection == RIGHT)
  {
    step();
    // Check to see if we have hit the right bumper
    if (digitalRead(bumpRightPin) == 0)
    {
      totalSteps = currentSteps;
      state = IDLE;
    }
  }
}

void MotorAxis::moveRelative(float percent, unsigned long delay=0)
{
  // Make sure we are in an idle state
  if (state == IDLE)
  {
    if (percent < 0 || percent > 100)
    {
      return;
    }
    
    targetDelay = max(delay, minDelay);
    percent /= 100;

    // Calculate what step value we need to arrive to
    long target = round(1.0 * totalSteps * percent);
    targetSteps = target;

    // Determine the step delta from where we currently are and properly set the direction pin
    long delta = target - currentSteps;
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
 
    state = STEPPING;
  }
}

void MotorAxis::move()
{
  if (targetSteps != currentSteps)
  {
    step();
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
