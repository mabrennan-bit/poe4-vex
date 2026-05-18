# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       Mallory Brennan and Dan Lutz                                               #
# 	Created:      5/6/2026, 1:20:25 PM                                         #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

# Brain should be defined by default
brain=Brain()

# --------------- Robot Configuration --------------------------------------------------------
rightMotor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)   # Right drive train motor
leftMotor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)     # Left drive train motor
liftMotor = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)    # Lift motor
inertial_1 = Inertial(Ports.PORT5)                               # Inertial sensor
liftArmRotation = Rotation(Ports.PORT6, False)                   # Liftarm rotation sensor
bumpSwitch = Bumper(brain.three_wire_port.a)                     # Bumper switch
# ---------------------------------------------------------------------------------------------

# --------------- Helper Functions ------------------------------------------------------------
def bump():
    """
    Hold the programs's execution until the button is pressed.
    """

    while(bumpSwitch.pressing() == False):
        wait(10, MSEC)  #Debounce the button

        brain.screen.set_cursor(1,1)    # Place cursor in row 1, col 1
        brain.screen.print("Press the button to start the program")
        pass
    brain.screen.clear_line(1)
    brain.screen.set_cursor(1,1)
    brain.screen.print("Program executed")
    wait(1, SECONDS)

def inertialCalibration():
    """
    1. Calibrate inertial sensor
    2. Include 2 second wait time for calibration
    3. Ca;; tis function as th estart of the program's execution
    """

    brain.screen.clear_screen
    brain.screen.set_cursor(1,1)
    brain.screen.print("Calibrating the inertial sensor")
    brain.screen.set_cursor(2,1)
    brain.screen.print("Don't move the robot!")
    inertial_1.calibrate()  # Calibrate the inertial sensore

    wait(2, SECONDS)

    brain.screen.set_cursor(1,1)
    brain.screen.clear_line(1)
    brain.screen.print("Inertial calibration complete.")

def testInertial():
    """
    1. Test the inertial sensor by having it display heading and rotation data
    2. Press the button to end the test
    """

    brain.screen.clear_screen()
    while(bumpSwitch.pressing() == False):
        wait(10, MSEC)  # Debounce the button
        brain.screen.set_cursor(5,1)
        brain.screen.print("Heading: " + str(inertial_1.heading()))
        brain.screen.set_cursor(6,1)
        brain.screen.print("Rotation: " + str(inertial_1.rotation()))
        brain.screen.set_cursor(8,1)
        brain.screen.print("Press the button to end the test.")

def driveStraightData(e):
    """
    1. Report position, rotation, and error
    2. Parameter: e = error value (setpoint - rotation)
    """

    brain.screen.set_cursor(1,1)
    brain.screen.print("Position: " + str(leftMotor.position()))      # Return current encoder count

    brain.screen.set_cursor(1,1)
    brain.screen.print("Rotation: " + str(inertial_1.rotation()))     # Return current rotation count

    brain.screen.set_cursor(1,1)
    brain.screen.print("Erorr: " + str(e))                            # Return current error count

def stopMotors():
    """
    Stop both motors at same time
    """

    rightMotor.stop()
    leftMotor.stop()
    wait(0.5, SECONDS)  # Wait 0.5 seconds for the system to stabilize

def driveStraight(distance, setpoint, motorVelocity):
    """
    1. distance = distance in inches
    2. setpoint = 0-degrees for driving straight
    3. motorVelocity = nomial motor velocity (+) => Forward, (-) => Reverse
    """ 

    inertial_1.reset_rotation() # Reset the rotation value before taking action

    kP = 0.3   # Proportional constant for driving straight
                # Used calculate the correction to maintain course
                # If too small, correction will occur too slowly
                # If too large, over-corretcion will occur
                # Determine best value by iteratively testing

    wheelDiameter = 4   # 4" Wheel diameter
    wheelCircumference = wheelDiameter * math.pi    # Wheel circumference

    # Convert the distance in ches to distance in "ticks"
    # distance (ticks) = (distance in inches / Wheel Circumference) * 360
    distance = (distance / wheelCircumference) * 360

    # Reset motor encoders
    leftMotor.set_position(0, DEGREES)
    rightMotor.set_position(0, DEGREES)

    # Drive forward if motor velocity > 0
    if (motorVelocity > 0):
        # while loop to track distance traveled
        while(leftMotor.position() < distance):
            error = (setpoint - inertial_1.rotation())  # Error
            correction = kP * error                     # Motor velocity correction

            # Correct motor velocities
            # If error > 0 (Setpoint > rotation) => drifting left
            # If error < 0 (Setpoint < rotation) => drifting right

            leftMotor.set_velocity((motorVelocity + correction), PERCENT)
            rightMotor.set_velocity((motorVelocity - correction), PERCENT)

            # Spin the motors
            leftMotor.spin(FORWARD)
            rightMotor.spin(FORWARD)


            driveStraightData(error)       # Display position, rotation, and error
        
        stopMotors()                       # Stop both motors when desired distance is reached
    
    else:
        # while loop to track distance traveled
        distance *= -1  # distance = distance * -1
        while(leftMotor.position() > distance):
            error = (setpoint - inertial_1.rotation())  # Error
            correction = kP * error                     # Motor velocity correction

            # Correct motor velocities
            # If error > 0 (Setpoint > rotation) => drifting left
            # If error < 0 (Setpoint < rotation) => drifting right

            leftMotor.set_velocity((motorVelocity + correction), PERCENT)
            rightMotor.set_velocity((motorVelocity - correction), PERCENT)

            # Spin the motors
            leftMotor.spin(FORWARD)
            rightMotor.spin(FORWARD)


            driveStraightData(error)       # Display position, rotation, and error
        
        stopMotors()                       # Stop both motors when desired distance is reached

# --------------------------------------------------------------------------------------------
# --------------- Define Main ----------------------------------------------------------------
def main():
    """
    The main() function is the program that is executed by the Brain
    """

    bump()                  # Call the bump() function to begin program execution 
    inertialCalibration()   # Calibarte the inertial sensor

    driveStraight(90, 0, 50) # Call driveStraight with neccessary parameters

# --------------- Call Main ------------------------------------------------------------------
main()  