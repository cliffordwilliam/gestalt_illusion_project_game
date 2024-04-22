from constants import *


class Curtain:
    '''
    How to use: 
        1: Give me duration of 0 -> 255, same value is used for 255 -> 0
        2: Tell me either to start from 0 or 255
        3: Optional can give me subs on my 2 events, reach 0 (invisible) and reach 255 (opaque)

    What will happen:
        1: For every frame I draw my curtain
        2: My curtain alpha is determined by the timer, timer acts as a position
        3: Timer is 50% of duration? then 122 is the value. Timer == duration? 255. Timer = 0? 0
        4: Timer can go from 0 to 255 or 255 to 0 based on direction, update direction to go wherever you want
    '''

    def __init__(self, duration, start="invisible"):
        # Invisible or opaque
        self.start = start

        # Max alpha
        self.max_alpha = 255

        # Curtain init
        self.curtain = pg.Surface((NATIVE_W, NATIVE_H))
        self.curtain.fill("black")

        # Direction
        self.direction = 0

        # Start invisible default
        self.curtain.set_alpha(0)
        self.alpha = 0
        self.fade_duration = duration
        self.fade_timer = 0

        # Start opaque? Override values
        if self.start == "opaque":
            self.curtain.set_alpha(self.max_alpha)
            self.alpha = self.max_alpha
            self.fade_duration = duration
            self.fade_timer = self.fade_duration

        # Remainder
        self.remainder = 0

        # Callbacks
        self.listener_invisible_ends = []
        self.listener_opaque_ends = []

        # To see if this is lerping or not
        self.is_done_lerping = True

    def go_to_opaque(self):
        # Go to opaque
        self.direction = 1

        # Reset done flag
        self.is_done_lerping = False

    def go_to_invisible(self):
        # Go to invisible
        self.direction = -1

        # Reset done flag
        self.is_done_lerping = False

    def reset(self):
        # Start invisible default
        self.curtain.set_alpha(0)
        self.alpha = 0
        self.fade_timer = 0

        # Start opaque? Override values
        if self.start == "opaque":
            self.curtain.set_alpha(self.max_alpha)
            self.alpha = self.max_alpha
            self.fade_timer = self.fade_duration

        # Remainder
        self.remainder = 0

    def add_event_listener(self, value, event):
        if event == "invisible_end":
            self.listener_invisible_ends.append(value)

        elif event == "opaque_end":
            self.listener_opaque_ends.append(value)

    def draw(self):
        # No need to draw if invisible
        if self.alpha == 0:
            return

        # Draw transition curtain
        NATIVE_SURF.blit(self.curtain, (0, 0))

    def update(self, dt):
        # No need to update if invisible
        if self.is_done_lerping == True:
            return

        # Update timer with direction and dt, go left or right
        self.fade_timer += dt * self.direction

        # Clamp timer
        self.fade_timer = max(0, min(self.fade_duration, self.fade_timer))

        # Use timer as position
        fraction = self.fade_timer / self.fade_duration

        # Use position to update alpha value
        lerp_alpha = lerp(0, self.max_alpha, fraction)

        # Add prev round float loss
        lerp_alpha += self.remainder

        # Round to int
        self.alpha = max(0, min(self.max_alpha, round(lerp_alpha)))

        # Collect round loss
        self.remainder = lerp_alpha - self.alpha

        # Set alpha
        self.curtain.set_alpha(self.alpha)

        # invisible end reched - 0 - invisible?
        if self.fade_timer == 0:
            # Done lerping
            self.is_done_lerping = True

            # Announce subscribers
            for callback in self.listener_invisible_ends:
                callback()

        # Filled end reached - self.max_alpha - pitch black?
        elif self.fade_timer == self.fade_duration:
            # Done lerping
            self.is_done_lerping = True

            # Announce subscribers
            for callback in self.listener_opaque_ends:
                callback()
