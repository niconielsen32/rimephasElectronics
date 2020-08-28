import cv2
import pi_servo_hat
import time
import random
import math
from threading import Timer,Thread,Event

pupilV = 0
pupilR = 0
pupilL = 0
zeroPositionLeft = [90, 90]
zeroPositionRight = [90, 90]
lowerBoundaryHorizontal = 50
upperBoundaryHorizontal = 130
lowerBoundaryVertical = 50
upperBoundaryVertical = 120
distanceFromCenterToPerson = 0

noPeople = True


# Servo Motor Object
servo = pi_servo_hat.PiServoHat()

if(servo == False):
    print("No i2c connection")

# Restart chip and return pwm freq to default 50 Hz
servo.restart()

# Drive servos to default
servo.move_servo_position(0, zeroPositionLeft[0])
servo.move_servo_position(1, zeroPositionLeft[1])
servo.move_servo_position(2, zeroPositionRight[0])
servo.move_servo_position(3, zeroPositionRight[1])


#print(servo.get_servo_position(0))

class perpetualTimer():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()
    

def faceTracking():
    global pupilV, pupilR, pupilL, noPeople
    
    pupilV = 0
    pupilR = 0
    pupilL = 0
    angleChangeThresholdLeft = [1.44, 1.68]
    angleChangeThresholdRight = [1.44, 1.68]
    angleChangeThresholdVert = [1.5, 1.6]
    
    res1 = (320,240)
    res2 = (640,480)
    res3 = (1280,720)
    res = res1

    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(-1)
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
        frame = cv2.rotate(frame, cv2.ROTATE_180)
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
    
        noOfPeople = len(faceTrackers)
        
        if noOfPeople == 0:
            noPeople = True
        else:
            noPeople = False
       
        if trackID != -1:
            
            # determine who to track
            (x, y, w, h, n, u) = faceTrackers.get(trackID)
            center = (int(x+w*0.5), int(y+h*0.5))
            hAngle = (1 - center[0]/WIDTH) * hFOV
            vAngle = (1 - center[1]/HEIGHT) * vFOV
            # Linear regression to find distance from camera to person
            c = -0.26*w+103
            
        
            # Left Eye - Horizontal
            b = 4 # distance from camera to eye
            # Angle from middel of FOV to person
            angleA = (90 - hAngle)*math.pi/180
            # Distance from eye to person
            a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
            # Angle from eye to person
            angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
            
            #only update if bigger change in angle
            if angleC > angleChangeThresholdLeft[1] or angleC < angleChangeThresholdLeft[0]:
                pupilL = int((angleC - math.pi/2) * EYE_DEPTH * ppcm)
            else:
                pupilL = 0
            
            
            # Right eye - Horizontal direction
            b_hat = 2*b # distance from camera to eye
            # Distance from eye to person
            c_hat = math.sqrt(a*a + b_hat*b_hat - 2*a*b_hat*math.cos(angleC))
            # Angle from eye to person
            angleA_hat = math.acos((b_hat*b_hat + c_hat*c_hat - a*a)/(2*b_hat*c_hat))
            
            #only update if bigger change in angle
            if(angleA_hat > angleChangeThresholdRight[1] or angleA_hat < angleChangeThresholdRight[0]):
                pupilR = int((math.pi/2 - angleA_hat) * EYE_DEPTH * ppcm)
            else:
                pupilR = 0
            
            
            # Both eyes - Vertical direction
            b = 6 # distance from camera to eye
            # Angle from middel of FOV to person
            angleAV = (90 - vAngle)*math.pi/180
            # Distance from eye to person
            a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleAV))
            # Angle from eye to person
            angleCV = math.acos((a*a + b*b - c*c)/(2*a*b))
            
            #only update if bigger change in angle - Calculate pupil move
            if angleCV > angleChangeThresholdVert[1] or angleCV < angleChangeThresholdVert[0]:
                pupilV = int((angleCV - math.pi/2) * EYE_DEPTH * ppcm)
            else:
                pupilV = 0
                
            #sender.send((pupilL, pupilR, pupilV))
            
        #if sender.poll():  
          #  term = sender.recv()
        # Draw the rectangle around each face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def drawPupils():
    pupilposL = (centerL[0]+pupilL, centerL[1]-pupilV)
    pupilposR = (centerR[0]+pupilR, centerR[1]-pupilV)
    screen.blit(pupil, pupilposL)
    screen.blit(pupil, pupilposR)
    

    
def drivePupil():
    global servo, pupilL, pupilR, pupilV, zeroPositionLeft, zeroPositionRight, lowerBoundary, upperBoundary, noPeople
    
    print(noPeople)

    
    # Scale the pupils
    pupilScale = 1.5
    #oldMovePupilL = newMovePupilL
    # The new angle of the pupils
    newMovePupilL = pupilL * pupilScale
    newMovePupilR = pupilR * pupilScale *1.2
    newMovePupilV = pupilV * pupilScale
    
    # Set the new positions for the servos - new angle and the 
    leftPos = zeroPositionLeft[0] + newMovePupilL
    vertPosL = zeroPositionLeft[1] - newMovePupilV
    rightPos = zeroPositionRight[0] + newMovePupilR
    vertPosR = zeroPositionRight[1] + newMovePupilV
    
    print("left: ", leftPos)
    print("right: ", rightPos)
    print("vertPosL: ", vertPosL)
    print("vertPosR: ", vertPosR)
    
    # Set the boundaries for the eyes
    if(leftPos > upperBoundaryHorizontal):
        leftPos = upperBoundaryHorizontal
    elif(leftPos < lowerBoundaryHorizontal):
        leftPos = lowerBoundaryHorizontal
    
    if(rightPos > upperBoundaryHorizontal):
        rightPos = upperBoundaryHorizontal
    elif(rightPos < lowerBoundaryHorizontal):
        rightPos = lowerBoundaryHorizontal
    
    if(vertPosL > upperBoundaryVertical):
        vertPosL = upperBoundaryVertical
    elif(vertPosL < lowerBoundaryVertical):
        vertPosL = lowerBoundaryVertical
    
    #print("pupL: ", pupilL)
    #print("pupR: ", pupilR)
    # Move servos - only if bigger change in angle occurs
    if pupilL != 0:
        servo.move_servo_position(0, leftPos)
        #print("Left Hori Move")
        
    if pupilR != 0:
        servo.move_servo_position(2, rightPos)
        #print("Right Hori Move")
        
    if pupilV != 0:
        servo.move_servo_position(1, vertPosL)
        servo.move_servo_position(3, vertPosR)
        #print("Vertical Move")
    
    #Update the zero position for the new camera position
    zeroPositionLeft[0] = leftPos
    zeroPositionLeft[1] = vertPosL
    zeroPositionRight[0] = rightPos
    zeroPositionRight[1] = vertPosR
    
    #print("posHori: ", zeroPositionLeft[0])
    #print("posVert: ", zeroPositionLeft[1])

    
# Update the servos every second    
t = perpetualTimer(1, drivePupil)
t.start()

faceTracking()


