#################### LIBRARIES IMPORTATION #############################
from stm32_alphabot_v2 import AlphaBot_v2   # Alphabot 
from bluetooth import BLE                   # BLE control
from stm32_ble_uart import UART_BLE         # BLE control
from stm32_nec import NEC_8                 # IR control
from stm32_ssd1306 import SSD1306_I2C       # OLED
from pyb import LED                         # LED
 
#################### CONSTANT VARIABLES ################################
# Customizable values
DEFAULT_SPEED       = 40           # Robot's default speed in percent
MEDIUM_SPEED        = 25           # Robot's medium speed in percent
SLOW_SPEED          = 15           # Robot's slow speed in percent
LONG_DISTANCE       = 30           # Long obstacle's distance
MEDIUM_DISTANCE     = 20           # Medium obstacle's distance
SHORT_DISTANCE      = 10           # Short obstacle's distance
LINE_THRESHOLD      = 700          # Threshold for the line detection
ROBOT_NAME          = "Skynet"     # Name of the robot
 
# IR codes for the remote control buttons
IR_CODE_BTN_PLUS = 21
IR_CODE_BTN_PREV = 68
IR_CODE_BTN_PLAY = 67
IR_CODE_BTN_CH   = 70
IR_CODE_BTN_NEXT = 64
 
# OLED size
OLED_HEIGHT = 64
OLED_WIDTH = 128
 
# Obstacle detection codes
OBSTACLE_RIGHT   = 'R'
OBSTACLE_LEFT    = 'L'
OBSTACLE_NOWHERE = 'N'
OBSTACLE_BOTH    = 'B'
 
# Control modes
MODE_BLE  = "BLE"
MODE_IR   = "IR"
MODE_LINE = "Line"
 
#################### FUNCTIONS #########################################
def line_follow():
    '''
    This function is designed to control a robot to follow a line using infrared (IR) sensors. The robot
    has five IR sensors positioned in a row. The function reads the values from these sensors to determine
    the robot's movement direction based on the line's position relative to the sensors.

    Steps:
        Step 1 : Reading Sensor Values
            The function reads the values from the five IR sensors.
        
        Step 2 : Decision Making
            * Move Forward: If the third sensor (IR3) detects the line (value below LINE_THRESHOLD), the robot
              moves forward at a medium speed.
            * Turn Left: If the first (IR1) or second (IR2) sensor detects the line, the robot turns left at a
              slow speed.
            * Turn Right: If the fourth (IR4) or fifth (IR5) sensor detects the line, the robot turns right at
              a slow speed.
            * Move Backward: If none of the sensors detect the line, the robot moves backward at a slow speed.

        Key Variables:
            * LINE_THRESHOLD: The threshold value to determine if a sensor is above the line.
            * MEDIUM_SPEED: The speed at which the robot moves forward.
            * SLOW_SPEED: The speed at which the robot turns or moves backward.
    
    By following these steps, the function ensures the robot adjusts its direction to stay on the line based on
    the sensor readings.
    '''
    # YOUR CODE HERE
 
def remote_callback(data, addr, cmd):
    '''
    This function handles remote control commands received by the robot. It interprets the data from the remote
    and executes corresponding actions based on the current mode of operation.

    Parameters:
        * data: The data received from the remote control, representing the button pressed.
        * addr: The address from which the data is received (not used in this function).
        * cmd: The command type (not used in this function).
    
    Steps:
        Step 1 : Mode Check
            The function first checks if the robot is in infrared (IR) mode by comparing current_mode with
            MODE_IR.
        
        Step 2 : Command Handling
            * Move Forward: If the data matches IR_CODE_BTN_CH, the robot moves forward at the default speed.
            * Move Backward: If the data matches IR_CODE_BTN_PLUS, the robot moves backward at a medium speed.
            * Turn Left: If the data matches IR_CODE_BTN_PREV, the robot turns left at a medium speed.
            * Turn Right: If the data matches IR_CODE_BTN_PLAY, the robot turns right at a medium speed.
            * Stop: If the data matches IR_CODE_BTN_NEXT, the robot stops.
    
    Key Variables:
        * current_mode: The current operational mode of the robot.
        * MODE_IR: The constant representing infrared mode.
        * IR_CODE_BTN_CH, IR_CODE_BTN_PLUS, IR_CODE_BTN_PREV, IR_CODE_BTN_PLAY, IR_CODE_BTN_NEXT: Constants
        * representing the codes for specific buttons on the remote control.
        * DEFAULT_SPEED: The default speed at which the robot moves forward.
        * MEDIUM_SPEED: The speed at which the robot moves backward, turns left, or turns right.
    
    By following these steps, the function ensures the robot responds appropriately to remote control commands
    when in IR mode.
    '''
    # YOUR CODE HERE
 
