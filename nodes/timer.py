from constants import *


class Timer:
    '''
    How to use: 
        1: Set my duration
        2: Call my update to start counting
        3: When time is up, I will call your callback

    What will happen:
        1: Timer is incremented on every frame
        2: When reaches end, it will reset the timer to 0
    '''

    def __init__(self, duration):
        # Counter
        self.timer = 0

        # How long do I count?
        self.duration = duration

        # Callbacks
        self.listener_end = []

        # Guard update from running when I am done
        self.is_done = False

    def add_event_listener(self, value, event):
        if event == "timer_end":
            self.listener_end.append(value)

    # Prepare to count again
    def reset(self):
        # Set timer to 0
        self.timer = 0
        # Set done to false
        self.is_done = False

    def update(self, dt):
        # Do not do anything if it is done
        if self.is_done == True:
            return

        # Start counting
        self.timer += dt
        # Time is up?
        if self.timer > self.duration:
            # Set done true
            self.is_done = True
            # Announce that I am done
            for callback in self.listener_end:
                callback()
