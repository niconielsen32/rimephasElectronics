from timerClass import createTimer

seconds = 0
timeRunout = False

def printer():
    global seconds
    seconds += 1

timer = createTimer(1,printer)
timer.start()


while True:
    print(seconds)
    
if timeRunout == True:
    print("test")
    