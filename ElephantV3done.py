import pygame
import pygame.freetype
import cv2
import threading
import multiprocessing as mp
from moviepy.editor import VideoFileClip
import math
import socket
import snowboydecoder
import speech_recognition as sr
from gtts import gTTS
import re
from pydub import AudioSegment as AS
import numpy as np
import random
import subprocess

import board
import adafruit_dotstar as dotstar

from edgetpu.detection.engine import DetectionEngine
from edgetpu.utils import dataset_utils
from PIL import Image
from PIL import ImageDraw

pygame.init()
#import stattracker         #stattracker.py
import os
import time

import pi_servo_hat
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import board
import adafruit_dotstar as dotstar

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25

##########  Settings  ##########
LANGUAGE = "en-US" # en-US or da-DK
isOnline = True
########## Load sounds ##########
Hi_sanitizer = "sounds/Hi_sanitizer.mp3"
Sorry_sanitizer = "sounds/Sorry_sanitizer.mp3"
Great_dispenser = "sounds/Great_dispenser.mp3"
Nice_day = "sounds/Nice_day.mp3"
Sorry_bye = "sounds/Sorry_bye.mp3"
Sorry_video = "sounds/Sorry_video.mp3"
Video = "sounds/Video.mp3"

Hej_sprit = "sounds/Hej_sprit.mp3"
Undskyld_sprit = "sounds/Undskyld_sprit.mp3"
Under_automaten = "sounds/Under_automaten.mp3"
God_dag = "sounds/God_dag.mp3"
Undskyld_farvel = "sounds/Undskyld_farvel.mp3"
Undskyld_video = "sounds/Undskyld_video.mp3"
Video_da = "sounds/Video_da.mp3"
Okay_video = "sounds/Okay_video.mp3"

thirtysec = "sounds/30sec.mp3"
joke1_1 = "sounds/joke1_1.mp3"
joke1_2 = "sounds/joke1_2.mp3"
joke2_1 = "sounds/joke2_1.mp3"
joke2_2 = "sounds/joke2_2.mp3"
joke3_1 = "sounds/joke3_1.mp3"
joke3_2 = "sounds/joke3_2.mp3"
nudge1 = "sounds/nudge1.mp3"
nudge2 = "sounds/nudge2.mp3"
nudge1da = "sounds/nudge1da.mp3"
Okay_video_da = "sounds/Okay_video_da.mp3"
thirtysecda = "sounds/30sec_da.mp3"
caring = "sounds/thanks_for_caring.mp3"
often = "sounds/sanitize_often.mp3"
trunk = "sounds/Trunk.mp3"

sounds_EN = [Hi_sanitizer, Video, trunk, Okay_video, Sorry_sanitizer, Sorry_video,  Nice_day, Sorry_bye,
          often, nudge1, thirtysec, caring, joke1_1, joke1_2, joke2_1, joke2_2, joke3_1, joke3_2]
          
sounds_DA = [Hej_sprit, Video_da, Under_automaten, Okay_video_da, Undskyld_sprit, Undskyld_video, God_dag, Undskyld_farvel,
          nudge1da, nudge1da, thirtysecda, caring]

########## Functions ##########

def checkInternet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False

def wait(ms):
    pygame.time.wait(ms)

def signal():
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted, timeout
    timeout += 0.03
    if threadevent.is_set():
        return True
    if timeout > 5:
        print("Timeout happened")
        return True
    return interrupted
    
def listen_for_two_cmds(cmd1, cmd2):
    global interrupted, timeout
    interrupted = False
    timeout = 0.
    detector = snowboydecoder.HotwordDetector(
        [f"resources/models/{cmd1}.pmdl",f"resources/models/{cmd2}.pmdl"], sensitivity=[0.5,0.5])
    detector.start(detected_callback=[detected_callback1, detected_callback2],
               interrupt_check=interrupt_callback,
               sleep_time=0.03)
    detector.terminate()
    print("Terminated")

def detected_callback1():
    print("callback 1")
    signal()
    global yes_detected
    yes_detected = True
    
def detected_callback2():
    print("callback 2")
    signal()
    global no_detected
    no_detected = True
    
