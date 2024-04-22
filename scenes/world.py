from constants import *
from nodes.camera import Camera
from nodes.curtain import Curtain
from nodes.room import Room
from nodes.mini_map import MiniMap
from actors.player import Player


class World:
    def __init__(self, game):
        # Get reference to game
        self.game = game

        # Init camera
        self.camera = Camera()

        # Init room
        # TODO: read save file to see which room to load
        self.room = Room(
            self.game,
            self.camera,
            "stage_1_bedroom_game.json"

            # STAGE 2 TEST REMOVE IN BUILD (DEL THE REAL JSON TOO)
            # "stage_2_test_game.json"
        )

        # Init player
        self.player = Player(
            self.game,
            self.room,
            self.camera,
            self
        )

        self.mini_map = MiniMap(self.player)

        # TODO: read save file to see where to put the player
        self.player.rect.x = 32
        self.player.rect.y = 32

        # Add player to quad tree in front of everyone, so that it will drawn in front
        self.room.quadtree.insert(self.player)

        # Whenever a room appear, call this to update the minimap
        self.room.add_room_to_mini_map(self.mini_map)

        # Set camera target to player
        self.camera.set_target(self.player.camera_anchor)

        # Curtain belongs to world, it needs to distinguish the callback
        self.curtain = Curtain(100, "invisible")
        self.curtain.add_event_listener(
            self.on_curtain_invisible, "invisible_end"
        )
        self.curtain.add_event_listener(
            self.on_curtain_opaque, "opaque_end"
        )

        # World state, room transition, pause, cutscene and so on
        self.state = "playing"

        # To remember which door after transition curtain
        self.next_door = None

    def on_player_hit_door(self, door):
        pass

    def on_curtain_invisible(self):
        pass

    def on_curtain_opaque(self):
        pass

    def change_room(self):
        pass

    def draw(self):
        # Clear canvas with hot pink, to see if there is a hole somewhere in case
        NATIVE_SURF.fill("pink")

        # Gameplay state
        if self.state == "playing":
            # Draw room
            self.room.draw()

            # Draw the mini map
            self.mini_map.draw()

    def update(self, dt):
        # Gameplay state
        if self.state == "playing":
            # Update all bg sprites actors, and moving actors
            self.room.update(dt)

    # Set state
    def set_state(self, value):
        old_state = self.state
        self.state = value

        # From playing
        if old_state == "playing":
            pass
