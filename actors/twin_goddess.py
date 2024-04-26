from constants import *
from nodes.popup import Popup


class TwinGoddess:
    def __init__(self, id, sprite_sheet, sprite_sheet_flip, animation_data, camera, xds, yds, game, room, quadtree, player, sprite_region):
        # Get player
        self.player = player

        # Get game
        self.game = game

        # Get room
        self.room = room

        # Get camera
        self.camera = camera

        # Get quadtree
        self.quadtree = quadtree

        # Id for quadtree bookeeping, for quick relocation in quad
        self.id = id

        # Name
        self.name = "twin_goddess"

        # Parents load once and pass to me
        self.sprite_sheet = sprite_sheet

        # Init starting region
        self.region = [384, 512, 96, 80]

        # Rect
        self.rect = pg.FRect(0, 0, self.region[2], self.region[3])
        self.rect.midbottom = (
            xds,
            yds + TILE_S
        )

        # Popup init
        text = f"press {
            pg.key.name(self.game.key_bindings["up"])
        } to save"

        self.popup = Popup(
            text,
            500,
            self.camera
        )

        # Set popup position
        self.popup.rect.center = self.rect.center
        self.popup.rect.y -= TILE_S

        # State
        self.state = "looking"

    def draw(self):
        # Draw myself
        xds = self.rect.x - self.camera.rect.x
        yds = self.rect.y - self.camera.rect.y
        NATIVE_SURF.blit(
            self.sprite_sheet,
            (xds, yds),
            self.region
        )

        # Draw my overlay
        self.popup.draw()

        # Debug draw
        if self.game.is_debug:
            x = self.rect.x - self.camera.rect.x
            y = self.rect.y - self.camera.rect.y
            w = self.rect.width
            h = self.rect.height

            # Owner real rect
            self.game.debug_draw.add(
                {
                    "type": "rect",
                    "layer": 1,
                    "rect": [x, y, w, h],
                    "color": "red",
                    "width": 1
                }
            )

            # Base
            x = self.rect.x - self.camera.rect.x
            y = self.rect.y - self.camera.rect.y

            # State
            self.game.debug_draw.add(
                {
                    "type": "text",
                    "layer": 3,
                    "x": x,
                    "y": y - FONT_H,
                    "text": f"name: {self.name}"
                }
            )

    def update(self, dt):
        # Looking
        if self.state == "looking":

            # Exit logic first

            # Exit to found when player is found
            if self.player in self.quadtree.search(self.rect):
                self.set_state("found")

            # Then state logic

        # Found
        elif self.state == "found":

            # Exit logic first

            # Exit to found when player is found
            if not self.player in self.quadtree.search(self.rect):
                self.set_state("looking")

            # Then state logic

        # Update curtain, this thing stops itself when it is done
        self.popup.update(dt)

    # Set state
    def set_state(self, value):
        old_state = self.state
        self.state = value

        # From run
        if old_state == "looking":
            # To idle
            if self.state == "found":
                self.popup.go_to_opaque()

        # From run
        elif old_state == "found":

            # To idle
            if self.state == "looking":
                self.popup.go_to_invisible()
