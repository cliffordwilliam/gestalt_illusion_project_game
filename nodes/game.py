from constants import *
from scenes.json_editor import JsonEditor
from scenes.room_editor import RoomEditor
from scenes.world import World
from nodes.audio_player import SoundManager
from nodes.debug_draw import DebugDraw
from actors.fire import Fire
from actors.goblin import Goblin


class Game:
    def __init__(self, initial_scene):
        # Game debug flag
        self.is_debug = False

        # REMOVE IN BUILD, for everyone to use
        self.debug_draw = DebugDraw()

        # Game resolution and window
        self.resolution = 6
        self.window_w = WINDOW_W * self.resolution
        self.window_h = WINDOW_H * self.resolution
        self.window_surf = pg.display.set_mode((self.window_w, self.window_h))
        self.y_offset = ((WINDOW_H - NATIVE_H) // 2) * self.resolution

        # Game input flags
        self.is_up_pressed = False
        self.is_down_pressed = False
        self.is_left_pressed = False
        self.is_right_pressed = False

        self.is_up_just_pressed = False
        self.is_down_just_pressed = False
        self.is_left_just_pressed = False
        self.is_right_just_pressed = False

        self.is_up_just_released = False
        self.is_down_just_released = False
        self.is_left_just_released = False
        self.is_right_just_released = False

        self.is_lmb_pressed = False
        self.is_rmb_pressed = False
        self.is_mmb_pressed = False

        self.is_lmb_just_pressed = False
        self.is_rmb_just_pressed = False
        self.is_mmb_just_pressed = False

        self.is_lmb_just_released = False
        self.is_rmb_just_released = False
        self.is_mmb_just_released = False

        self.is_enter_pressed = False
        self.is_pause_pressed = False
        self.is_jump_pressed = False

        self.is_enter_just_pressed = False
        self.is_pause_just_pressed = False
        self.is_jump_just_pressed = False

        self.is_enter_just_released = False
        self.is_pause_just_released = False
        self.is_jump_just_released = False

        # Game keybindings
        self.key_bindings = {
            "up": pg.K_UP,
            "down": pg.K_DOWN,
            "left": pg.K_LEFT,
            "right": pg.K_RIGHT,
            "enter": pg.K_RETURN,
            "pause": pg.K_ESCAPE,
            "jump": pg.K_c,
            # REMOVE IN BUILD
            "lmb": 1,
            "mmb": 2,
            "rmb": 3,
        }

        # All game actors
        self.actors = {
            "fire": Fire,
            "goblin": Goblin
        }

        # All game scenes
        self.scenes = {
            "JsonEditor": JsonEditor,
            "RoomEditor": RoomEditor,
            "World": World
        }

        # Game sound manager
        self.sound_manager = SoundManager()

        # Game current scene
        self.current_scene = self.scenes[initial_scene](self)

    # Call this to change game resolution
    def set_resolution(self, value):
        # Takes values from 1 to 7, 7 == fullscreen
        if value != 7:
            self.resolution = value
            self.window_w = WINDOW_W * self.resolution
            self.window_h = WINDOW_H * self.resolution
            self.window_surf = pg.display.set_mode(
                (self.window_w, self.window_h))
            self.y_offset = ((WINDOW_H - NATIVE_H) // 2) * self.resolution

        elif value == 7:
            self.window_surf = pg.display.set_mode(
                (self.window_w, self.window_h), pg.FULLSCREEN)
            self.resolution = self.window_surf.get_width() // NATIVE_W
            self.window_w = WINDOW_W * self.resolution
            self.window_h = WINDOW_H * self.resolution
            self.y_offset = ((WINDOW_H - NATIVE_H) // 2) * self.resolution

    # Call this to change scene
    def set_scene(self, value):
        self.current_scene = self.scenes[value](self)

    # Exit window / update game input flags
    def event(self, event):
        if event.type == pg.QUIT:
            pg.quit()
            exit()

        if event.type == pg.KEYDOWN:
            if event.key == self.key_bindings["up"]:
                self.is_up_pressed = True
                self.is_up_just_pressed = True
            if event.key == self.key_bindings["down"]:
                self.is_down_pressed = True
                self.is_down_just_pressed = True
            if event.key == self.key_bindings["left"]:
                self.is_left_pressed = True
                self.is_left_just_pressed = True
            if event.key == self.key_bindings["right"]:
                self.is_right_pressed = True
                self.is_right_just_pressed = True
            if event.key == self.key_bindings["enter"]:
                self.is_enter_pressed = True
                self.is_enter_just_pressed = True
            if event.key == self.key_bindings["pause"]:
                self.is_pause_pressed = True
                self.is_pause_just_pressed = True
            if event.key == self.key_bindings["jump"]:
                self.is_jump_pressed = True
                self.is_jump_just_pressed = True

        elif event.type == pg.KEYUP:
            if event.key == self.key_bindings["up"]:
                self.is_up_pressed = False
                self.is_up_just_released = True
            if event.key == self.key_bindings["down"]:
                self.is_down_pressed = False
                self.is_down_just_released = True
            if event.key == self.key_bindings["left"]:
                self.is_left_pressed = False
                self.is_left_just_released = True
            if event.key == self.key_bindings["right"]:
                self.is_right_pressed = False
                self.is_right_just_released = True
            if event.key == self.key_bindings["enter"]:
                self.is_enter_pressed = False
                self.is_enter_just_released = True
            if event.key == self.key_bindings["pause"]:
                self.is_pause_pressed = False
                self.is_pause_just_released = True
            if event.key == self.key_bindings["jump"]:
                self.is_jump_pressed = False
                self.is_jump_just_released = True
            # REMOVE IN BUILD
            if event.key == pg.K_0:
                self.is_debug = not self.is_debug

        # REMOVE IN BUILD
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == self.key_bindings["lmb"]:
                self.is_lmb_pressed = True
                self.is_lmb_just_pressed = True
            if event.button == self.key_bindings["mmb"]:
                self.is_mmb_pressed = True
                self.is_mmb_just_pressed = True
            if event.button == self.key_bindings["rmb"]:
                self.is_rmb_pressed = True
                self.is_rmb_just_pressed = True

        # REMOVE IN BUILD
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == self.key_bindings["lmb"]:
                self.is_lmb_pressed = False
                self.is_lmb_just_released = True
            if event.button == self.key_bindings["mmb"]:
                self.is_mmb_pressed = False
                self.is_mmb_just_released = True
            if event.button == self.key_bindings["rmb"]:
                self.is_rmb_pressed = False
                self.is_rmb_just_released = True
