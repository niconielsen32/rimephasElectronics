import board
import adafruit_dotstar as dotstar
import pygame
from pydub import AudioSegment as AS
import numpy as np
import time

#------------ Functions to convert amplitudes to brightness -------
#Normalized Data
def normalize_data(sample, data):
    
    normalizedSample = (sample - min(data)) / (max(data) - min(data)) 
    
    return normalizedSample

# convert the normalized data to a brightness
def convert_normData_to_brightness(normData):
    
    maxBrightValue = 255
    brightValue = int(normData * maxBrightValue)
        
    return brightValue


# Choose color and set the brightness
def set_brightness(color, brightness):
    #return (0, 0, 255-brightness)
    if color == "red":
        return (brightness, 0, 0)
    elif color == "green":
        return (0, brightness, 0)
    elif color == "blue":
        return (0, 0, brightness)
    elif color == "all":
        return (brightness, brightness, brightness)

# Lightning up and then down like a pulse
def insideOut(middleOfDots, brightValue):
     for dot in range(middleOfDots):
        #print(color)
        dots[middleOfDots + dot] = brightValue
        dots[middleOfDots - dot -1] = brightValue
        time.sleep(0.0025)

# Goes out from middle and back again to middle
def insideOutIn(lengthOfDots, middleOfDots, brightValue):
     for dot in range(middleOfDots):
        dots[middleOfDots + dot] = brightValue
        dots[middleOfDots - dot -1] = brightValue
        time.sleep(0.002)
     for dot in range(middleOfDots):
        dots[lengthOfDots - dot - 1] = NOCOLOR
        dots[dot] = NOCOLOR
        time.sleep(0.002)

# Lightning up and then down like a pulse
def insideOutPulse(middleOfDots, brightValue):
     for dot in range(middleOfDots):
        #print(color)
        dots[middleOfDots + dot] = brightValue
        dots[middleOfDots - dot -1] = brightValue
        #time.sleep(0.02)
# All leds light up
def allLedsFill(brightValue):
    dots.fill(brightValue)


def sideToSide(lengthOfDots, brightValue):
    
    for dot in range(0, lengthOfDots):
        dots[dot] = brightValue
        time.sleep(0.015)
        
    for dot in range(0, lengthOfDots):
        dots[lengthOfDots - dot - 1] = NOCOLOR
        time.sleep(0.015)
       
    for dot in range(0, lengthOfDots):
        dots[lengthOfDots - dot - 1] = brightValue
        time.sleep(0.015)

    for dot in range(0, lengthOfDots):
        dots[dot] = NOCOLOR
        time.sleep(0.015)

    dots.fill(NOCOLOR)
    


#----------------LEDS init---------------------
NOCOLOR = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Using a DotStar Digital LED Strip with 72 LEDs connected to hardware SPI
# 5V - Yellow wire to gpio11 and green wire to gpio10 - 27 first - 
dots = dotstar.DotStar(board.SCK, board.MOSI, 28, brightness=0.3)

# Using a DotStar Digital LED Strip with 72 LEDs connected to digital pins
# 5V - Yellow wire to gpio6 and green wire to gpio5
#dots = dotstar.DotStar(board.D6, board.D5, 72, brightness=0.1)
 
red = "red"
green = "green"
blue = "blue"
allColors = "all"

chosenColor = blue
    
dots.fill(NOCOLOR)


numberOfDots = len(dots)
        
#---------- sound decoding -----------------
sound = AS.from_mp3("sounds/Hej_sprit.mp3")

raw_data = sound.raw_data
channels = sound.channels
sample_rate = sound.frame_rate
sample_size = sound.sample_width

amp_data = np.frombuffer(raw_data, dtype=np.int16)
amp_data = np.absolute(amp_data)
amp_data.tofile('amp_data.csv', sep=' ')

pygame.mixer.init()
pygame.mixer.music.load('sounds/Hej_sprit.mp3')
pygame.mixer.music.play()

i = 0
        
        
def change_brightness_when_speaking(sample_rate, amp_data):
    global i
    
    ms = pygame.time.Clock().tick(30)
    samples = int(sample_rate/(1000/ms))
    out = np.average(amp_data[i*samples:(i+1)*samples])
    #Normalize sample
    normalizedSample = normalize_data(out, amp_data)
    #convert amp to brightness
    brightnessScale = 4
    brightnessAmp = convert_normData_to_brightness(normalizedSample) * brightnessScale
    print("brightness: ", brightnessAmp)
    if(brightnessAmp > 255):
        brightnessAmp = 255
    #convert brightness to color
    brightValue = set_brightness(chosenColor, brightnessAmp)
    #print("color: ", brightValue)
    
    lengthOfDots = len(dots)
    middleOfDots = round(lengthOfDots/2)
    #print("brightValue: ", brightValue)
    
    # Fill all LEDs
    allLedsFill(brightValue)
    
    # Inside out
    #insideOut(middleOfDots, brightValue)
    
    # Inside out Pulse
    #insideOutPulse(middleOfDots, brightValue)
    
    # Inside Out and In
    #insideOutIn(lengthOfDots, middleOfDots, brightValue)
    
    # Sliding from side to side
    #sideToSide(lengthOfDots, BLUE)
    
    
    i += 1
    
    
while pygame.mixer.music.get_busy():
    
    # Change the brightness of the LEDs when its speaking
    change_brightness_when_speaking(sample_rate, amp_data)

pygame.mixer.quit()
dots.fill(NOCOLOR)