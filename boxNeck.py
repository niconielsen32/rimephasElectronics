import RPi.GPIO as GPIO
from timerClass import createTimer
import random


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


GPIO.setmode(GPIO.BCM)

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


def move_servo_to_random_position():
    global servo
    
    randomPosition = random.randint(40, 140)
    set_angle(servo, randomPosition)
    print("Position: ", randomPosition)



timer = createTimer(5, move_servo_to_random_position)
timer.start()

# Main program loop.
    
try:
    
    servo = setup_servo(PIN_SERVO, PULSE_FREQ) # 50 Hz pulse

    while True:
        pass
        
            
except:
    servo.stop()
    GPIO.cleanup()
    print("clean up")