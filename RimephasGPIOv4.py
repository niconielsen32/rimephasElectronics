import RPi.GPIO as GPIO
#import pygame
#import os
#from pushbullet import Pushbullet
import time
import threading
# Push Notification
# pb = Pushbullet('o.8ffn8GHVYRYPVFxMwYjE8xlHiZSPnH2G')
# print(pb.devices)

# Pins
PIN_MOTORDETECT = 24
PIN_TURNOFFDISPENSER = 25

# SPI Pins
PIN_CLK = 11
PIN_MOSI = 10
PIN_MISO = 9
PIN_CS = 8


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


#global variables
numberOfActivations = 0
irSensorThreshold = 30
ADCvalue = 0
dispenserEmptyTemp = 0
dispenserEmpty = False
turnOffDispenser = False
timeRunOut = False




def init_GPIO():
    # Init GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_TURNOFFDISPENSER, GPIO.OUT)
    GPIO.setup(PIN_MOTORDETECT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # Spi pins Init
    GPIO.setup(PIN_CLK, GPIO.OUT)
    GPIO.setup(PIN_MISO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PIN_MOSI, GPIO.OUT)
    GPIO.setup(PIN_CS, GPIO.OUT)


def setup_servo(pin, pwmFreq):
    GPIO.setup(pin, GPIO.OUT)
    servo = GPIO.PWM(pin, pwmFreq)
    servo.start(0)
    return servo

def set_angle(servo, angle):

    dutyCycle = 2 + (float(angle) / 18)
    #print(dutyCycle)
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
    
    

# Read SPI data from ADC
     
def recvBits(numBits, clkPin, misoPin):
    #Receives arbitrary number of bits
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


def readAdc(channel, clkPin, misoPin, mosiPin, csPin):
    if (channel < 0) or (channel > 7):
        print("Invalid ADC Channel number, must be between [0,7]")
        return -1
        
    # Datasheet says chip select must be pulled high between conversions
    GPIO.output(csPin, GPIO.HIGH)
    
    # Start the read with both clock and chip select low
    GPIO.output(csPin, GPIO.LOW)
    GPIO.output(clkPin, GPIO.HIGH)
    
    adcValue = recvBits(10, clkPin, misoPin)
    
    # Set chip select high to end the read
    GPIO.output(csPin, GPIO.HIGH)
  
    return round(adcValue)

def timeout():
    timeRunOut = True

    

#windowInit()
oldNumberOfActivations = 0
adcValueList = []
# Use try and keyboard exception for cleaning GPIO
try:
    
    # Main program
    print("Initializing GPIO and window")
    init_GPIO()
    servo = setup_servo(PIN_SERVO, PULSE_FREQ) # 50 Hz pulse
    
    while True:
        
        ADCvalue = readAdc(0, PIN_CLK, PIN_MISO, PIN_MOSI, PIN_CS)
        
        
        if ADCvalue > 300:
            print("drive")
            #driveServo()
            #ADCvalue = 0
            
            
        print("Adc: ", ADCvalue)
        time.sleep(0.5)
            
        if(GPIO.input(PIN_MOTORDETECT)):
            print("Motor Activated!")
            #Save adc values when motor is activated
            for i in range(20):
                adcValueList.append(ADCvalue)
            #count number of times used
            if(dispenserEmpty == False):
                oldNumberOfActivations = numberOfActivations
                numberOfActivations += 1
                print("Activations: ", numberOfActivations)
                diffActivations = numberOfActivations - oldNumberOfActivations
            
            if(diffActivations == 1):
                if(adcValueList):
                    adcMaxValue = max(adcValueList)
                    print(adcMaxValue)
                if(adcMaxValue > irSensorThreshold):
                    dispenserEmpty = False
                    adcValueList.clear()
                    adcMaxValue = 0
                    dispenserEmptyTemp = 0
                else:
                    dispenserEmptyTemp += 1
                    adcValueList.clear()
                    adcMaxValue = 0
            
                diffActivations = 0
                oldNumberOfActivations = 0

                if(dispenserEmptyTemp >= 3):
                    dispenserEmpty = True
                    #GPIO.output(PIN_TURNOFFDISPENSER, False)
                    print("Dispenser Empty!")
                    
                    
            timer = threading.Timer(1.2, timeout)
            timer.start()
            timer.join()
            
            
        """turnOffDispenser = False
        # Test MOSFET
        if(turnOffDispenser == True):
            GPIO.output(PIN_TURNOFFDISPENSER, False)
        else:
            GPIO.output(PIN_TURNOFFDISPENSER, True)"""
        
        
except KeyboardInterrupt:
    # Clean/reset GPIO pins before program terminates
    GPIO.cleanup()
    print("Cleaned up")
    