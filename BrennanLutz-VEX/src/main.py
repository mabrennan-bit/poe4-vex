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
    brain.screen.clear_line(1,1)
    brain.screen.print("Inertial calibration complete.")
# --------------- Define Main ----------------------------------------------------------------
def main():
    """
    The main() function is the program that is executed by the Brain
    """

    bump() # Call the bump() function to begin program execution 
# --------------- Call Main ------------------------------------------------------------------
main()
