import RPi.GPIO as GPIO
import time

CLK = 11
MISO = 9
MOSI = 10
CS = 8

PIN_SERVO = 4
PULSE_FREQ = 50
DUTY_CYCLE = 2

MS100 = 0.1
MS200 = 0.2
MS300 = 0.3
MS500 = 0.5
MS1000 = 1.0
MS2000 = 2.0
MS3000 = 3.0
MS5000 = 5.0


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

def setupSpiPins(clkPin, misoPin, mosiPin, csPin):
    ''' Set all pins as an output except MISO (Master Input, Slave Output)'''
    GPIO.setup(clkPin, GPIO.OUT)
    GPIO.setup(misoPin, GPIO.IN)
    GPIO.setup(mosiPin, GPIO.OUT)
    GPIO.setup(csPin, GPIO.OUT)
     

def readAdc(channel, clkPin, misoPin, mosiPin, csPin):
    if (channel < 0) or (channel > 1):
        print ("Invalid ADC Channel number, must be between [0,7]")
        return -1
        
    # Datasheet says chip select must be pulled high between conversions
    GPIO.output(csPin, GPIO.HIGH)
    
    # Start the read with both clock and chip select low
    GPIO.output(csPin, GPIO.LOW)
    GPIO.output(clkPin, GPIO.HIGH)
    
    # read command is:
    # start bit = 1
    # single-ended comparison = 1 (vs. pseudo-differential)
    # channel num bit 2
    # channel num bit 1
    # channel num bit 0 (LSB)
    #read_command = 0x18
   
    #print("command: ", read_command)
    #sendBits(read_command, noBits, clkPin, mosiPin)
    
    adcValue = recvBits(10, clkPin, misoPin)
    
    # Set chip select high to end the read
    GPIO.output(csPin, GPIO.HIGH)
  
    return adcValue

def recvBits(numBits, clkPin, misoPin):
    '''Receives arbitrary number of bits'''
    retVal = 0
    
    for bit in range(numBits):
        # Pulse clock pin 
        GPIO.output(clkPin, GPIO.HIGH)
        GPIO.output(clkPin, GPIO.LOW)
        
        # Read 1 data bit in
        if GPIO.input(misoPin):
            retVal |= 0x1
        
        # Advance input to next bit
        retVal <<= 1
    
    # Divide by two to drop the NULL bit
    return (retVal/2)


def driveServo():
    set_angle(servo, 180)
    time.sleep(MS500)
    set_angle(servo, 0)
    time.sleep(MS500)
    set_angle(servo, 180)
    time.sleep(MS500)
    
try:
    servo = setup_servo(PIN_SERVO, PULSE_FREQ) # 50 Hz pulse
    setupSpiPins(CLK, MISO, MOSI, CS)
    time.sleep(MS500)
    while True:
        # Setup servo pin
        #driveServo()
        
        adcValue = readAdc(0, CLK, MISO, MOSI, CS)
        print("adc: ", adcValue)
        time.sleep(0.5)
except:
    servo.stop()
    GPIO.cleanup()
    print("clean up")