def google_in():
    r = sr.Recognizer()
    r.pause_threshold = 0.5
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Say something!")
        try:
            audio = r.listen(source, timeout=4, phrase_time_limit=3)
        except sr.WaitTimeoutError:
            return "Timeout"
        else:
            try:
                out = r.recognize_google(audio, language=LANGUAGE)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
            else:
                return out
        return "Error"

def speech_in(cmd1, cmd2):
    global yes_detected, no_detected
    yes_detected = False
    no_detected = False
    if cmd1 == "yes" and LANGUAGE == "da-DK":
        cmdList1 = ["ja", "gerne", "jo", "ok"]
        cmdList2 = ["nej", "ellers tak"]
    elif cmd1 == "yes" and LANGUAGE == "en-US":
        cmdList1 = [cmd1, "please", "ok", "alright", "why not", "yeah", "i guess"]
        cmdList2 = [cmd2, "don't"]
    else:
        cmdList1 = [cmd1]
        cmdList2 = [cmd2]
    if not isOnline:
        listen_for_two_cmds(cmd1, cmd2)
    else:    
        gin = google_in()
        for cmd in cmdList1:
            if findWholeWord(cmd)(gin):
                yes_detected = True
                return
        for cmd in cmdList2:
            if findWholeWord(cmd)(gin):
                no_detected = True
                return
            
#------------ Functions to convert amplitudes to brightness -------
#Normalized Data
def normalize_data(sample, data):
    normalizedSample = (sample - min(data)) / (max(data) - min(data))
    return normalizedSample

# convert the normalized data to a brightness
def convert_normData_to_brightness(normData):
    if not math.isnan(normData):
        maxBrightValue = 255
        brightValue = int(normData * maxBrightValue)
    else: brightValue = 0
    return brightValue

# Choose color and set the brightness
def set_brightness(color, brightness):
    #return (0, 0, 255-brightness)
    if color == "red":
        return (255-brightness, 0, 0)
    elif color == "green":
        return (0, 255-brightness, 0)
    elif color == "blue":
        return (0, 0, 255-brightness)
    elif color == "all":
        return (brightness, brightness, brightness)

def insideOut():
    for dot in range(round(numberOfDots/2)):
        color = random_brightness(blue)
        dots[round(numberOfDots/2) + dot] = color
        dots[round(numberOfDots/2) - dot -1] = color

#----------------LEDS init---------------------
NOCOLOR = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

red = "red"
green = "green"
blue = "blue"
allColors = "all"

chosenColor = allColors

indexLED = 5

def change_brightness_when_speaking(sample_rate, amp_data):
    global indexLED
    
    ms = pygame.time.Clock().tick(30)
    samples = int(sample_rate/(1000/ms))
    out = np.average(amp_data[indexLED*samples:(indexLED+1)*samples])
    #Normalize sample
    normalizedSample = normalize_data(out, amp_data)
    #convert amp to brightness
    brightnessScale = 4
    brightnessAmp = convert_normData_to_brightness(normalizedSample) * brightnessScale
    if(brightnessAmp > 255):
        brightnessAmp = 255
    #convert brightness to color
    brightValue = set_brightness(chosenColor, brightnessAmp)
    lengthOfDots = len(dots)
    middleOfDots = round(lengthOfDots/2)
    # Fill all LEDs
    dots.fill(brightValue)
    #insideOut()
    indexLED += 1

def speech_out(index):
    global indexLED
    if LANGUAGE == "da-DK":
       sounds = sounds_DA
    else:
        sounds = sounds_EN
    pygame.mixer.init()
    pygame.mixer.music.load(sounds[index])
    sound = AS.from_mp3(sounds[index])
    raw_data = sound.raw_data
    sample_rate = sound.frame_rate * 2.3
    amp_data = np.frombuffer(raw_data, dtype=np.int16)
    amp_data = np.absolute(amp_data)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        if threadevent.is_set():
            pygame.mixer.quit()
            break
        change_brightness_when_speaking(sample_rate, amp_data)
    dots.fill(NOCOLOR)
    indexLED = 5

def interaction(*items):
    skip = False
    for item in items:
        if item == "nudge":
            speech_out(8+items[1])
        elif item == "30s":
            rand = random.randint(0,2)
            if rand: speech_out(10)
            else: speech_out(11)
        elif item == "joke":
            speech_out(11+items[1])
            wait(2000)
            speech_out(12+items[1])
        elif item == "sanitizer":
            interactionQuestion(0)
        threadevent.clear()
                      
