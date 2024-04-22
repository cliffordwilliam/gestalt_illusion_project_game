import pygame as pg
from os.path import join
import pygame.freetype as font
from pygame.math import Vector2
from pygame.math import lerp
from pygame.math import clamp
from json import dump
from json import load

pg.init()

# Pngs
PNGS_DIR_PATH = "pngs"
PNGS_PATHS = {
    "player_flip_sprite_sheet.png": join(PNGS_DIR_PATH, "player_flip_sprite_sheet.png"),
    "player_sprite_sheet.png": join(PNGS_DIR_PATH, "player_sprite_sheet.png"),
    "stage_1_sprite_sheet.png": join(PNGS_DIR_PATH, "stage_1_sprite_sheet.png"),
    "stage_2_sprite_sheet.png": join(PNGS_DIR_PATH, "stage_2_sprite_sheet.png"),
}

# Jsons
JSONS_DIR_PATH = "jsons"
JSONS_PATHS = {
    "fire_animation.json": join(JSONS_DIR_PATH, "fire_animation.json"),
    "big_flame_animation.json": join(JSONS_DIR_PATH, "big_flame_animation.json"),
    "player_animation.json": join(JSONS_DIR_PATH, "player_animation.json"),
    "stage_1_room_editor.json": join(JSONS_DIR_PATH, "stage_1_room_editor.json"),
    "stage_2_room_editor.json": join(JSONS_DIR_PATH, "stage_2_room_editor.json"),
    "stage_1_bedroom_game.json": join(JSONS_DIR_PATH, "stage_1_bedroom_game.json"),

    # STAGE 2 TEST REMOVE IN BUILD (DEL THE REAL JSON TOO)
    "stage_2_test_game.json": join(JSONS_DIR_PATH, "stage_2_test_game.json"),
}

# Wavs
WAVS_DIR_PATH = "wavs"
WAVS_PATHS = {
    "cursor.wav": join(WAVS_DIR_PATH, "cursor.wav"),
    "cancel.wav": join(WAVS_DIR_PATH, "cancel.wav"),
    "accept.wav": join(WAVS_DIR_PATH, "accept.wav"),
    "success.wav": join(WAVS_DIR_PATH, "success.wav"),
}

# Constants
TILE_S = 16
FPS = 60
NATIVE_W = 320
NATIVE_H = 160
WINDOW_W = 320
WINDOW_H = 180

NATIVE_W_TU = 20
NATIVE_H_TU = 10

# Used for camera draw
NATIVE_W_TU_EXTRA_ONE = 21
NATIVE_H_TU_EXTRA_ONE = 11

# Pg constants
NATIVE_SURF = pg.Surface((NATIVE_W, NATIVE_H))
NATIVE_RECT = NATIVE_SURF.get_rect()

CLOCK = pg.time.Clock()
EVENTS = [pg.KEYDOWN, pg.KEYUP, pg.QUIT]

# REMOVE IN BUILD
EDITOR_EVENTS = [
    pg.KEYDOWN, pg.KEYUP, pg.MOUSEBUTTONUP, pg.MOUSEBUTTONDOWN, pg.QUIT
]

# Font
FONT_H = 5
FONT_W = 3
FONT = font.Font(
    join("ttf", "cg_pixel_3x5_mono.ttf"),
    FONT_H,
)

# The quad layers limit, 8 levels depth
MAX_QUADTREE_DEPTH = 8

# REMOVE IN BUILD
MASK_ID_TO_INDEX = {
    "208": 0,
    "248": 1,
    "104": 2,
    "64": 3,
    "80": 4,
    "120": 5,
    "216": 6,
    "72": 7,
    "88": 8,
    "219": 9,

    "214": 10,
    "255": 11,
    "107": 12,
    "66": 13,
    "86": 14,
    "127": 15,
    "223": 16,
    "75": 17,
    "95": 18,
    "126": 19,

    "22": 20,
    "31": 21,
    "11": 22,
    "2": 23,
    "210": 24,
    "251": 25,
    "254": 26,
    "106": 27,
    "250": 28,
    "218": 29,
    "122": 30,

    "16": 31,
    "24": 32,
    "8": 33,
    "0": 34,
    "18": 35,
    "27": 36,
    "30": 37,
    "10": 38,
    "26": 39,
    "94": 40,
    "91": 41,

    "82": 42,
    "123": 43,
    "222": 44,
    "74": 45,
    "90": 46
}

# Max recursion quadtree
MAX_QUADTREE_DEPTH = 8

# Book to store all quad (section / kid) with their actors
# For quick lookup, to avoid search tree recursion
# Reset the book
actor_to_quad = {}