def OLED_write(line_1, line_2, line_3):
    '''
    This function is designed to display text on an OLED screen. It takes three lines of text as input and
    positions them appropriately on the screen before rendering them.

    Parameters:
        * line_1: The text to be displayed on the first line.
        * line_2: The text to be displayed on the second line.
        * line_3: The text to be displayed on the third line.
    
    Steps:
        Step 1 : Screen Erasure
            The function begins by clearing the OLED screen.
    
        Step 2 : Text Positioning and Display
            * First Line: The text from line_1 is displayed at the top-left corner of the screen (coordinates (0, 0)).
              It is intended to be printed in yellow.
            * Second Line: The text from line_2 is positioned at least 17 pixels below the first line, starting at coordinates (0, 17).
            * Third Line: The text from line_3 is positioned at least 10 pixels below the second line, starting at coordinates (0, 27).
    
        Step 3 : Screen Update
            Finally, the function updates the display to show the new content.

    By following these steps, the function ensures that the provided text is displayed neatly on the OLED screen with proper spacing.
    '''
    # YOUR CODE HERE
 
def update_LEDs_and_OLED():
    if current_mode == MODE_BLE:
        blue_led.on()   # LED BLUE ON
        red_led.off()   # LED RED OFF
        green_led.off() # LED GREEN OFF
        OLED_write("BLE mode", "Use the app on", "the phone.")
    elif current_mode == MODE_IR:
        blue_led.off()  # LED BLUE OFF
        red_led.on()    # LED RED ON
        green_led.off() # LED GREEN OFF
        OLED_write("IR mode", "Use the remote", "controller.")
    elif current_mode == MODE_LINE:
        blue_led.off()  # LED BLUE OFF
        red_led.off()   # LED RED OFF
        green_led.on()  # LED GREEN ON
        OLED_write("Line mode", "Put the robot", "on the line.")
        
def avoid_obstacle():
    distance = 0
    # Stop the robot while we are deciding what the next move will be
    my_robot.stop()     
    # Try to see the obstacle with the IR sensors
    ir_sensor = my_robot.readInfrared()
    # If the obstacle is at the right
    if ir_sensor == OBSTACLE_RIGHT:
        # Turn left until there is no more obstacle in the way
        while(distance < MEDIUM_DISTANCE):
            distance = my_robot.readUltrasonicDistance()  
            my_robot.turnLeft(MEDIUM_SPEED)
    # If the obstacle is in front of the robot or at its left
    elif ir_sensor == OBSTACLE_BOTH or ir_sensor == OBSTACLE_LEFT:
        # Turn right until there is no more obstacle in the way
        while(distance < MEDIUM_DISTANCE):
            distance = my_robot.readUltrasonicDistance()  
            my_robot.turnRight(MEDIUM_SPEED)
    # If the obstacle is not detected by the IR sensors yet, move forward very slow
    else:
        my_robot.moveForward(SLOW_SPEED)
        
def ble_remote(ble_data):
    ## FORWARD
    if ble_data == "F pressed":
        # Read the ultrasonic distance
        distance = my_robot.readUltrasonicDistance()
        # If an obstacle is very close, avoid it
        if distance < SHORT_DISTANCE:
            avoid_obstacle()
        # If there is an obstacle not far from the robot, move slower
        elif distance < MEDIUM_DISTANCE:
            my_robot.moveForward(MEDIUM_SPEED)     
        # If there is no obstacle, move forward at the default speed
        else:
            my_robot.moveForward(DEFAULT_SPEED)
    ## BACKWARD
    elif ble_data == "B pressed":
        my_robot.moveBackward(MEDIUM_SPEED)
    ## LEFT 
    elif ble_data == "L pressed":
        my_robot.turnLeft(MEDIUM_SPEED)
    ## RIGHT
    elif ble_data == "R pressed":
        my_robot.turnRight(MEDIUM_SPEED)
    ## STOP    
    else:
        my_robot.stop()
 
#################### INITALIZATION #####################################
# Create the robot object
my_robot = AlphaBot_v2()
 
# Create the IR object for the communication with the remote control
my_remote_controler = NEC_8(my_robot.pin_IR, remote_callback)
 
# Create the BLE objects for the communication with the phone
ble = BLE()
uart = UART_BLE(ble, name=ROBOT_NAME)
 
# Create an OLED object that will communicate by I2C
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, my_robot.i2c, addr=my_robot.getOLEDaddr())
 
# Create the LEDs objects
red_led = LED(1)
green_led = LED(2)
blue_led = LED(3)
 
# Initialize the global variables
current_mode = MODE_BLE
ble_data = "S pressed"
 
#################### INFINITE LOOP #####################################
while True:
    # If we received something from the phone
    if uart.any():
        # Read the data and decode it
        ble_data = uart.read().decode().replace("\x00", "")
        
        # If the data is a mode change
        if "Mode" in ble_data:
            # Update the mode
            current_mode = ble_data.replace("Mode ", "")
            update_LEDs_and_OLED()
 
 
    ### MODE LINE FOLLOWING ###
    if current_mode == MODE_LINE:
        line_follow()
        
    ### MODE BLE REMOTE ###    
    elif current_mode == MODE_BLE:
        ble_remote(ble_data)
