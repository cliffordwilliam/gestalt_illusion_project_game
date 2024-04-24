from constants import *
from nodes.curtain import Curtain
from nodes.mini_map import MiniMap


class Inventory:
    def __init__(self, world, player, game):
        # Get world
        self.world = world

        # Get player
        self.player = player

        # Get game
        self.game = game

        # Init minimap
        self.mini_map = MiniMap("inventory", self.player)

        # Prevent input during curtain fade
        self.is_allow_input = False

        # Inventory overlay, my base is a curtain
        self.curtain = Curtain(80, "invisible")
        self.curtain.add_event_listener(
            self.on_curtain_invisible, "invisible_end"
        )
        self.curtain.add_event_listener(
            self.on_curtain_opaque, "opaque_end"
        )

    # Called by world, I deactivate myself on exit
    def activate(self):
        self.curtain.go_to_opaque()

        # Need to redraw ONCE again with new plyaer pos and room
        self.mini_map.redraw_inventory_mini_map()

        # TODO: add pages for inventory, only clear when enter the map tab
        # Clear the curtain from old map
        self.curtain.surface.fill("black")

    # Caused by myself deactivate, tells world that I am done
    def on_curtain_invisible(self):
        # Overlay curtain is gone? Announce to world
        self.world.on_inventory_curtain_invisible()

    # Caused by activate that tells curtain to go apaque
    def on_curtain_opaque(self):
        # Allow input when fade to full is done
        self.is_allow_input = True

    def draw(self):
        # Draw my overlay
        self.curtain.draw()

        # Draw map on overlay in its inventory mode
        self.mini_map.draw(self.curtain.surface)

    def update(self, dt):
        # Priotize input checks
        if self.is_allow_input == True:
            # Prioritize pause input check
            if self.game.is_pause_just_pressed:
                # Deactivate myself, no input allowed, fade out
                self.is_allow_input == False
                self.curtain.go_to_invisible()

        # Update curtain, this thing stops itself when it is done
        self.curtain.update(dt)
