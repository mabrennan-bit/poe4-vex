# ---------------------------------------------------------------------------- 
#                                                                              
# 	Module:       main.py                                                      
# 	Author:       Mallory Brennan and Dan Lutz                                   
# 	Created:      5/6/2026, 1:20:25 PM                                         
# 	Description:  V5 project                                                   
#                                                                              
# ---------------------------------------------------------------------------- 

import math

from vex import *

# Brain should be defined by default
brain = Brain()

# -------------------------------------------- Robot Configuration --------------------------------------------
rightMotor = Motor(Ports.PORT7, GearSetting.RATIO_18_1, False)  # Right drivetrain motor
leftMotor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)    # Left drivetrain motor
liftMotor = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)   # Lifearm motor
inertial_1 = Inertial(Ports.PORT5)                              # Inertial sensor
bumpSwitch = Bumper(brain.three_wire_port.a)                    # Bumper switch
# --------------------------------------------------------------------------------------------------------------


# -------------------------------------------- Helper Functions --------------------------------------------
def bump():
    """
    Hold the program's execution until the button is pressed
    """

    while bumpSwitch.pressing() == False:
        wait(10, MSEC)  # Debounce the button (10 ms)

        brain.screen.set_cursor(1, 1)  # Place the cursor in upper left corner of the screen
        brain.screen.print("Press the button to start the program")
        pass

    brain.screen.clear_line(1)  # Clear the text row 1
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Program executed")
    wait(1, SECONDS)  # Wait 1 second before continuing


def intertialCalibration():
    """
    Calibrate the inertial sensor
    A wait time of 2 seconds is required
    This function should be called at the start of the program's execution
    """

    brain.screen.clear_screen()                             # Clear the brain's screen
    brain.screen.set_cursor(1, 1)                           # Place the cursor in upper left corner of the screen
    brain.screen.print("Calibrating the inertial sensor")
    brain.screen.set_cursor(2, 1)                           # Place cursor on row 2
    inertial_1.calibrate()                                  # Calibrate the inertial sensor

    wait(2, SECONDS)                                        # Wait for the calibration process to complete

    brain.screen.clear_line(1)
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Inertial calibration completed")


def testInertial():
    """
    Test the inertial sensor by having it display heading and total rotation
    data. Pressing the bump switch will end the test
    """

    brain.screen.clear_screen()  # Clear the brain's screen
    while bumpSwitch.pressing() == False:
        wait(10, MSEC)  # Debounce the button (10 ms)
        brain.screen.set_cursor(5, 1)
        brain.screen.print("Heading: " + str(inertial_1.heading()))
        brain.screen.set_cursor(6, 1)
        brain.screen.print("Rotation: " + str(inertial_1.rotation()))
        brain.screen.set_cursor(8, 1)
        brain.screen.print("Press the bump switch to exit")
    brain.screen.clear_line(8)
    brain.screen.set_cursor(8, 1)
    brain.screen.print("Inertial test terminated")
    
def driveStraightData(e): 
    """
    1. Report position, rotation and error values to the screen while driving
    2. Parameter: e = error value (setpoint - rotation)
    """

    brain.screen.set_cursor(1, 1)
    brain.screen.print("Position: " + str(leftMotor.position())) # Return the current motor count
    
    brain.screen.set_cursor(2, 1)
    brain.screen.print("Rotation: " + str(inertial_1.rotation())) # Return the current rotation value
    
    brain.screen.set_cursor(3, 1)
    brain.screen.print("Error: " + str(e)) # Return the current error

def stopMotors():
    rightMotor.stop()
    leftMotor.stop()
    wait(0.5, SECONDS) # Wait 0.5 seconds for the system to stabilize
    
def driveStraight(distance, setpoint, motorVelocity):
    """
    1. distance = distance to travel in inches
    2. setpoint = 0-degrees of rotation for driving straight
    3. motorVelocity = the velocity of the motors (+) => forward, (-) => reverse
    """
    
    inertial_1.reset_rotation() # Reset the rotation before each driving 
    
    # Set stopping mode for the motors
    leftMotor.set_stopping(COAST)
    rightMotor.set_stopping(COAST)

    kP = 0.33       # Proportional constant for driving straight
                    # used to calculate the correctionto maintain course
                    # If too small, correction will occur too slowly
                    # If too large, overcorrection will occur
                    # Determine best value by iteratively testing
                    
    wheelDiameter = 4 # Wheel diameter = 4 inches
    
    # Calculate the distance in terms of encoder ticks (1 tick = 1 degreee)
    #distance (ticks) = Distance in inches / Wheel circumference * 360 (degrees in one rotation)
     
    wheelCircumference = wheelDiameter * math.pi # Wheel circumeference
    distance = (distance / wheelCircumference) * 360 # Distance in ticks
     
     # Reset the motor encoder to zero before driving
    leftMotor.set_position(0, DEGREES)
    rightMotor.set_position(0, DEGREES)
    
    # Drive forward if motor velocity > 0
    if(motorVelocity > 0):
        # While loop to track the distance traveled
        while(leftMotor.position(DEGREES) < distance):
            error = (setpoint - inertial_1.rotation()) # Caculate error
            correction = kP * error                    # Motor velocity correction

            # Correct motor velocites
            # if error > 0 (setpoint > rotation) => drifting left
            # if error < 0 (setpoint < rotation) => drifting right
            
            leftMotor.set_velocity(motorVelocity + correction, PERCENT) 
            rightMotor.set_velocity(motorVelocity - correction, PERCENT)
            
            # Spin motors
            leftMotor.spin(FORWARD)
            rightMotor.spin(FORWARD)
            
            driveStraightData(error) # Display position, rotation, and error
    
        # Stop the motors when the desired distance is reached
        stopMotors()
        
    # Drive straight in reverse if motor velocity < 0
    else:
        
        distance *= -1 # distance = distance * -1
        # While loop to track the distance traveled
        while(leftMotor.position(DEGREES) > distance):
            error = (setpoint - inertial_1.rotation()) # Caculate error
            correction = kP * error                    # Motor velocity correction

            # Correct motor velocites
            # if error > 0 (setpoint > rotation) => drifting left
            # if error < 0 (setpoint < rotation) => drifting right
            
            leftMotor.set_velocity(motorVelocity + correction, PERCENT) 
            rightMotor.set_velocity(motorVelocity - correction, PERCENT)
            
            # Spin motors
            leftMotor.spin(FORWARD)
            rightMotor.spin(FORWARD)
            
            driveStraightData(error) # Display position, rotation, and error
    
        # Stop the motors when the desired distance is reached
        stopMotors()

