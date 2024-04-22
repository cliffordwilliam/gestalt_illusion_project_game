from constants import *
from nodes.animator import Animator


class Fire:
    def __init__(self, sprite_sheet, animation_data, camera, xds, yds):
        # Depedencies
        self.camera = camera

        # Name
        self.name = "Fire"

        # Parents load once and pass to me
        self.sprite_sheet = sprite_sheet

        # Parents load once and pass to me
        self.aniamtion_data = animation_data

        # Init starting region
        self.region = self.aniamtion_data["burn"]["frames_list"][0]["region"]

        # Rect
        self.rect = pg.Rect(xds, yds, self.region[2], self.region[3])

        # Animator node
        self.animator = Animator(self, self.aniamtion_data, "burn")

    def draw(self):
        # Turn my coord to draw coord
        xds = self.rect.x - self.camera.rect.x
        yds = self.rect.y - self.camera.rect.y

        # Draw me with draw coord
        NATIVE_SURF.blit(
            self.sprite_sheet,
            (xds, yds),
            self.region
        )

    def update(self, dt):
        # Update animation node
        self.animator.update(dt)
