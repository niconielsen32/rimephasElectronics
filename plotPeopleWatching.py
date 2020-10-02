import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab
import matplotlib.pyplot as plt, mpld3
import pygame
from pygame.locals import *
import datetime as dt
import random
import cv2
import math
from matplotlib.ticker import MaxNLocator

pygame.init()

activationPlot = "activations"
numberPeoplePlot = "people"

typeOfPlot = activationPlot


# Matplotlib plot
fig = plt.figure(figsize=[8, 4.8], dpi=100)


hoursStart = 0
hoursEnd = 10

hours = "%H"
minutes = "%M"
seconds = "%S"

timeFormat = seconds

lastHour = 0
operatingTime = False

numberOfPeopleHour = 0
oldNumberOfPeople = 0
numberOfPeople = 0
people = 0
hoursListPeople = []
peopleList = []



def faceTracking():
    global pupilV, pupilR, pupilL, oldNumberOfPeople, numberOfPeople, people
    
    pupilV = 0
    pupilR = 0
    pupilL = 0
    numbers = 0
    tempList = [0]
    
    res1 = (320,240)
    res2 = (640,480)
    res3 = (1280,720)
    res = res1

    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
    frameCounter = 0
    currentID = 0   
    faceTrackers = {}
    
    WIDTH = res[0]/2
    HEIGHT = res[1]/2
    EYE_DEPTH = 2
    hFOV = 62/2
    vFOV = 49/2
    ppcm = WIDTH*2/15.5
    term = False
    
    while not term:
        ret, frame = cap.read()
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        #frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frameCounter += 1
        if frameCounter % 1 == 0:
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                grey,
                scaleFactor = 1.1,
                minNeighbors = 5,
                minSize = (30, 30),                           
                flags = cv2.CASCADE_SCALE_IMAGE)
            for (x, y, w, h) in faces:
                center = (int(x+w*0.5), int(y+h*0.5))
                fidMatch = False
                for fid in faceTrackers.keys():
                    (tx, ty, tw, th, n, u) =  faceTrackers.get(fid)
                    if tx <= center[0] <= tx+tw and ty <= center[1] <= ty+th:
                        if n < 50: n += 1
                        faceTrackers.update({fid:(x,y,w,h,n,True)})
                        fidMatch = True
                        break
                if not fidMatch:
                    faceTrackers.update({currentID:(x,y,w,h,1,True)})
                    currentID += 1
                    
                    
        trackID = -1
        fidsToDelete = []
        #noOfPeople = findNoOfPeopleWatching(faceTrackers)
        
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u) =  faceTrackers.get(fid)
            if not u: n -= 1
            if n < 1: fidsToDelete.append(fid)
            else:
                faceTrackers.update({fid:(tx,ty,tw,th,n,False)})
                if n < 25:
                    pass
                else:
                    trackID = fid
       
        for fid in fidsToDelete:
            faceTrackers.pop(fid, None)
        
        if trackID != -1:
            
            # determine who to track
            (x, y, w, h, n, u) = faceTrackers.get(trackID)
            center = (int(x+w*0.5), int(y+h*0.5))
            hAngle = (1 - center[0]/WIDTH) * hFOV
            vAngle = (1 - center[1]/HEIGHT) * vFOV            
            c = -0.26*w+103
            
            
            # Left Eye - Horizontal
            b = 4
            angleA = (90 - hAngle)*math.pi/180
            #print("hAngle: ", hAngle)
            a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
            angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
            pupilL = int((angleC - math.pi/2) * EYE_DEPTH * ppcm)
            
            # Right Eye - Horizontal
            b_hat = 2*b
            c_hat = math.sqrt(a*a + b_hat*b_hat - 2*a*b_hat*math.cos(angleC))
            angleA_hat = math.acos((b_hat*b_hat + c_hat*c_hat - a*a)/(2*b_hat*c_hat))
            pupilR = int((math.pi/2 - angleA_hat) * EYE_DEPTH * ppcm)
            
            # Both Eyes - Vertical
            b = 6
            angleA = (90 - vAngle)*math.pi/180
            a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
            angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
            pupilV = int((angleC - math.pi/2) * EYE_DEPTH * ppcm)

                
            #sender.send((pupilL, pupilR, pupilV))

        # Find number of people in video


        # DET HER ER ÆNDRET ----------------------------------------------------------------------
        people = len(faceTrackers)
        
        if people > oldNumberOfPeople:
            newPeople = people - oldNumberOfPeople
            numberOfPeople += newPeople
            print("People: ", numberOfPeople)

        update_people_plot(hoursListPeople, numberOfPeople)

        oldNumberOfPeople = people
         
        #-----------------------------------------------------------------------------------------   
        #if sender.poll():  
          #  term = sender.recv()
        # Draw the rectangle around each face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("no: ", numbers)
            break
    cap.release()
    cv2.destroyAllWindows()



def update_people_plot(operatingTimeList, numberOfPeople):
    global lastHour, peopleList, numberOfPeopleHour

    dailyHour = dt.datetime.now()
    dailyHour = dailyHour.strftime(timeFormat)
    hour = int(dailyHour)

    hourString = ""

    if hour < 10:
        hourString = "0" + str(hour) + ":00"
    else:
        hourString = str(hour) + ":00"


    if hourString in operatingTimeList:
        operatingHours = len(operatingTimeList) - 1
        indexHour = operatingTimeList.index(hourString)
        operatingTime = True
    else:
        operatingTime = False

   

    if hour != lastHour and operatingTime == True:

        trailingPeople = numberOfPeople - numberOfPeopleHour
        print("People: ", trailingPeople)
        peopleList.insert(indexHour, round(trailingPeople))
        peopleList.pop(indexHour + 1)
        print("People list: ", peopleList)
        numberOfPeopleHour = numberOfPeople


    lastHour = hour



def list_with_operating_hours(hoursStart, hoursEnd):
    hours = []
    numberList = []

    for i in range(hoursStart + 1, hoursEnd + 1):
        
        if i < 10:
            hours.append("0" + str(i) + ":00")
        else:
            hours.append(str(i) + ":00")

    length = len(hours)

    for i in range(length):
        numberList.append(0)
    
    return hours, numberList



# Pygame plot from matplotlib plot

window = pygame.display.set_mode((800, 480), DOUBLEBUF)
screen = pygame.display.get_surface()


hoursListPeople, peopleList = list_with_operating_hours(hoursStart, hoursEnd)
print(hoursListPeople)
print(peopleList)

faceTracking()

# Pygame loop
terminated = False
while not terminated:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminated = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("ESC")
                terminated = True
            if event.key == pygame.K_a:
                numberOfActivations += 1
                print("acti: ", numberOfActivations)
            if event.key == pygame.K_p:
 

                # plot
                plt.clf()
                plt.bar(hoursListPeople, peopleList)
                plt.title('Number Of Activations')

                ax = plt.gca()
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))

                #send to local webserver
                #mpld3.show()

                if((hoursEnd - hoursStart) > 12):
                    fig.autofmt_xdate()
    

                # Using backend
                canvas = agg.FigureCanvasAgg(fig)
                canvas.draw()
                renderer = canvas.get_renderer()
                raw_data = renderer.tostring_rgb()

                size = canvas.get_width_height()

                surf = pygame.image.fromstring(raw_data, size, "RGB")
                screen.blit(surf, (0,0))
                pygame.display.flip()
                    


pygame.display.quit()
pygame.quit()