def turnData(turnError, derivative):
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Heading: " + str(inertial_1.heading()))     # Return the heading 
    
    brain.screen.set_cursor(2, 1)
    brain.screen.print("Error: " + str(abs(turnError)))             # Return turning error
    
    brain.screen.set_cursor(3, 1)
    brain.screen.print("Derivative: " + str(abs(derivative)))       # Return the derivative

def pointTurn(setPoint):
    """
    1. Perform a point turn using the inertial sensor heading and propotional & derivative control
    2. Argument: Desired heading (setPoint) in degrees
    """

    brain.screen.clear_screen()         # Clear the screen

    # Set stopping mode for the left and right motors
    leftMotor.set_stopping(BRAKE)
    rightMotor.set_stopping(BRAKE)

    # Calculate the different between the setPoint and current heading
    # to determine the turning direction
    difference = setPoint - inertial_1.heading()

    # Want to turn the smallest amount to reach the desired heading 
    if (setPoint > inertial_1.heading()): # Setpoint > current heading
        if (abs(difference) <= 180):
            clockwise = True # Turn CW
        else:
            clockwise = False   # Turn CCW

        if (abs(difference) <= 180):
            clockwise = False   # Turn CCW
        else:
            clockwise = True    # Turn CW
    # Define kP and kD for CW and CCW turns
    if (clockwise): # Values for CW turn
        kP = 0.045
        kD = 0.00
    else:           # Values for CCW turn
        kP = 0.04
        kD = 0.00

    # Define maximum turning velocity and previous error term
    maxVelocity = 50    # Maximum turnign velocity
    previousError = 0.0 # Error from previous loop iteration

    while(True):
        turnError = setPoint - inertial_1.heading()  # Caluclate error
        derivative = turnError - previousError      # Current error - previous

        # Break out of loop and stop turning when setpoint is reached without osciliation
        if((abs(turnError)) < 1 and (abs(derivative) < 0.2)):
            stopMotors()        # Stop motors
            break               # Exit the while loop

        # Calculate the corection for the motor velocities
        turnCorrection = (kP * turnError) + (kD * derivative)

        # Limit the turn correction value to be between -1 and 1
        # This will keep the motor velocity <= maximum turn velocity
        if (abs(turnCorrection) > 1):
            turnCorrection = 1

        turnVelocity = maxVelocity * turnCorrection

        # Set the motor velocities based on the direction (CW or CCW)
        if(clockwise):  # Turning clockwise
            leftMotor.set_velocity(turnVelocity)
            rightMotor.set_velocity(-1 * turnVelocity)
        else:           # Turn counterclockwise
            leftMotor.set_velocity(-1 * turnVelocity)
            rightMotor.set_velocity(turnVelocity)

        # Spin the motors 
        leftMotor.spin(FORWARD)
        rightMotor.spin(FORWARD)

        turnData(turnError, derivative) # Print heading, error & derivative datat

        previousError = turnError       # Update prevoous error term
        wait(20, MSEC)

# -------------------------------------------- Main Function --------------------------------------------
def main():
    """
    The main() function is the program that will be executed by the brain
    """
    bump()  # call bump() to execute the program
    intertialCalibration()  # Calibrate the inertial sensor

    #driveStraight(84.2, 0, 50) # Call driveStaight() with distance, setpoint, and motor velocity parameters
   # wait(4, SECONDS) # Wait 4 seconds before executing the next command
    #driveStraight(84.2, 0, -50) # Call driveStaight() with distance, setpoint, and motor velocity parameters to drive in reverse

    pointTurn(224)
    wait(2, SECONDS)
    pointTurn(37)
    wait(2, SECONDS)
    pointTurn(135)
    wait(2, SECONDS)
# -------------------------------------------- Call main Function --------------------------------------------
main()