from constants import *
from nodes.camera import Camera


class JsonEditor:
    def __init__(self, game):
        # Store my dependencies
        self.game = game
        self.sound_manager = game.sound_manager

        # Populate sound manager
        self.sound_manager.load_sound("cursor", WAVS_PATHS["cursor.wav"])
        self.sound_manager.load_sound("cancel", WAVS_PATHS["cancel.wav"])
        self.sound_manager.load_sound("accept", WAVS_PATHS["accept.wav"])
        self.sound_manager.load_sound("success", WAVS_PATHS["success.wav"])

        self.sound_manager.play_sound("cursor")
        self.stage_no = input("Stage no: ")
        self.sound_manager.play_sound("success")

        self.sprite_sheet_path = PNGS_PATHS[f"stage_{
            self.stage_no}_sprite_sheet.png"]
        self.sprite_sheet_surface = pg.image.load(
            self.sprite_sheet_path
        ).convert_alpha()
        self.sprite_sheet_rect = self.sprite_sheet_surface.get_rect()

        self.offset = pg.math.Vector2(0.0, 0.0)

        self.camera = Camera(self.offset)
        self.camera.set_limit(self.sprite_sheet_rect)

        self.camera_speed = 2

        self.bitmask_region_normal_base = [
            [0, 0, 16, 16],
            [16, 0, 16, 16],
            [32, 0, 16, 16],
            [48, 0, 16, 16],
            [64, 0, 16, 16],
            [80, 0, 16, 16],
            [96, 0, 16, 16],
            [112, 0, 16, 16],
            [128, 0, 16, 16],
            [144, 0, 16, 16],

            [0, 16, 16, 16],
            [16, 16, 16, 16],
            [32, 16, 16, 16],
            [48, 16, 16, 16],
            [64, 16, 16, 16],
            [80, 16, 16, 16],
            [96, 16, 16, 16],
            [112, 16, 16, 16],
            [128, 16, 16, 16],
            [144, 16, 16, 16],

            [0, 32, 16, 16],
            [16, 32, 16, 16],
            [32, 32, 16, 16],
            [48, 32, 16, 16],
            [64, 32, 16, 16],
            [80, 32, 16, 16],
            [96, 32, 16, 16],
            [112, 32, 16, 16],
            [128, 32, 16, 16],
            [144, 32, 16, 16],
            [160, 32, 16, 16],

            [0, 48, 16, 16],
            [16, 48, 16, 16],
            [32, 48, 16, 16],
            [48, 48, 16, 16],
            [64, 48, 16, 16],
            [80, 48, 16, 16],
            [96, 48, 16, 16],
            [112, 48, 16, 16],
            [128, 48, 16, 16],
            [144, 48, 16, 16],
            [160, 48, 16, 16],

            [64, 64, 16, 16],
            [80, 64, 16, 16],
            [96, 64, 16, 16],
            [112, 64, 16, 16],
            [128, 64, 16, 16]
        ]

        self.bitmask_region_corner_base = [
            [0, 0, 16, 16],
            0,
            [16, 0, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            [0, 16, 16, 16],
            0,
            [16, 16, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
        ]

        self.bitmask_region_horizontal_base = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            [0, 0, 16, 16],
            [16, 0, 16, 16],
            [32, 0, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
        ]

        self.bitmask_region_vertical_base = [
            0,
            0,
            0,
            [0, 0, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            [0, 16, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            [0, 32, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
        ]

        self.bitmask_region_square_base = [
            [0, 0, 16, 16],
            [16, 0, 16, 16],
            [32, 0, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            [0, 16, 16, 16],
            [16, 16, 16, 16],
            [32, 16, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            [0, 32, 16, 16],
            [16, 32, 16, 16],
            [32, 32, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
        ]

        self.bitmask_region_double_vertical_base = [
            [0, 0, 16, 16],
            0,
            [16, 0, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            [0, 16, 16, 16],
            0,
            [16, 16, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            [0, 32, 16, 16],
            0,
            [16, 32, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
        ]

        self.bitmask_region_double_horizontal_base = [
            [0, 0, 16, 16],
            [16, 0, 16, 16],
            [32, 0, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            [0, 32, 16, 16],
            [16, 32, 16, 16],
            [32, 32, 16, 16],
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,

            0,
            0,
            0,
            0,
            0,
        ]

        self.bitmask_regions = {
            "normal": self.bitmask_region_normal_base,
            "corner": self.bitmask_region_corner_base,
            "horizontal": self.bitmask_region_horizontal_base,
            "vertical": self.bitmask_region_vertical_base,
            "square": self.bitmask_region_square_base,
            "double_vertical": self.bitmask_region_double_vertical_base,
            "double_horizontal": self.bitmask_region_double_horizontal_base
        }

        self.sprites_types = {
            "background": "background",
            "animated_background": "animated_background",
            "solid": "solid",
            "thin": "thin",
            "door": "door",
            "save": "save",
            "actor": "actor",
            "cancel": "cancel",
        }

        self.door_directions = {
            "left": "left",
            "right": "right",
            "up": "up",
            "down": "down",
            "cancel": "cancel",
        }

        self.bitmasks_types = {
            "none": "none",
            "normal": "normal",
            "corner": "corner",
            "horizontal": "horizontal",
            "vertical": "vertical",
            "square": "square",
            "double_vertical": "double_vertical",
            "double_horizontal": "double_horizontal",
            "cancel": "cancel",
        }

        self.binary_types = {
            "yes": "yes",
            "no": "no",
            "cancel": "cancel",
        }

        self.to_be_saved = {
            "sprite_sheet_name": f"stage_{self.stage_no}_sprite_sheet.png",
            "total_layers": 0,
            "solid_layer": 0,
            "actor_layer": 0,
            "sprites": []
        }

        self.start_selection_rect = None
        self.selection_rect = None

        self.state = "setting start rect"

        self.save_path = join(JSONS_DIR_PATH, f"stage_{
                              self.stage_no}_room_editor.json")

    def selectFromDict(self, options, name):
        index = 0
        indexValidList = []
        print("Select a " + name + ":")
        for optionName in options:
            index = index + 1
            indexValidList.extend([options[optionName]])
            print(str(index) + ") " + optionName)
        inputValid = False
        while not inputValid:
            inputRaw = input(name + ": ")
            inputNo = int(inputRaw) - 1
            if inputNo > -1 and inputNo < len(indexValidList):
                selected = indexValidList[inputNo]
                print("Selected " + name + ": " + selected)
                inputValid = True
                break
            else:
                print("Please select a valid " + name + " number")
        return selected

    def mark_sprite_sheet(self, rect, name):
        # rect = selection_rect
        pg.draw.rect(
            self.sprite_sheet_surface,
            "blue",
            rect
        )

        pg.draw.rect(
            self.sprite_sheet_surface,
            "green",
            rect,
            1
        )

    def draw(self):
        NATIVE_SURF.fill("gray50")

        NATIVE_SURF.blit(
            self.sprite_sheet_surface, (
                -self.camera.rect.x, -self.camera.rect.y
            )
        )

        # region Draw cursor
        pos = pg.mouse.get_pos()
        x = pos[0] // self.game.resolution
        y = (pos[1] // self.game.resolution) - (
            self.game.y_offset // self.game.resolution
        )
        x = clamp(
            x, self.sprite_sheet_rect.x, self.sprite_sheet_rect.x + self.sprite_sheet_rect.width
        )
        y = clamp(
            y, self.sprite_sheet_rect.y, self.sprite_sheet_rect.y + self.sprite_sheet_rect.height
        )
        xd = x + self.camera.rect.x
        yd = y + self.camera.rect.y
        xd_tu = xd // TILE_S
        yd_tu = yd // TILE_S
        xds = xd_tu * TILE_S
        yds = yd_tu * TILE_S
        # Remove room offset to be collision index
        x_tu = xd_tu - 0
        y_tu = yd_tu - 0
        # Cursor position global pos
        xs = xds - self.camera.rect.x
        ys = yds - self.camera.rect.y

        pg.draw.rect(NATIVE_SURF, "white", [xs, ys, TILE_S, TILE_S], 1)
        # endregion

        # tu is availbale from here for index access

        if self.state == "setting start rect":
            if self.game.is_lmb_just_pressed:
                x = int(x_tu * TILE_S)
                y = int(y_tu * TILE_S)
                self.start_selection_rect = pg.Rect(x, y, TILE_S, TILE_S)
                self.state = "setting end rect"
                self.sound_manager.play_sound("cursor")

            # Save and quit
            if self.game.is_enter_just_pressed == True:
                # Sanitize
                for sprite in self.to_be_saved["sprites"]:
                    # Not door? no need door direction
                    if sprite["sprite_type"] != "door":
                        sprite.pop("door_direction")

                    # Not bitmask? No need is mix or regions
                    if sprite["sprite_bitmask_type"] == "none":
                        sprite.pop("sprite_is_bitmask_mix")
                        sprite.pop("sprite_regions")
                # Write
                with open(self.save_path, "w") as json_file:
                    dump(self.to_be_saved, json_file)
                pg.quit()
                exit()

        elif self.state == "setting end rect":
            x = int(x_tu * TILE_S)
            y = int(y_tu * TILE_S)
            self.selection_rect = self.start_selection_rect.union(
                [x, y, TILE_S, TILE_S]
            )
            selection_rect_xd = self.selection_rect.x - self.camera.rect.x
            selection_rect_yd = self.selection_rect.y - self.camera.rect.y
            pg.draw.rect(
                NATIVE_SURF, "green", [
                    selection_rect_xd, selection_rect_yd, self.selection_rect.width, self.selection_rect.height
                ], 1
            )

            # Made a mistake, cancel back to selecting start point
            if self.game.is_pause_just_pressed == True:
                self.state = "setting start rect"
                self.sound_manager.play_sound("cancel")

            # Confirm selection, start asking
            if self.game.is_lmb_just_pressed == True:
                self.sound_manager.play_sound("cursor")

                sprite_name = input("Sprite name: ")
                self.sound_manager.play_sound("accept")

                sprite_layer = int(input("Sprite layer: "))
                self.sound_manager.play_sound("accept")

                sprite_type = self.selectFromDict(
                    self.sprites_types, "Sprite type"
                )
                if sprite_type == "cancel":
                    self.sound_manager.play_sound("cancel")
                    return
                self.sound_manager.play_sound("accept")

                sprite_bitmask_type = self.selectFromDict(
                    self.bitmasks_types, "Sprite bitmask type"
                )
                if sprite_bitmask_type == "cancel":
                    self.sound_manager.play_sound("cancel")
                    return
                self.sound_manager.play_sound("accept")

                # Update total layer
                if self.to_be_saved["total_layers"] <= sprite_layer:
                    self.to_be_saved["total_layers"] = sprite_layer + 1

                # Update door layer
                door_directions = ""
                if sprite_type == "door":
                    door_directions = self.selectFromDict(
                        self.door_directions, "Door direction"
                    )
                    if door_directions == "cancel":
                        self.sound_manager.play_sound("cancel")
                        return

                # Update solid layer
                elif sprite_type == "solid":
                    self.to_be_saved["solid_layer"] = sprite_layer

                # Update actor layer
                elif sprite_type == "actor":
                    self.to_be_saved["actor_layer"] = sprite_layer

                # Handle none bitmask type
                if sprite_bitmask_type == "none":
                    sprite_is_bitmask_mix = "none"
                    sprite_region = [
                        self.selection_rect.x,
                        self.selection_rect.y,
                        self.selection_rect.width,
                        self.selection_rect.height,
                    ]
                    sprite_regions = [sprite_region]

                # Handle bitmask type
                else:

                    sprite_is_bitmask_mix = self.selectFromDict(
                        self.binary_types, "Sprite bitmask mix"
                    )
                    if sprite_is_bitmask_mix == "cancel":
                        self.sound_manager.play_sound("cancel")
                        return

                    choosen_bitmask_region = self.bitmask_regions[sprite_bitmask_type]

                    sprite_regions = []
                    for region in choosen_bitmask_region:
                        if region == 0:
                            sprite_regions.append(0)
                        else:
                            sprite_regions.append(
                                [
                                    region[0] + self.selection_rect.x,
                                    region[1] + self.selection_rect.y,
                                    region[2],
                                    region[3],
                                ]
                            )

                # Prepare region
                sprite_region = []
                for region in sprite_regions:
                    if region != 0:
                        sprite_region = region
                        continue

                # Collect this obj
                self.to_be_saved["sprites"].append(
                    {
                        "sprite_name": sprite_name,
                        "sprite_layer": sprite_layer,
                        "sprite_type": sprite_type,
                        "sprite_bitmask_type": sprite_bitmask_type,
                        "sprite_is_bitmask_mix": sprite_is_bitmask_mix,
                        "sprite_regions": sprite_regions,
                        "sprite_region": sprite_region,
                        "door_direction": door_directions
                    }
                )

                # Mark this on sprite sheet
                self.mark_sprite_sheet(
                    self.selection_rect,
                    sprite_name
                )

                self.state = "setting start rect"
                self.sound_manager.play_sound("success")
                print("\n" * 100)

                print(self.to_be_saved)

    def update(self, dt):
        self.offset.x += (
            self.game.is_right_pressed - self.game.is_left_pressed
        ) * self.camera_speed

        self.offset.y += (
            self.game.is_down_pressed - self.game.is_up_pressed
        ) * self.camera_speed

        self.camera.update(dt)
