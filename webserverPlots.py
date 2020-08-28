import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab
import matplotlib.pyplot as plt, mpld3
import pygame
from pygame.locals import *
import datetime as dt
import random
#from eyetestV4 import faceTracking

# Matplotlib plot
fig = plt.figure(figsize=[8, 4.8], dpi=100)

dailyHour = dt.datetime.now()
dailyHour = dailyHour.strftime("%H")
print("Hour: ", dailyHour)


hoursStart = 10
hoursEnd = 20


def makeListWithRand():
    hours = []
    activations = []

    for i in range(hoursStart, hoursEnd):
        
        if i < 10:
            hours.append("0" + str(i) + ":00")
        else:
            hours.append(str(i) + ":00")
            
        activations.append(random.randint(10, 50))
            
    print(hours)   
    print(activations)
    
    return hours, activations


fig, axs = plt.subplots(2, 2)
hours, activations = makeListWithRand()
axs[0, 0].bar(hours, activations)
axs[0, 0].set_title('Plot 1')
hours, activations = makeListWithRand()
axs[0, 1].bar(hours, activations)
axs[0, 1].set_title('Plot 2')
hours, activations = makeListWithRand()
axs[1, 0].bar(hours, activations)
hours, activations = makeListWithRand()
axs[1, 1].bar(hours, activations)


for ax in axs.flat:
    ax.set(xlabel='x-label', ylabel='y-label')

# Hide x labels and tick labels for top plots and y ticks for right plots.
for ax in axs.flat:
    ax.label_outer()

# Plot
#ax = plt.bar(hours,activations)

mpld3.show()

if((hoursEnd - hoursStart) > 12):
    fig.autofmt_xdate()
    

# Using backend
canvas = agg.FigureCanvasAgg(fig)
canvas.draw()
renderer = canvas.get_renderer()
raw_data = renderer.tostring_rgb()


# Pygame plot from matplotlib plot
pygame.init()

window = pygame.display.set_mode((800, 480), DOUBLEBUF)
screen = pygame.display.get_surface()

size = canvas.get_width_height()

surf = pygame.image.fromstring(raw_data, size, "RGB")
screen.blit(surf, (0,0))
pygame.display.flip()


#faceTracking()

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
                    
pygame.display.quit()
pygame.quit()
