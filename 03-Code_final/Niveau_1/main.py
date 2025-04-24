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
    ir1 = my_robot.TRSensors_readLine(sensor=1)
    ir2 = my_robot.TRSensors_readLine(sensor=2)
    ir3 = my_robot.TRSensors_readLine(sensor=3)
    ir4 = my_robot.TRSensors_readLine(sensor=4)
    ir5 = my_robot.TRSensors_readLine(sensor=5)
    
    # If IR3 is above the line
    if ir3 < LINE_THRESHOLD:
        my_robot.moveForward(MEDIUM_SPEED)
    # If IR1 or IR2 are above the line, turn left
    elif ir1 < LINE_THRESHOLD or ir2 < LINE_THRESHOLD:
        my_robot.turnLeft(SLOW_SPEED)
    # If IR4 or IR5 are above the line, turn right
    elif ir4 < LINE_THRESHOLD or ir5 < LINE_THRESHOLD:
        my_robot.turnRight(SLOW_SPEED)
    else:
        my_robot.moveBackward(SLOW_SPEED)
 
def remote_callback(data, addr, cmd):
    if current_mode == MODE_IR:
        if data == IR_CODE_BTN_CH:
            my_robot.moveForward(DEFAULT_SPEED)
        elif data == IR_CODE_BTN_PLUS:
            my_robot.moveBackward(MEDIUM_SPEED)
        elif data == IR_CODE_BTN_PREV:
            my_robot.turnLeft(MEDIUM_SPEED)
        elif data == IR_CODE_BTN_PLAY:
            my_robot.turnRight(MEDIUM_SPEED)
        elif data == IR_CODE_BTN_NEXT:
            my_robot.stop()
 
def OLED_write(line_1, line_2, line_3):
    # Erase the screen
    oled.fill(0)
    # The first line is at the top and will be printed in yellow
    oled.text(line_1, 0, 0)
    # The second line must be at least 17 pixels below
    oled.text(line_2, 0, 17)
    # The third line must be at least 8 pixels below, let's say 10
    oled.text(line_3, 0, 27)
    # Show the content of the screen
    oled.show()
 
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