def interactionQuestion(question):
    lastNumberOfActivations = numberOfActivations
    speech_out(question)
    i = 0 
    while not threadevent.is_set():   
        speech_in("yes", "no")
        if yes_detected:
            speech_out(question+2)
            if question == 0:
                    wait(3000)
                    if numberOfActivations != lastNumberOfActivations:
                        speech_out(10)
                    #else: add speech if no activation
                    else:
                        wait(2000)
                        break
        elif no_detected:
            speech_out(6)
            break
        elif question == 0 and numberOfActivations != lastNumberOfActivations:
            break
        elif i < 1:
            speech_out(question+4)
            i += 1
        else:
            speech_out(7)
    print("Flow ended")

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
  
res0 = (320,320)
res1 = (320,240)
res2 = (640,480)
res3 = (1280,720)
res = res2

def faceTracking(sender):
    engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
    cap = cv2.VideoCapture(-1)
    currentID = 1   
    faceTrackers = {}
    term = False
    peopleCount = 0
    
    while not term:
        _, frame = cap.read()
        
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        framePIL = Image.fromarray(frameRGB)
        faces = engine.detect_with_image(framePIL,
                                         threshold=0.05,
                                         keep_aspect_ratio=True,
                                         relative_coord=False,
                                         top_k=10,
                                         resample=4)
        for face in faces:
            (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
            w = x2-x
            h = y2-y
            center = (int(x+w*0.5), int(y+h*0.5))
            fidMatch = False
            for fid in faceTrackers.keys():
                (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
                if tx <= center[0] <= tx+tw and ty <= center[1] <= ty+th:
                    if n < 50: n += 1
                    if n >= 35 and c == False:
                        c = True
                        peopleCount += 1                        
                    faceTrackers.update({fid:(x,y,w,h,n,True,c)})
                    fidMatch = True
                    break
            if not fidMatch:
                faceTrackers.update({currentID:(x,y,w,h,1,True,False)})
                currentID += 1
            
            cv2.rectangle(frameRGB, (x, y), (x+w, y+h), (255, 0, 0), 2)

        fidsToDelete = []
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
            if not u:
                # if center is close to frame edge then decay faster
                #if res[0]-tw-20 < tx < 20:
                    #n-=5
                n -= 1
            if n < 1: fidsToDelete.append(fid)
            else:
                faceTrackers.update({fid:(tx,ty,tw,th,n,False,c)})

        for fid in fidsToDelete:
            faceTrackers.pop(fid, None)
        #if faceTrackers:    
        #    print("Sending")
        sender.send((faceTrackers, peopleCount, frameRGB))       
        if sender.poll():  
            term = sender.recv()
        
        """
        surf = pygame.surfarray.make_surface(frameRGB)
        surf_rot = pygame.transform.rotate(surf, 270)
        screen.blit(surf_rot, (0,0))
        pygame.display.flip()
        """
        pygame.time.Clock().tick(50)
        
    cap.release()

zeroPositionLeft = [90, 90]
zeroPositionRight = [85, 95]
lowerBoundaryHorizontalL = 50
upperBoundaryHorizontalL = 130
lowerBoundaryHorizontalR = 130
upperBoundaryHorizontalR = 50
lowerBoundaryVerticalL = 50
upperBoundaryVerticalL = 120
lowerBoundaryVerticalR = 120
upperBoundaryVerticalR = 50
distanceFromCenterToPerson = 0

noPeople = True

def drivePupil():
    global pupilL, pupilR, pupilV, zeroPositionLeft, zeroPositionRight, lowerBoundary, upperBoundary, noPeople

    if noPeople:
        zeroPositionLeft[0] = 90
        zeroPositionLeft[1] = 90
        zeroPositionRight[0] = 85
        zeroPositionRight[1] = 95
        servo.move_servo_position(0, zeroPositionLeft[0])
        servo.move_servo_position(1, zeroPositionLeft[1])
        servo.move_servo_position(2, zeroPositionRight[0])
        servo.move_servo_position(3, zeroPositionRight[1])
    else:
        # Set the new positions for the servos - new angle and the 
        leftPos = zeroPositionLeft[0] + pupilL
        vertPosL = zeroPositionLeft[1] - pupilV
        rightPos = zeroPositionRight[0] + pupilL
        vertPosR = zeroPositionRight[1] + pupilV
        

        # Set the boundaries for the eyes
        if(leftPos > upperBoundaryHorizontalL):
            leftPos = upperBoundaryHorizontalL
        elif(leftPos < lowerBoundaryHorizontalL):
            leftPos = lowerBoundaryHorizontalL
        if(rightPos < upperBoundaryHorizontalR):
            rightPos = upperBoundaryHorizontalR
        elif(rightPos > lowerBoundaryHorizontalR):
            rightPos = lowerBoundaryHorizontalR
        if(vertPosL > upperBoundaryVerticalL):
            vertPosL = upperBoundaryVerticalL
        elif(vertPosL < lowerBoundaryVerticalL):
            vertPosL = lowerBoundaryVerticalL
        if(vertPosR < upperBoundaryVerticalR):
            vertPosR = upperBoundaryVerticalR
        elif(vertPosL > lowerBoundaryVerticalR):
            vertPosR = lowerBoundaryVerticalR
        
        print("Pupil: ", pupilL)
        # Move servos - only if change in angle
        if pupilL != 0:
            # Left eye
            servo.move_servo_position(0, leftPos)
            #Update the zero position for the new camera position
            zeroPositionLeft[0] = leftPos
            # Right eye
            servo.move_servo_position(2, rightPos*0.85)
            #Update the zero position for the new camera position
            zeroPositionRight[0] = rightPos
             
        if pupilV != 0:
            servo.move_servo_position(1, vertPosL)
            #Update the zero position for the new camera position
            zeroPositionLeft[1] = vertPosL
            servo.move_servo_position(3, vertPosR)
            #Update the zero position for the new camera position
            zeroPositionRight[1] = vertPosR

def calculateAngles(x, y, w, h):
    WIDTH = res[0]/2
    HEIGHT = res[1]/2
    EYE_DEPTH = 2
    hFOV = 62/2
    vFOV = 49/2
    ppcm = WIDTH*2/15.5# * 1.5

    center = (int(x+w*0.5), int(y+h*0.5))
    hAngle = (1 - center[0]/WIDTH) * hFOV
    vAngle = (1 - center[1]/HEIGHT) * vFOV            
    c = -0.26*w+103
    if c < 30: c = 30
    
    global pupilL, pupilR, pupilV

    b = 4
    angleA = (90 - hAngle)*math.pi/180
    a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
    angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
    
    pupilL = int((angleC - math.pi/2) * EYE_DEPTH * ppcm)
    
    b_hat = 2*b
    c_hat = math.sqrt(a*a + b_hat*b_hat - 2*a*b_hat*math.cos(angleC))
    angleA_hat = math.acos((b_hat*b_hat + c_hat*c_hat - a*a)/(2*b_hat*c_hat))
    
    pupilR = int((math.pi/2 - angleA_hat) * EYE_DEPTH * ppcm)
    
    # vertical
    b = 6
    angleA = (90 - vAngle)*math.pi/180
    a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
    angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
    
    pupilV = int((angleC - math.pi/2) * EYE_DEPTH * ppcm)
    
    
    
########## Setup face detection ##########
pupilL = 0
pupilR = 0
pupilV = 0

########## Setup misc ##########
interrupted = False
yes_detected = False
no_detected = False
timeout = 0.

########## Events ##########
NORMALEVENT = pygame.USEREVENT + 1
NECKSERVOEVENT = pygame.USEREVENT + 2
INTERACTIONEVENT = pygame.USEREVENT + 3
PUMPINGEVENT = pygame.USEREVENT + 4
ELEPHANTEYESEVENT = pygame.USEREVENT + 5

pumpingevent = pygame.event.Event(PUMPINGEVENT)
########## States ##########
NORMALSTATE = 0
state = NORMALSTATE

numberOfActivations = 0

if __name__ == '__main__':
    if isOnline and not checkInternet():
        isOnline = False
    # Initialize interprocess communication
    receiver, sender = mp.Pipe(True)
    mp.set_start_method('spawn',force=True)
    tracking_proc = mp.Process(target=faceTracking, args=(sender,))
    tracking_proc.start()

    # Initialize interaction variables
    flow = threading.Thread(target=interaction)
    threadevent = threading.Event()
    trackID = 0
    altTrackID = 0
    gazeAtClosest = True

    videoKeys = []
    prevKeys = []
    prevInteraction = 0
    interactionWait = False
    interactionIndex = 0
    lastNumberOfActivations = 0
    peopleAmount = 1 #len(trackedList)
    frequency = 1    #from trailing_five
    interactionItems = []
    runInteraction = False
    
    # Initialize stats variables
    #st = stattracker.StatTracker()
    #hoursList = st.list_with_operating_hours()
    oldNumberOfPeople = 0
    numberOfPeople = 0
    
    # Servo and stuff 
    mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
    servo = pi_servo_hat.PiServoHat()
    servo.restart()
    # Drive servos to default
    servo.move_servo_position(0, zeroPositionLeft[0])
    servo.move_servo_position(1, zeroPositionLeft[1])
    servo.move_servo_position(2, zeroPositionRight[0])
    servo.move_servo_position(3, zeroPositionRight[1])
      
    # Using a DotStar Digital LED Strip with 72 LEDs connected to hardware SPI
    # 5V - Yellow wire to gpio11 and green wire to gpio10 - 66 first - 
    #dots = dotstar.DotStar(board.SCK, board.MOSI, 6, brightness=0.3)

    # Using a DotStar Digital LED Strip with 72 LEDs connected to digital pins
    # 5V - Yellow wire to gpio6 and green wire to gpio5
    dotsTrunk = dotstar.DotStar(board.D6, board.D5, 4, brightness=0.3)
    dots = dotstar.DotStar(board.D19, board.D13, 6, brightness=0.3)
    
    dots.fill(NOCOLOR)    
    dotsTrunk.fill(GREEN)
    
    pumpindex = 0
    pumpangles = [-35,135,-35]
    activated = False
    pumpwait = False
    sensorThresholdValue = 2
    # Load the first values into a list to have a default ir value for the sensor
    adcValue = mcp.read_adc(0)
    print("start: ", adcValue)
    # Ir sensor threshold
    adcThreshold = adcValue * sensorThresholdValue
    print("thresh: ", adcThreshold)
    
    screen = pygame.display.set_mode(res)
    pygame.time.set_timer(ELEPHANTEYESEVENT, 500)
    #screen = pygame.display.set_mode(res)
    clock = pygame.time.Clock()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("ESC")
                    done = True
                elif event.key == pygame.K_r:
                    pygame.time.set_timer(INTERACTIONEVENT, 1, True)
                    #interactionWait = False
                    runInteraction = not runInteraction
                    print("Run: ", runInteraction)
                elif event.key == pygame.K_o:
                    turnOffDispenser = not turnOffDispenser
                    print(turnOffDispenser)
                elif event.key == pygame.K_a:
                    numberOfActivations += 1
                    print("Activation!")
                elif event.key == pygame.K_f:
                    if frequency == 1: frequency = 10
                    else: frequency = 1
                    print("Frequency: ", frequency)
                elif event.key == pygame.K_p:
                    if peopleAmount == 1: peopleAmount = 10
                    else: peopleAmount = 1
                    print("Number of people: ", peopleAmount)
            ########## User Events ##########
            if event.type == INTERACTIONEVENT:
                interactionWait = False
                print("Interaction timer reset")
            #PUMPING EVENT - kører pumping sekvensen igennem
            elif event.type == PUMPINGEVENT:
                print("pumping angle: ", pumpangles[pumpindex])
                servo.move_servo_position(4, pumpangles[pumpindex])
                if pumpindex == 2:
                    pumpindex = 0
                    pumpwait = False
                else:
                    pumpindex += 1
                    pygame.time.set_timer(PUMPINGEVENT, 500, True)
            # drivePupil - Til at move eyes ud fra vinklerne - skal køre i et ELEPHANTEVENT hvert 200 ms:
            elif event.type == ELEPHANTEYESEVENT:
               
                drivePupil()
            """
            elif event.type == GAZEEVENT:
                gazeAtClosest = not gazeAtClosest
                altTrackID = 0
                if gazeAtClosest:
                    gazeTime = 8000 + random.randrange(-3, 3)*1000
                else:
                    gazeTime = 5000 + random.randrange(-2, 2)*1000
                pygame.time.set_timer(GAZEEVENT, gazeTime, True)
            """

        ########## Interaction ##########    
        #st.trailing_five_min_activations(disp.numberOfActivations)
        manyPeople = 3
        frequentUse = 5
        waitTimer = 0
        if receiver.poll():  
            (trackedList, peopleCount, frameRGB) = receiver.recv()
            trackedList = {k:v for (k,v) in trackedList.items() if v[4]>35}
            if runInteraction:                
                if not interactionWait and not flow.is_alive() and trackedList:
                    keys = trackedList.keys()
                    recurrents = set(keys) & set(prevKeys)
                    recurrentsVideo = set(keys) & set(videoKeys)
                    interactionItems = []
                    
                    # Scenarios
                    if frequency >= frequentUse:           # Scenario 1
                        waitTimer = 30000
               
                    else:                                  # Scenario 2
                        if prevInteraction == 2: interactionIndex += 1
                        else: interactionIndex = 0

                        if interactionIndex == 0:              #elif 2
                            interactionItems.append("sanitizer")
                            waitTimer = 30000
                
                elif not flow.is_alive(): # and activation
                    print("Acti ", numberOfActivations)
                    print("Last ", lastNumberOfActivations)
                    if lastNumberOfActivations != numberOfActivations:    
                        interactionItems.append("30s")
                
                if interactionItems:
                        print("Arguments: ", interactionItems)       
                        flow = threading.Thread(target=interaction, args=interactionItems)
                        flow.start()
                        interactionItems = []
            if waitTimer > 0:
                interactionWait = True
                pygame.time.set_timer(INTERACTIONEVENT, waitTimer, True)            
            lastNumberOfActivations = numberOfActivations
            
            # Gaze calculation and control
            if trackedList:
                noPeople = False
                """
                if gazeAtClosest:
                    if altTrackID == 0:
                        trackID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                        altTrackID = trackID
                    elif trackID not in trackedList:
                        trackID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                else:
                    if altTrackID == 0:
                        peopleList = list(trackedList.keys())
                        if len(peopleList) > 1:
                            maxID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                            peopleList.remove(maxID)
                        altTrackID = random.choice(peopleList)
                    if altTrackID in trackedList:
                        trackID = altTrackID
                    else:
                        trackID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                """
                trackID = max(trackedList.items(), key = lambda i : i[1][2])[0]
                (x, y, w, h, n, u, c) = trackedList.get(trackID)
                calculateAngles(x, y, w, h)
                
                if peopleCount > oldNumberOfPeople:
                    newPeople = peopleCount - oldNumberOfPeople
                    numberOfPeople += newPeople
                    oldNumberOfPeople = peopleCount
            else:
                noPeople = True
                #print("Reset eyes")
            surf = pygame.surfarray.make_surface(frameRGB)
            surf_rot = pygame.transform.rotate(surf, 270)
            screen.blit(surf_rot, (0,0))
            pygame.display.flip()
        #st.update_plot(disp.numberOfActivations, numberOfPeople)
        #disp.update()
        ########## State Machine ##########
        '''
        if disp.numberOfActivations >= almostEmpty:
            disp.numberOfActivations = 0
            st.pushbullet_notification(typeOfNotification, msg)
            print("Notification sent!")
        '''
        IRvalue = mcp.read_adc(0)
        #print(IRvalue)
        if IRvalue > adcThreshold and activated == False:
            numberOfActivations += 1
            activated = True
            pumpwait = True
            pygame.event.post(pumpingevent)
            print("PUMPING")
        elif activated == True and not pumpwait and IRvalue < adcValue*1.3:
            print(IRvalue)
            activated = False
    interrupted = True
    threadevent.set()
    receiver.send(True)
    while receiver.poll():  
        (trackedList, peopleCount, frameRGB) = receiver.recv()
    tracking_proc.terminate()
    #tracking_proc.join()
    pygame.display.quit()
    pygame.quit()
    print("Cleaned up")
    exit(0)

