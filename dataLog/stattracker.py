import datetime as dt
from pushbullet import Pushbullet
import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt, mpld3
from matplotlib.ticker import MaxNLocator
import numpy as np



class StatTracker:
    def __init__(self):
        self.activationsList = []
        self.numberOfDispenses = 10
        self.dispensesEmptyThreshold = 0.8
        self.almostEmpty = self.numberOfDispenses * self.dispensesEmptyThreshold
        self.hours = "%H"
        self.minutes = "%M"
        self.seconds = "%S"
        self.notification = "notification"
        self.sms = "sms"

        self.typeOfNotification = self.notification
        self.msg = "The dispenser is under 20" + "%" + " full."
        
        self.hoursStart = 0
        self.hoursEnd = 24
        self.timeFormat = self.seconds
        self.operatingTime = False
        self.lastHour = 0
        self.numberOfActivationsHour = 0
        
        self.numberOfActivationsMinute = 0
        self.firstMinSkipped = False
        self.trailingFiveMinSum = 0
        self.lastMinute = 0
        self.fiveMinQue = []
        self.hoursList = self.list_with_operating_hours()
        self.fig = plt.figure(figsize=[8, 4.8], dpi=100)
        
        self.xlist = np.arange(len(self.hoursList))
        self.labels = ["Activations"]

    def list_with_operating_hours(self):
        hoursList = []
        for i in range(self.hoursStart + 1, self.hoursEnd + 1):   
            #if (self.hoursEnd - self.hoursStart) > 10:
                #hoursList.append(str(i))
            #else:
            if i < 10:
                hoursList.append("0" + str(i)) #+ ":00")
            else:
                hoursList.append(str(i))# + ":00")
        length = len(hoursList)
        for i in range(length):
            self.activationsList.append(0)
        return hoursList
    
    def update_plot(self, numberOfActivations):
        dailyHour = dt.datetime.now()
        dailyHour = dailyHour.strftime(self.timeFormat)
        hour = int(dailyHour)
        hourString = ""
        if hour < 10:
            hourString = "0" + str(hour)# + ":00"
        else:
            hourString = str(hour)# + ":00"

        if hourString in self.hoursList:
            indexHour = self.hoursList.index(hourString)
            self.operatingTime = True
        else:
            self.operatingTime = False
            self.numberOfActivationsHour = numberOfActivations
        if hour != self.lastHour and self.operatingTime == True:
            trailingActivations = numberOfActivations - self.numberOfActivationsHour
            self.activationsList.insert(indexHour, round(trailingActivations))
            self.activationsList.pop(indexHour + 1)
            self.numberOfActivationsHour = numberOfActivations

        self.lastHour = hour
    
    def trailing_five_min_activations(self, numberOfActivations):
        dailyMinute = dt.datetime.now()
        dailyMinute = dailyMinute.strftime(self.timeFormat)
        minute = int(dailyMinute)

        if minute != self.lastMinute:
            if self.lastMinute != 0 and self.firstMinSkipped:
                if len(self.fiveMinQue) == 5:
                    self.fiveMinQue.pop(0)

                trailingActivations = numberOfActivations - self.numberOfActivationsMinute
                self.fiveMinQue.append(trailingActivations)
                self.numberOfActivationsMinute = numberOfActivations

            if len(self.fiveMinQue) == 5:
                self.trailingFiveMinSum = sum(self.fiveMinQue)

            self.lastMinute = minute
            self.firstMinSkipped = True

    def pushbullet_notification(self):
        pb = Pushbullet("o.xgWW2FkTk3pGt2oQXM9m9TiQXF2GvUPQ")
        phone = pb.devices[0] 
        phone = pb.get_device('OnePlus 7 Pro') 
        if self.typeOfNotification == "notification":
            push = phone.push_note("Alert!", self.msg)
        elif self.typeOfNotification == "sms":
            push = pb.push_sms(phone, "+4521378019", self.msg)
    
    def get_plot(self):
        plt.clf()
        plt.bar(self.xlist, self.activationsList, width=0.3)
        plt.title('Number of Activations')
        plt.xticks(self.xlist, self.hoursList)
        plt.xlabel("Time")
        plt.ylabel("Frequency")
        plt.legend(self.labels)
        ax = plt.gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        canvas = agg.FigureCanvasAgg(self.fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()
        
        return raw_data, size

