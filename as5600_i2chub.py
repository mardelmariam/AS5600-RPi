'''

Using a TCA9548A I2C multiplexer to handle multiple AS5600 boards

'''

import time, smbus, RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Hardware constraints
I2C_BUS = 1
I2C_MUX_ADDR = 0x70 # TCA9548A address
I2C_MUX_DEVICE = 0x04 # It should be 0x1, 0x2, 0x4, and so on
AS5600_I2C_ADDR = 0x36
RESET_PIN = 4

"""

A reset pin is added. Sometimes, when using TCA9548A with 
motors, these ICs's freeze. Then, a reset before reading values
should help you execute any instruction you need

"""

# Configuration registers
# Refer to datasheet, page 19, for more details
# 0x07 - CONF - XX - WD - FTH(2:0) - SF(1:0)
# 0x08 - CONF - PWMF(1:0) - OUTS(1:0) - HYST(1:0) - PM(1:0)

# Output registers
# 0x0C / 0x0D - RAW_ANGLE(11:8) and RAW_ANGLE(7:0)
# 0x0E / 0x0F - ANGLE(11:8) and ANGLE(7:0)

# Status registers
# 0x0B - STATUS - MD(5), ML(4), MH(3)
# 0x1A - AGC - 8-bit
# 0x1B / 0x1C - MAGNITUDE(11:8) and MAGNITUDE(7:0)

AS5600_CONF_REG_ADDR = 0x07
AS5600_RAW_ANGLE_REG_ADDR = 0x0C 
AS5600_STATUS_REG_ADDR = 0x0B

#AS5600_CONF_BYTE1 = '1-100-001-1'
#AS5600_CONF_BYTE2 = '001-0-0-0-11'
AS5600_CONF_BYTE1 = 0b00000000
AS5600_CONF_BYTE2 = 0b00000001

# Auxiliary functions
def configureAS5600():
    GPIO.setup(RESET_PIN, GPIO.OUT)
    GPIO.output(RESET_PIN, True)
    time.sleep(0.1)
    GPIO.output(RESET_PIN, False)
    time.sleep(0.1)
    GPIO.output(RESET_PIN, True)
    time.sleep(0.1)
    BUS.write_byte_data(I2C_MUX_ADDR, 0x00, I2C_MUX_DEVICE)
    BUS.write_byte_data(AS5600_I2C_ADDR, AS5600_CONF_REG_ADDR, AS5600_CONF_BYTE1)
    time.sleep(0.01)
    BUS.write_byte_data(AS5600_I2C_ADDR, AS5600_CONF_REG_ADDR+1, AS5600_CONF_BYTE2)
    time.sleep(0.01)
    
def readRawAngle():
    byte1 = BUS.read_byte_data(AS5600_I2C_ADDR, AS5600_RAW_ANGLE_REG_ADDR)
    byte2 = BUS.read_byte_data(AS5600_I2C_ADDR, AS5600_RAW_ANGLE_REG_ADDR+1)
    print(str(byte1*256 + byte2))
    
def checkMagnet():
    byte = BUS.read_byte_data(AS5600_I2C_ADDR, AS5600_STATUS_REG_ADDR)
    byte = byte & 0x38
    if byte == 0x20: # Magnet is properly placed
        return True
    else:
        return False

# Open I2C device
BUS = smbus.SMBus(I2C_BUS)
BUS.open(I2C_BUS)    

# Configure AS5600 operation
configureAS5600()

# Data acquisition
while True:
    if checkMagnet():
        readRawAngle()
    time.sleep(0.1)
