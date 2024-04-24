from constants import *
from nodes.camera import Camera
from nodes.curtain import Curtain
from nodes.room import Room
from nodes.mini_map import MiniMap
from nodes.inventory import Inventory
from actors.player import Player


class World:
    def __init__(self, game):
        # Get reference to game
        self.game = game

        # Init camera
        self.camera = Camera(game = game)

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

        # Init mini map
        self.mini_map = MiniMap("gameplay", self.player)

        # Init inventory
        self.inventory = Inventory(self, self.player, self.game)

        # TODO: read save file to see where to put the player
        self.player.rect.midbottom = (10 * TILE_S, 9 * TILE_S)

        # Add player to quad tree in front of everyone, so that it will drawn in front
        self.room.quadtree.insert(self.player)

        # Whenever a room appear, call this to update the minimap
        self.room.add_room_to_mini_map(self.mini_map)
        self.room.add_room_to_mini_map(self.inventory.mini_map)

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

    def on_inventory_curtain_invisible(self):
        # Reset curtain
        self.curtain.reset()

        # Go back to playing
        self.set_state("playing")

    def on_player_hit_door(self, door):
        # Only trigger once, do not call if alr in transition
        if self.state != "transition":
            # Remember this door to use after curtain reach opaque
            self.next_door = door

            # Exit to transition state
            self.set_state("transition")

            # Tell curtain go to opaque
            self.curtain.go_to_opaque()

    def on_curtain_invisible(self):
        # Return to playing state
        self.set_state("playing")

    def on_curtain_opaque(self):
        # Curtain fully closed, change the room

        # Change room
        self.change_room()

        # Tell curtain to fade out
        self.curtain.go_to_invisible()

    def change_room(self):
        # Change to new room
        self.room.set_name(self.next_door["door_target"])

        # Add player to quad tree in front of everyone, so that it will drawn in front
        self.room.quadtree.insert(self.player)

        # Whenever a room appear, call this to update the minimap, duplicate is impossible, they handle that
        self.room.add_room_to_mini_map(self.mini_map)
        self.room.add_room_to_mini_map(self.inventory.mini_map)

        # Get door direction
        door_direction = self.next_door["door_direction"]

        # Based on door direction, update player and camera position
        if door_direction == "left":
            self.player.rect.right = (
                self.room.rect[0] + self.room.rect[2]) - TILE_S
            self.camera.rect.x -= NATIVE_W

        elif door_direction == "right":
            self.player.rect.left = self.room.rect[0] + TILE_S
            self.camera.rect.x += NATIVE_W

        elif door_direction == "up":
            self.player.rect.bottom = (
                self.room.rect[1] + self.room.rect[3]) - (2 * TILE_S)
            self.camera.rect.y -= NATIVE_H

        elif door_direction == "down":
            self.player.rect.top = self.room.rect[1] + TILE_S
            self.camera.rect.y += NATIVE_H

    def draw(self):
        # Clear canvas with hot pink, to see if there is a hole somewhere in case
        NATIVE_SURF.fill("pink")

        # Gameplay state
        if self.state == "playing":
            # Draw room
            self.room.draw()

            # Draw the mini map
            self.mini_map.draw()

        # Transition state
        elif self.state == "transition":
            # Draw room
            self.room.draw()

            # Draw the mini map
            self.mini_map.draw()

            # Draw transition curtain
            self.curtain.draw()

        # Gameplay state
        elif self.state == "pause":
            # Draw room
            self.room.draw()

            # Draw the mini map
            self.mini_map.draw()

            # Draw inventory
            self.inventory.draw()

    def update(self, dt):
        # Gameplay state
        if self.state == "playing":
            # Prioritize pause input check
            if self.game.is_pause_just_pressed:
                self.set_state("pause")

            # Update all bg sprites actors, and moving actors
            self.room.update(dt)

            # Update camera (must be here, after its target actor moved)
            self.camera.update(dt)

        elif self.state == "transition":
            # On transition state, immediately update transition curtain
            self.curtain.update(dt)

        elif self.state == "pause":
            # On pause state, immediately update overlay curtain
            self.inventory.update(dt)

    # Set state
    def set_state(self, value):
        old_state = self.state
        self.state = value

        # From playing
        if old_state == "playing":
            # To pause
            if self.state == "pause":
                # Tell pause inventory to activate  / fade in
                self.inventory.activate()
                pass

        # From pause
        if old_state == "pause":
            # To playing
            if self.state == "playing":
                pass

        # From transition
        if old_state == "transition":
            # To playing
            if self.state == "playing":
                pass
