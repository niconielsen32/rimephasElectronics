import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab
import matplotlib.pyplot as plt, mpld3
import pygame
from pygame.locals import *
import datetime as dt
import random
from matplotlib.ticker import MaxNLocator

pygame.init()

# Matplotlib plot
fig = plt.figure(figsize=[8, 4.8], dpi=100)


hoursStart = 10
hoursEnd = 18

hours = "%H"
minutes = "%M"
seconds = "%S"

timeFormat = seconds

numberOfActivations = 0
numberOfActivationsHour = 0

lastHour = 0
operatingTime = False

hoursList = []


def update_activations_plot(operatingTimeList, numberOfActivations):
    global lastHour, activationsList, numberOfActivationsHour


    dailyHour = dt.datetime.now()
    dailyHour = dailyHour.strftime(timeFormat)
    #print("Hour: ", dailyHour)
    hour = int(dailyHour)

    hourString = ""

    if hour < 10:
        hourString = "0" + str(hour) + ":00"
    else:
        hourString = str(hour) + ":00"
    #print("hourString: ", hourString)


    if hourString in operatingTimeList:
        operatingHours = len(operatingTimeList) - 1
        #print("no hours: ", operatingHours)
        indexHour = operatingTimeList.index(hourString)
        operatingTime = True
    else:
        #print("no hours: ", operatingHours)
        operatingTime = False


    if hour != lastHour and operatingTime == True:
        trailingActivations = numberOfActivations - numberOfActivationsHour
        print("Activations: ", trailingActivations)
        activationsList.insert(indexHour, round(trailingActivations))
        activationsList.pop(indexHour + 1)
        print("acti list: ", activationsList)
        numberOfActivationsHour = numberOfActivations

    lastHour = hour
        
    return operatingTimeList, activationsList



def list_with_operating_hours(hoursStart, hoursEnd):
    hours = []
    activationsList = []

    for i in range(hoursStart + 1, hoursEnd + 1):
        
        if i < 10:
            hours.append("0" + str(i) + ":00")
        else:
            hours.append(str(i) + ":00")

    length = len(hours)

    for i in range(length):
        activationsList.append(0)
    
    return hours, activationsList



# Pygame plot from matplotlib plot

window = pygame.display.set_mode((800, 480), DOUBLEBUF)
screen = pygame.display.get_surface()



hoursList, activationsList = list_with_operating_hours(hoursStart, hoursEnd)
print(hoursList)
print(activationsList)
# Pygame loop
terminated = False
while not terminated:

    hoursList, antivationsList = update_activations_plot(hoursList, numberOfActivations)

    acti = [12, 8, 18,4,15,17,22,7]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminated = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("ESC")
                terminated = True
            if event.key == pygame.K_a:
                numberOfActivations += 1
            if event.key == pygame.K_p:

                plt.clf()
                plt.bar(hoursList,acti)
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
