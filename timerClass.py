from threading import Timer,Thread,Event


class createTimer():

   def __init__(self,timer,hFunction):
      self.timer = timer
      self.hFunction = hFunction
      self.thread = Timer(self.timer,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.timer,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()
      
    

