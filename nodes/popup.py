from constants import *


class Popup:
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

    def __init__(self, text, duration, camera, start="invisible"):
        # Get camera
        self.camera = camera

        # Text
        self.text = text

        self.padding = 2

        self.rect = FONT.get_rect(self.text)
        self.rect.inflate_ip(
            self.padding * 2,
            self.padding * 2
        )

        # Invisible or opaque
        self.start = start

        # Max alpha
        self.max_alpha = 255

        # Max y offset
        self.max_y_offset = TILE_S // 2

        # Curtain init
        self.surface = pg.Surface(
            (
                self.rect.width,
                self.rect.height
            )
        )
        self.surface.fill("black")

        # Draw text on the surface
        FONT.render_to(
            self.surface,
            (
                self.padding,
                self.padding
            ),
            self.text,
            "white",
            "black",
        )

        # Draw border on text surface
        pg.draw.rect(
            self.surface,
            "white",
            [
                0,
                0,
                self.rect.width,
                self.rect.height,
            ],
            1
        )

        # Direction
        self.direction = 0

        # Start invisible default
        self.surface.set_alpha(0)
        self.alpha = 0
        self.fade_duration = duration
        self.fade_timer = 0

        # Start opaque? Override values
        if self.start == "opaque":
            self.surface.set_alpha(self.max_alpha)
            self.alpha = self.max_alpha
            self.fade_timer = self.fade_duration

        # Y offset
        self.y_offset = 0

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

    def add_event_listener(self, value, event):
        if event == "invisible_end":
            self.listener_invisible_ends.append(value)

        elif event == "opaque_end":
            self.listener_opaque_ends.append(value)

    def draw(self):
        # No need to draw if invisible
        if self.alpha == 0:
            return

        x = self.rect.x - self.camera.rect.x
        y = self.rect.y - self.camera.rect.y - self.y_offset

        # Draw transition curtain
        NATIVE_SURF.blit(self.surface, (x, y))

    def update(self, dt):
        # No need to update if invisible
        if self.is_done_lerping:
            return

        # Update timer with direction and dt, go left or right
        self.fade_timer += dt * self.direction

        # Clamp timer
        self.fade_timer = clamp(self.fade_timer, 0, self.fade_duration)

        # Use timer as position
        fraction = self.fade_timer / self.fade_duration

        # Use position to update alpha value
        lerp_alpha = lerp(0, self.max_alpha, fraction)

        # Add prev round float loss
        lerp_alpha += self.remainder

        # Round to int
        self.alpha = clamp(round(lerp_alpha), 0, self.max_alpha)

        # Use position to update y offset
        self.y_offset = round(lerp(0, self.max_y_offset, fraction))

        # Collect round loss
        self.remainder = lerp_alpha - self.alpha

        # Set alpha
        self.surface.set_alpha(self.alpha)

        # invisible end reached - 0 - invisible?
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
