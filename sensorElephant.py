import time
import RPi.GPIO as GPIO

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

MS100 = 0.1
MS200 = 0.2
MS300 = 0.3
MS500 = 0.5
MS1000 = 1.0
MS2000 = 2.0
MS3000 = 3.0
MS5000 = 5.0


PIN_SERVO = 4
PULSE_FREQ = 50
DUTY_CYCLE = 2

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
# SPI_PORT   = 0
# SPI_DEVICE = 0
# mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

GPIO.setmode(GPIO.BCM)

def setup_servo(pin, pwmFreq):
    GPIO.setup(pin, GPIO.OUT)
    servo = GPIO.PWM(pin, pwmFreq)
    servo.start(0)
    return servo

def set_angle(servo, angle):

    dutyCycle = 2 + (float(angle) / 18)
    print(dutyCycle)
    servo.ChangeDutyCycle(dutyCycle) #Recalculate with values from datasheet of servo
    #time.sleep(MS200)
    #servo.ChangeDutyCycle(0)

def driveServo():
    set_angle(servo, 180)
    time.sleep(MS500)
    set_angle(servo, 0)
    time.sleep(MS500)
    set_angle(servo, 180)
    time.sleep(MS500)


# Main program loop.
    
try:
    
    
    
    servo = setup_servo(PIN_SERVO, PULSE_FREQ) # 50 Hz pulse

    while True:
        
        sensorValues = mcp.read_adc(0)
            
        #print(sensorValues)
        

        if sensorValue > 100:
            driveServo()
    
        #time.sleep(0.5)
            
except:
    servo.stop()
    GPIO.cleanup()
    print("clean up")
