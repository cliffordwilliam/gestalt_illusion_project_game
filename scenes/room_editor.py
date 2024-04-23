from constants import *
from nodes.camera import Camera
from nodes.curtain import Curtain
from nodes.background import Background
import copy


class RoomEditor:
    def __init__(self, game):
        # Store my dependencies
        self.game = game
        self.sound_manager = game.sound_manager

        # Populate sound manager
        self.sound_manager.load_sound("cursor", WAVS_PATHS["cursor.wav"])
        self.sound_manager.load_sound("cancel", WAVS_PATHS["cancel.wav"])
        self.sound_manager.load_sound("accept", WAVS_PATHS["accept.wav"])
        self.sound_manager.load_sound("success", WAVS_PATHS["success.wav"])

        # Questions types
        self.binary_types = {
            "yes": "yes",
            "no": "no",
        }

        # Prepare data
        self.room_x_ru = 0
        self.room_y_ru = 0
        self.room_scale_x = 1
        self.room_scale_y = 1
        self.room_name = ""
        self.stage_no = 1
        self.save_path_game = ""
        self.save_path_editor = ""
        self.layers_list = []
        self.desired_background_names = []

        self.sound_manager.play_sound("cursor")
        IS_LOAD = self.selectFromDict(
            self.binary_types, "Load data"
        )

        # Load data
        if IS_LOAD == "yes":
            # Room name to be loaded?
            self.sound_manager.play_sound("accept")

            self.room_name = input("Enter room_name: ")
            self.sound_manager.play_sound("accept")

            self.stage_no = int(input("Enter stage_no: "))
            self.sound_manager.play_sound("accept")

            # Prepare path from room name
            self.save_path_game = join(
                JSONS_DIR_PATH, f"stage_{self.stage_no}_{
                    self.room_name}_game.json"
            )
            self.save_path_editor = join(
                JSONS_DIR_PATH, f"stage_{self.stage_no}_{
                    self.room_name}_editor.json"
            )

            # Load data
            with open(self.save_path_editor, "r") as data:
                room_data = load(data)
            self.room_x_ru = room_data["room_x_ru"]
            self.room_y_ru = room_data["room_y_ru"]
            self.room_scale_x = room_data["room_scale_x"]
            self.room_scale_y = room_data["room_scale_y"]
            self.stage_no = room_data["stage_no"]
            self.layers_list = room_data["layers_list"]
            self.desired_background_names = room_data["desired_background_names"]

        # Do not load data
        elif IS_LOAD == "no":
            # Use user input to populate data
            self.sound_manager.play_sound("accept")

            self.room_name = input("Enter room_name: ")
            self.sound_manager.play_sound("accept")

            self.stage_no = int(input("Enter stage_no: "))
            self.sound_manager.play_sound("accept")

            self.room_x_ru = int(input("Enter room_x_ru: "))
            self.sound_manager.play_sound("accept")

            self.room_y_ru = int(input("Enter room_y_ru: "))
            self.sound_manager.play_sound("accept")

            self.room_scale_x = int(input("Enter room_scale_x: "))
            self.sound_manager.play_sound("accept")

            self.room_scale_y = int(input("Enter room_scale_y: "))
            self.sound_manager.play_sound("accept")

            self.save_path_game = join(
                JSONS_DIR_PATH, f"stage_{self.stage_no}_{
                    self.room_name}_game.json"
            )
            self.save_path_editor = join(
                JSONS_DIR_PATH, f"stage_{self.stage_no}_{
                    self.room_name}_editor.json"
            )

        # Get my editor data based on input stage number
        with open(
            JSONS_PATHS[f"stage_{self.stage_no}_room_editor.json"], "r"
        ) as data:
            stage_data = load(data)
        self.sprite_sheet_name = stage_data["sprite_sheet_name"]
        self.total_layers = stage_data["total_layers"]
        self.solid_layer = stage_data["solid_layer"]
        self.actor_layer = stage_data["actor_layer"]
        self.sprites = stage_data["sprites"]
        self.sprites_len = len(self.sprites)

        # Move this
        self.offset = Vector2(0.0, 0.0)

        # Camera follows the offset
        self.camera = Camera(self.offset)
        self.camera_speed = 2

        # Get stage sprite sheet
        self.sprite_sheet_path = PNGS_PATHS[f"{self.sprite_sheet_name}"]
        self.sprite_sheet_surface = pg.image.load(
            self.sprite_sheet_path
        ).convert_alpha()

        # Get room
        self.room_x_tu = self.room_x_ru * NATIVE_W_TU
        self.room_y_tu = self.room_y_ru * NATIVE_H_TU
        self.room_w_tu = self.room_scale_x * NATIVE_W_TU
        self.room_h_tu = self.room_scale_y * NATIVE_H_TU
        self.room_rect = pg.Rect(
            self.room_x_tu * TILE_S, self.room_y_tu * TILE_S,
            self.room_w_tu * TILE_S, self.room_h_tu * TILE_S
        )

        # Bring offset to room tl
        self.offset.x = self.room_rect.x + (self.camera.rect.width // 2)
        self.offset.y = self.room_rect.y + (self.camera.rect.height // 2)
        self.camera.set_limit(self.room_rect)

        # Setup the layers of rooms from loaded or empty
        if IS_LOAD == "no":
            self.layers_list = [
                [0] * (self.room_w_tu * self.room_h_tu) for _ in range(self.total_layers)
            ]

        # Menu lookup
        self.menu_collisions = [0 for _ in range(NATIVE_W_TU * NATIVE_H_TU)]

        # Collect animation data for this stage
        self.animation_data = {}

        # Draw menu surface
        self.menu_surface = pg.Surface((NATIVE_W, NATIVE_H))
        self.menu_surface.fill("grey50")
        for i in range(self.sprites_len):
            sprite = self.sprites[i]
            x_tu = i % NATIVE_W_TU
            y_tu = i // NATIVE_W_TU
            x = x_tu * TILE_S
            y = y_tu * TILE_S
            self.menu_collisions[i] = sprite

            region = sprite["sprite_region"]

            self.menu_surface.blit(
                self.sprite_sheet_surface, (x, y), [
                    region[0], region[1], 16, 16
                ]
            )
            for i in range(NATIVE_W_TU + 1):
                v = TILE_S * i
                pg.draw.line(self.menu_surface, "grey58",
                             (v, 0), (v, NATIVE_H))
                pg.draw.line(self.menu_surface, "grey58",
                             (0, v), (NATIVE_W, v))

            # Find animated sprites
            if sprite["sprite_type"] == "animated_background":
                # Load the animation data for this sprite
                with open(
                    JSONS_PATHS[f"{sprite["sprite_name"]}_animation.json"], "r"
                ) as data:
                    animation_data = load(data)

                # Collect it
                self.animation_data[sprite["sprite_name"]] = animation_data

        self.selected_sprite = self.menu_collisions[0]
        self.selected_layer = self.layers_list[self.selected_sprite["sprite_layer"]]

        self.start_selection_rect = None
        self.selection_rect = None

        self.game = game

        self.bg_color = "#7f7f7f"

        self.curtain = Curtain(100, "invisible")
        self.curtain.add_event_listener(
            self.on_curtain_invisible, "invisible_end"
        )
        self.curtain.add_event_listener(
            self.on_curtain_opaque, "opaque_end"
        )

        self.state = "normal"

        # This one cannot be saved to json needs to be hardcoded or saved to const

        if IS_LOAD == "no":
            # Handle bg options
            if self.stage_no == 1:
                is_sky = self.selectFromDict(
                    self.binary_types, "Sky background"
                )
                self.sound_manager.play_sound("accept")

                is_clouds = self.selectFromDict(
                    self.binary_types, "Clouds background"
                )
                self.sound_manager.play_sound("accept")

                is_temple = self.selectFromDict(
                    self.binary_types, "Temple background"
                )
                self.sound_manager.play_sound("accept")

                is_trees = self.selectFromDict(
                    self.binary_types, "Trees background"
                )
                self.sound_manager.play_sound("accept")

                is_blue_glow = self.selectFromDict(
                    self.binary_types, "Blue glow background"
                )
                self.sound_manager.play_sound("success")

                if is_sky == "yes":
                    self.desired_background_names.append("sky")

                if is_clouds == "yes":
                    self.desired_background_names.append("clouds")

                if is_temple == "yes":
                    self.desired_background_names.append("temple")

                if is_trees == "yes":
                    self.desired_background_names.append("trees")

                if is_blue_glow == "yes":
                    self.desired_background_names.append("blue_glow")

            elif self.stage_no == 2:
                is_rock = self.selectFromDict(
                    self.binary_types, "Rock background"
                )
                self.sound_manager.play_sound("accept")

                is_orange_glow = self.selectFromDict(
                    self.binary_types, "Orange glow background"
                )
                self.sound_manager.play_sound("success")

                if is_rock == "yes":
                    self.desired_background_names.append("rock")

                if is_orange_glow == "yes":
                    self.desired_background_names.append("orange_glow")

        self.background = Background(
            self.sprite_sheet_surface,
            self.camera,
            self.stage_no,
            self.desired_background_names
        )

        # Loop over each item and instance the background actor
        for i in range(self.total_layers):
            # Handle each room in all layers
            layer = self.layers_list[i]

            # Remove uneeded things for ingame render
            for sprite in layer:
                if sprite != 0:

                    # Is this animated_background?
                    if sprite["sprite_type"] == "animated_background":
                        # Add a new pair instance
                        sprite["instance"] = self.game.actors[sprite["sprite_name"]](
                            self.sprite_sheet_surface,
                            self.animation_data[sprite["sprite_name"]],
                            self.camera,
                            sprite["xds"],
                            sprite["yds"]
                        )

    def update_bitmasks(self, x_tu, y_tu, xds, yds, last=False):
        # Raw bits
        br, b, bl, r, l, tr, t, tl = 0, 0, 0, 0, 0, 0, 0, 0

        # Check my neighbour positions
        neighbour_pos_tu = [
            (x_tu - 1, y_tu - 1), (x_tu - 0, y_tu - 1), (x_tu + 1, y_tu - 1),
            (x_tu - 1, y_tu - 0),                       (x_tu + 1, y_tu - 0),
            (x_tu - 1, y_tu + 1), (x_tu - 0, y_tu + 1), (x_tu + 1, y_tu + 1)
        ]

        # Top and bottom checks only
        if self.selected_sprite["sprite_bitmask_type"] in "vertical":
            neighbour_pos_tu = [
                (x_tu - 0, y_tu - 1),
                (x_tu - 0, y_tu + 1),
            ]

        # Left and right checks only
        elif self.selected_sprite["sprite_bitmask_type"] in "horizontal":
            neighbour_pos_tu = [
                (x_tu - 1, y_tu - 0), (x_tu + 1, y_tu - 0),
            ]

        # Check each nenighbour position
        for pos in neighbour_pos_tu:
            # Get tile from collision list
            neighbour_x_tu = pos[0]
            neighbour_y_tu = pos[1]

            # Make sure that pos is inside the list
            if (0 <= neighbour_x_tu < self.room_w_tu) and (0 <= neighbour_y_tu < self.room_h_tu):
                neighbour = self.selected_layer[
                    neighbour_y_tu *
                    self.room_w_tu + neighbour_x_tu
                ]

                # Air? check other position
                if neighbour == 0:
                    continue

                # I do not mix?
                if self.selected_sprite["sprite_bitmask_type"] == "none":
                    continue

                # I do not mix?
                if self.selected_sprite["sprite_is_bitmask_mix"] == "no":
                    # Neighbour diff name than me? look for someone else
                    if self.selected_sprite["sprite_name"] != neighbour["sprite_name"]:
                        continue

                # Found! Tell my neighbour to update bitmask
                if last == False:
                    self.update_bitmasks(
                        neighbour_x_tu, neighbour_y_tu,
                        neighbour["xds"], neighbour["yds"],
                        last=True
                    )

                # Cook bitmask -> mask_id
                dx = neighbour_x_tu - x_tu
                dy = neighbour_y_tu - y_tu
                t += dx == 0 and dy == -1
                r += dx == 1 and dy == 0
                b += dx == 0 and dy == 1
                l += dx == -1 and dy == 0
                br += dx == 1 and dy == 1
                bl += dx == -1 and dy == 1
                tr += dx == 1 and dy == -1
                tl += dx == -1 and dy == -1
        tr = tr and t and r
        tl = tl and t and l
        br = br and b and r
        bl = bl and b and l

        mask_id = (br << 7) | (b << 6) | (bl << 5) | (
            r << 4) | (l << 3) | (tr << 2) | (t << 1) | tl

        # Update region of this tile with cooked bitmask
        sprite = self.selected_layer[y_tu * self.room_w_tu + x_tu]

        # In case this tile is from deleted draw, then I cannot update this tile
        if sprite != 0:
            if sprite["sprite_bitmask_type"] != "none":
                # Turn mask id to index for region access
                i = MASK_ID_TO_INDEX[str(mask_id)]
                new_region = sprite["sprite_regions"][i]
                if new_region != 0:
                    self.selected_layer[
                        y_tu * self.room_w_tu + x_tu
                    ]["sprite_region"] = new_region

    def bucket_fill(self, x_tu, y_tu, xds, yds):
        # Create a blink effect on tile that mask about to change

        # Check my neighbours, but not corners
        neighbour_pos_tu = [
            (x_tu - 0, y_tu - 1), (x_tu - 1, y_tu - 0),
            (x_tu + 1, y_tu - 0), (x_tu - 0, y_tu + 1)
        ]
        for pos in neighbour_pos_tu:
            # Get tile from collision list
            neighbour_x_tu = pos[0]
            neighbour_y_tu = pos[1]

            # Make sure that pos is inside the list
            if (0 <= neighbour_x_tu < self.room_w_tu) and (0 <= neighbour_y_tu < self.room_h_tu):
                neighbour = self.selected_layer[
                    neighbour_y_tu *
                    self.room_w_tu + neighbour_x_tu
                ]

                # Air? Instance new sprite
                if neighbour == 0:
                    # Prepare real draw positions
                    neighbour_xd_tu = neighbour_x_tu + self.room_x_tu
                    neighbour_yd_tu = neighbour_y_tu + self.room_y_tu
                    neighbour_xds = neighbour_xd_tu * TILE_S
                    neighbour_yds = neighbour_yd_tu * TILE_S

                    # Instance new sprite
                    new_sprite = self.selected_sprite.copy()
                    new_sprite["xds"] = neighbour_xds
                    new_sprite["yds"] = neighbour_yds
                    self.selected_layer[
                        neighbour_y_tu *
                        self.room_w_tu + neighbour_x_tu
                    ] = new_sprite

                    # Tell my neighbour to fill
                    self.bucket_fill(
                        neighbour_x_tu, neighbour_y_tu,
                        neighbour_xds, neighbour_yds,
                    )

                    # Update bistmasks if it is bitmask type
                    if new_sprite["sprite_bitmask_type"] != "none":
                        self.update_bitmasks(
                            neighbour_x_tu, neighbour_y_tu,
                            neighbour_xds, neighbour_yds
                        )

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

    def on_curtain_invisible(self):
        pass

    def on_curtain_opaque(self):
        # Curtain closed, set new state
        if self.state == "normal":
            self.set_state("menu")

        elif self.state == "menu":
            self.set_state("normal")

        # New state is here, open curtain
        self.curtain.go_to_invisible()

    def draw(self):
        if self.state == "normal":
            NATIVE_SURF.fill("gray50")

            self.background.draw()

            # region Draw grid
            for i in range(NATIVE_W_TU):
                offset = TILE_S * i
                xd = (offset - self.camera.rect.x) % NATIVE_W
                yd = (offset - self.camera.rect.y) % NATIVE_H
                pg.draw.line(NATIVE_SURF, "grey58", (xd, 0), (xd, NATIVE_H))
                pg.draw.line(NATIVE_SURF, "grey58", (0, yd), (NATIVE_W, yd))
            xd = -self.camera.rect.x % NATIVE_W
            yd = -self.camera.rect.y % NATIVE_H
            pg.draw.line(NATIVE_SURF, "grey66", (xd, 0), (xd, NATIVE_H))
            pg.draw.line(NATIVE_SURF, "grey66", (0, yd), (NATIVE_W, yd))
            FONT.render_to(
                NATIVE_SURF, (xd + FONT_W, yd + FONT_H), f"{
                    (int(self.camera.rect.x) - 1) // NATIVE_W + 1}{
                    (int(self.camera.rect.y) - 1) // NATIVE_H + 1}", "grey100"
            )
            # endregion

            # region Cam pos -> indexes -> get tile and draw them
            # Turn coord into tu
            cam_x_tu = self.camera.rect.x // TILE_S
            cam_y_tu = self.camera.rect.y // TILE_S

            # Turn tu into index, by sub cam offset
            cam_x_tu = int(cam_x_tu - self.room_x_tu)
            cam_y_tu = int(cam_y_tu - self.room_y_tu)

            for layer in self.layers_list:
                # Iterate over rows
                for row in range(11):  # NATIVE_H_TU + 1
                    # Iterate over columns
                    for col in range(21):  # NATIVE_W_TU + 1
                        # Calculate index for the current tile
                        index = (cam_y_tu + row) * \
                            self.room_w_tu + (cam_x_tu + col)

                        # Makes sure its in index
                        if 0 <= index < len(layer):
                            # Get item and grab its draw pos
                            item = layer[index]

                            # Find air? Continue
                            if item == 0:
                                continue

                            # Found actor? let it draw itself
                            if item["sprite_type"] == "animated_background":
                                instance = item["instance"]
                                instance.draw()
                                continue

                            xd = item["xds"] - self.camera.rect.x
                            yd = item["yds"] - self.camera.rect.y

                            NATIVE_SURF.blit(
                                self.sprite_sheet_surface,
                                (xd, yd),
                                item["sprite_region"]
                            )
            # endregion Cam pos -> indexes -> get tile and draw them

            # region Draw cursor
            pos = pg.mouse.get_pos()
            x = pos[0] // self.game.resolution
            y = (pos[1] // self.game.resolution) - (
                self.game.y_offset // self.game.resolution
            )
            # 0 - 9
            x = clamp(
                x, NATIVE_RECT.x, NATIVE_RECT.x + NATIVE_RECT.width
            )
            # 0 - 19
            y = clamp(
                y, NATIVE_RECT.y, NATIVE_RECT.y + NATIVE_RECT.height - TILE_S
            )

            xd = x + self.camera.rect.x
            yd = y + self.camera.rect.y
            xd_tu = xd // TILE_S
            yd_tu = yd // TILE_S
            xds = xd_tu * TILE_S
            yds = yd_tu * TILE_S
            # Remove room offset to be collision index
            # x_tu = xd_tu - self.room_x_tu
            # y_tu = yd_tu - self.room_y_tu
            # Cursor position global pos
            xs = xds - self.camera.rect.x
            ys = yds - self.camera.rect.y
            w = self.selected_sprite["sprite_region"][2]
            h = self.selected_sprite["sprite_region"][3]

            pg.draw.rect(NATIVE_SURF, "green", [xs, ys, w, h], 1)
            # endregion Draw cursor

        elif self.state == "menu":
            NATIVE_SURF.fill("gray50")

            # Draw menu surface
            NATIVE_SURF.blit(self.menu_surface, (0, 0))

            # region Draw cursor
            pos = pg.mouse.get_pos()
            x = pos[0] // self.game.resolution
            y = (pos[1] // self.game.resolution) - (
                self.game.y_offset // self.game.resolution
            )
            # 0 - 9
            x = clamp(
                x, NATIVE_RECT.x, NATIVE_RECT.x + NATIVE_RECT.width
            )
            # 0 - 19
            y = clamp(
                y, NATIVE_RECT.y, NATIVE_RECT.y + NATIVE_RECT.height - TILE_S
            )

            x_tu = x // TILE_S
            y_tu = y // TILE_S
            xs = x_tu * TILE_S
            ys = y_tu * TILE_S

            pg.draw.rect(NATIVE_SURF, "white", [xs, ys, TILE_S, TILE_S], 1)

            item = self.menu_collisions[
                y_tu * NATIVE_W_TU + x_tu
            ]

            if item != 0:
                pg.draw.rect(NATIVE_SURF, "green", [xs, ys, TILE_S, TILE_S], 1)
            # endregion Draw cursor

        self.curtain.draw()

    def update(self, dt):
        if self.state == "normal":
            # Do not update when curtain is lerping
            if self.curtain.is_done_lerping == True:

                # Update animation background

                # region Cam pos -> indexes -> get tile and draw them
                # Turn coord into tu
                cam_x_tu = self.camera.rect.x // TILE_S
                cam_y_tu = self.camera.rect.y // TILE_S

                # Turn tu into index, by sub cam offset
                cam_x_tu = int(cam_x_tu - self.room_x_tu)
                cam_y_tu = int(cam_y_tu - self.room_y_tu)

                for layer in self.layers_list:
                    # Iterate over rows
                    for row in range(11):  # NATIVE_H_TU + 1
                        # Iterate over columns
                        for col in range(21):  # NATIVE_W_TU + 1
                            # Calculate index for the current tile
                            index = (cam_y_tu + row) * \
                                self.room_w_tu + (cam_x_tu + col)

                            # Makes sure its in index
                            if 0 <= index < len(layer):
                                # Get item and grab its draw pos
                                item = layer[index]

                                # Find air? Continue
                                if item == 0:
                                    continue

                                # Found actor? let it draw itself
                                if item["sprite_type"] == "animated_background":
                                    instance = item["instance"]
                                    instance.update(dt)
                                    continue

                # Tap enter?
                if self.game.is_enter_just_pressed == True:

                    for i in range(self.total_layers):
                        # Handle each room in all layers
                        layer = self.layers_list[i]

                        # Remove uneeded things for ingame render
                        for sprite in layer:
                            if sprite != 0:

                                # An animated_background? Remove the instance pair, add it later, this cannot be json saved
                                if sprite["sprite_type"] == "animated_background":
                                    sprite.pop("instance")

                    # Save current editor state
                    to_be_saved_editor = {
                        "room_x_ru": self.room_x_ru,
                        "room_y_ru": self.room_y_ru,
                        "room_scale_x": self.room_scale_x,
                        "room_scale_y": self.room_scale_y,
                        "stage_no": self.stage_no,
                        "layers_list": self.layers_list,
                        "desired_background_names": self.desired_background_names
                    }
                    with open(self.save_path_editor, "w") as json_file:
                        dump(
                            to_be_saved_editor,
                            json_file
                        )

                    background_layer = []
                    solid_layer = []
                    actor_layer = []
                    foreground_layer = []

                    for i in range(self.total_layers):
                        # Handle each room in all layers
                        layer = self.layers_list[i]

                        # Actor layer?
                        if i == self.actor_layer:
                            # Remove zeroes, actors move so cannot use static grid lookup
                            layer = [x for x in layer if x != 0]

                        # Remove uneeded things for ingame render
                        for sprite in layer:
                            if sprite != 0:
                                # No one needs layer
                                sprite.pop("sprite_layer")

                                # A bitmask? Remove the mix and regions
                                if sprite["sprite_bitmask_type"] != "none":
                                    sprite.pop("sprite_is_bitmask_mix")
                                    sprite.pop("sprite_regions")

                                # No need to know its type now
                                sprite.pop("sprite_bitmask_type")
                                # If not door no need door direction

                        # Populate
                        if i == self.actor_layer:
                            actor_layer = layer
                        else:
                            if i < self.solid_layer:
                                background_layer.append(layer)
                            elif i == self.solid_layer:
                                solid_layer = layer
                            elif i > self.solid_layer:
                                foreground_layer.append(layer)

                    # Save created room data to be used in game
                    to_be_saved_editor = {
                        "actor_layer": actor_layer,
                        "background_layer": background_layer,
                        "solid_layer": solid_layer,
                        "foreground_layer": foreground_layer,
                        "room_rect": [self.room_rect.x, self.room_rect.y, self.room_rect.width, self.room_rect.height],
                        "sprite_sheet_name": self.sprite_sheet_name,
                        "desired_background_names": self.desired_background_names,
                        "stage_no": self.stage_no,
                    }
                    with open(self.save_path_game, "w") as json_file:
                        dump(
                            to_be_saved_editor,
                            json_file
                        )

                    # Exit
                    pg.quit()
                    exit()

                # Tap pause?
                if self.game.is_pause_just_pressed == True:
                    # Curtain go to opaque
                    self.sound_manager.play_sound("accept")
                    self.curtain.go_to_opaque()
                    return

                # Not pressing jump
                elif not self.game.is_jump_pressed:
                    # Held lmb on canvas?
                    if self.game.is_lmb_pressed:
                        # Get mouse positions
                        pos = pg.mouse.get_pos()
                        x = pos[0] // self.game.resolution
                        y = (pos[1] // self.game.resolution) - (
                            self.game.y_offset // self.game.resolution
                        )
                        # 0 - 9
                        x = clamp(
                            x, NATIVE_RECT.x, NATIVE_RECT.x + NATIVE_RECT.width
                        )
                        # 0 - 19
                        y = clamp(
                            y, NATIVE_RECT.y, NATIVE_RECT.y + NATIVE_RECT.height - TILE_S
                        )

                        xd = x + self.camera.rect.x
                        yd = y + self.camera.rect.y
                        xd_tu = xd // TILE_S
                        yd_tu = yd // TILE_S
                        xds = xd_tu * TILE_S
                        yds = yd_tu * TILE_S
                        # Remove room offset to be collision index
                        x_tu = int(xd_tu - self.room_x_tu)
                        y_tu = int(yd_tu - self.room_y_tu)
                        # Cursor position global pos
                        xs = xds - self.camera.rect.x
                        ys = yds - self.camera.rect.y
                        w = self.selected_sprite["sprite_region"][2]
                        h = self.selected_sprite["sprite_region"][3]

                        # Mouse position -> index -> get item in selected layer
                        item = self.selected_layer[y_tu *
                                                   self.room_w_tu + x_tu]

                        # Can only draw on 0, empty cells only
                        if item == 0:
                            # Check if sprite right side and bottom side does not overshoot room rect
                            r = xds + self.selected_sprite["sprite_region"][2]
                            b = yds + self.selected_sprite["sprite_region"][3]
                            # Does not overshoot? Copy selected and insert to selected layer
                            if not r > self.room_rect.right and not b > self.room_rect.bottom:

                                # Check first if any part of body overlap
                                for y in range(self.selected_sprite["sprite_region"][3] // TILE_S):
                                    for x in range(self.selected_sprite["sprite_region"][2] // TILE_S):

                                        yc = y_tu + y
                                        xc = x_tu + x

                                        # Check if it is occupied
                                        cell = self.selected_layer[
                                            yc * self.room_w_tu + xc
                                        ]

                                        # If the body is overlapping occupied cell, return
                                        if cell != 0:
                                            return

                                # Here, body does not overlap, free to insert

                                # If this sprite w or h is bigger than 1 tile, chop into 1 tile and add to layers list
                                for y in range(self.selected_sprite["sprite_region"][3] // TILE_S):
                                    for x in range(self.selected_sprite["sprite_region"][2] // TILE_S):
                                        new_sprite = copy.deepcopy(
                                            self.selected_sprite
                                        )

                                        new_sprite["xds"] = xds + (x * TILE_S)
                                        new_sprite["yds"] = yds + (y * TILE_S)

                                        new_sprite["sprite_region"][0] += (
                                            x * TILE_S)
                                        new_sprite["sprite_region"][1] += (
                                            y * TILE_S)

                                        new_sprite["sprite_region"][2] = TILE_S
                                        new_sprite["sprite_region"][3] = TILE_S

                                        yc = y_tu + y
                                        xc = x_tu + x

                                        # Check if it is occupied
                                        cell = self.selected_layer[
                                            yc * self.room_w_tu + xc
                                        ]

                                        # If the body is overlapping occupied cell, return
                                        if cell != 0:
                                            return

                                        # Is this animated_background?
                                        if new_sprite["sprite_type"] == "animated_background":

                                            # Add a new pair instance
                                            new_sprite["instance"] = self.game.actors[new_sprite["sprite_name"]](
                                                self.sprite_sheet_surface,
                                                self.animation_data[new_sprite["sprite_name"]],
                                                self.camera,
                                                new_sprite["xds"],
                                                new_sprite["yds"]
                                            )

                                        self.selected_layer[
                                            yc * self.room_w_tu + xc
                                        ] = new_sprite

                                # If this sprite has bitmask type, then update it
                                if new_sprite["sprite_bitmask_type"] != "none":
                                    self.update_bitmasks(x_tu, y_tu, xds, yds)

                                self.sound_manager.play_sound("cursor")

                    # Held rmb on canvas?
                    elif self.game.is_rmb_pressed:
                        # Get mouse positions
                        pos = pg.mouse.get_pos()
                        x = pos[0] // self.game.resolution
                        y = (pos[1] // self.game.resolution) - (
                            self.game.y_offset // self.game.resolution
                        )
                        # 0 - 9
                        x = clamp(
                            x, NATIVE_RECT.x, NATIVE_RECT.x + NATIVE_RECT.width
                        )
                        # 0 - 19
                        y = clamp(
                            y, NATIVE_RECT.y, NATIVE_RECT.y + NATIVE_RECT.height - TILE_S
                        )

                        xd = x + self.camera.rect.x
                        yd = y + self.camera.rect.y
                        xd_tu = xd // TILE_S
                        yd_tu = yd // TILE_S
                        xds = xd_tu * TILE_S
                        yds = yd_tu * TILE_S
                        # Remove room offset to be collision index
                        x_tu = int(xd_tu - self.room_x_tu)
                        y_tu = int(yd_tu - self.room_y_tu)
                        # Cursor position global pos
                        xs = xds - self.camera.rect.x
                        ys = yds - self.camera.rect.y
                        w = self.selected_sprite["sprite_region"][2]
                        h = self.selected_sprite["sprite_region"][3]

                        # Mouse position -> index -> get item in selected layer
                        item = self.selected_layer[y_tu *
                                                   self.room_w_tu + x_tu]

                        # Found occupied cell?
                        if item != 0:
                            self.selected_layer[
                                y_tu * self.room_w_tu + x_tu
                            ] = 0

                            # If this sprite has bitmask type, then update it
                            if item["sprite_bitmask_type"] != "none":
                                self.update_bitmasks(x_tu, y_tu, xds, yds)

                            self.sound_manager.play_sound("cancel")

                    # Just pressed mmb on canvas?
                    elif self.game.is_mmb_just_pressed:
                        # Get mouse positions
                        pos = pg.mouse.get_pos()
                        x = pos[0] // self.game.resolution
                        y = (pos[1] // self.game.resolution) - (
                            self.game.y_offset // self.game.resolution
                        )
                        # 0 - 9
                        x = clamp(
                            x, NATIVE_RECT.x, NATIVE_RECT.x + NATIVE_RECT.width
                        )
                        # 0 - 19
                        y = clamp(
                            y, NATIVE_RECT.y, NATIVE_RECT.y + NATIVE_RECT.height - TILE_S
                        )

                        xd = x + self.camera.rect.x
                        yd = y + self.camera.rect.y
                        xd_tu = xd // TILE_S
                        yd_tu = yd // TILE_S
                        xds = xd_tu * TILE_S
                        yds = yd_tu * TILE_S
                        # Remove room offset to be collision index
                        x_tu = int(xd_tu - self.room_x_tu)
                        y_tu = int(yd_tu - self.room_y_tu)
                        # Cursor position global pos
                        xs = xds - self.camera.rect.x
                        ys = yds - self.camera.rect.y
                        w = self.selected_sprite["sprite_region"][2]
                        h = self.selected_sprite["sprite_region"][3]

                        # Mouse position -> index -> get item in selected layer
                        item = self.selected_layer[y_tu *
                                                   self.room_w_tu + x_tu]

                        # Found empty cell?
                        if item == 0:
                            # Check if sprite right side and bottom side does not overshoot room rect
                            r = xds + self.selected_sprite["sprite_region"][2]
                            b = yds + self.selected_sprite["sprite_region"][3]
                            # Does not overshoot? Copy selected and insert to selected layer
                            if not r > self.room_rect.right and not b > self.room_rect.bottom:

                                # Check first if any part of body overlap
                                for y in range(self.selected_sprite["sprite_region"][3] // TILE_S):
                                    for x in range(self.selected_sprite["sprite_region"][2] // TILE_S):

                                        yc = y_tu + y
                                        xc = x_tu + x

                                        # Check if it is occupied
                                        cell = self.selected_layer[
                                            yc * self.room_w_tu + xc
                                        ]

                                        # If the body is overlapping occupied cell, return
                                        if cell != 0:
                                            return

                                # Here, body does not overlap, free to insert

                                # If this sprite w or h is bigger than 1 tile, chop into 1 tile and add to layers list
                                for y in range(self.selected_sprite["sprite_region"][3] // TILE_S):
                                    for x in range(self.selected_sprite["sprite_region"][2] // TILE_S):
                                        new_sprite = copy.deepcopy(
                                            self.selected_sprite
                                        )

                                        new_sprite["xds"] = xds + (x * TILE_S)
                                        new_sprite["yds"] = yds + (y * TILE_S)

                                        new_sprite["sprite_region"][0] += (
                                            x * TILE_S)
                                        new_sprite["sprite_region"][1] += (
                                            y * TILE_S)

                                        new_sprite["sprite_region"][2] = TILE_S
                                        new_sprite["sprite_region"][3] = TILE_S

                                        yc = y_tu + y
                                        xc = x_tu + x

                                        # Check if it is occupied
                                        cell = self.selected_layer[
                                            yc * self.room_w_tu + xc
                                        ]

                                        # If the body is overlapping occupied cell, return
                                        if cell != 0:
                                            return

                                        self.selected_layer[
                                            yc * self.room_w_tu + xc
                                        ] = new_sprite

                                self.bucket_fill(x_tu, y_tu, xds, yds)

                                # If this sprite has bitmask type, then update it
                                if new_sprite["sprite_bitmask_type"] != "none":
                                    self.update_bitmasks(x_tu, y_tu, xds, yds)

                                self.sound_manager.play_sound("cursor")

                # Held lmb on canvas?
                elif self.game.is_jump_pressed:
                    if self.game.is_lmb_just_pressed:
                        pos = pg.mouse.get_pos()
                        x = pos[0] // self.game.resolution
                        y = (pos[1] // self.game.resolution) - (
                            self.game.y_offset // self.game.resolution
                        )
                        # 0 - 9
                        x = clamp(
                            x, NATIVE_RECT.x, NATIVE_RECT.x + NATIVE_RECT.width
                        )
                        # 0 - 19
                        y = clamp(
                            y, NATIVE_RECT.y, NATIVE_RECT.y + NATIVE_RECT.height - TILE_S
                        )

                        xd = x + self.camera.rect.x
                        yd = y + self.camera.rect.y
                        xd_tu = xd // TILE_S
                        yd_tu = yd // TILE_S
                        xds = xd_tu * TILE_S
                        yds = yd_tu * TILE_S
                        # Remove room offset to be collision index
                        # x_tu = xd_tu - self.room_x_tu
                        # y_tu = yd_tu - self.room_y_tu
                        # Cursor position global pos
                        xs = xds - self.camera.rect.x
                        ys = yds - self.camera.rect.y
                        # w = self.selected_sprite["sprite_region"][2]
                        # h = self.selected_sprite["sprite_region"][3]

                        # pg.draw.rect(NATIVE_SURF, "green", [xs, ys, w, h], 1)

                        self.start_selection_rect = pg.Rect(
                            xds, yds, TILE_S, TILE_S
                        )

                    elif self.game.is_lmb_pressed:
                        pos = pg.mouse.get_pos()
                        x = pos[0] // self.game.resolution
                        y = (pos[1] // self.game.resolution) - (
                            self.game.y_offset // self.game.resolution
                        )
                        # 0 - 9
                        x = clamp(
                            x, NATIVE_RECT.x, NATIVE_RECT.x + NATIVE_RECT.width
                        )
                        # 0 - 19
                        y = clamp(
                            y, NATIVE_RECT.y, NATIVE_RECT.y + NATIVE_RECT.height - TILE_S
                        )

                        xd = x + self.camera.rect.x
                        yd = y + self.camera.rect.y
                        xd_tu = xd // TILE_S
                        yd_tu = yd // TILE_S
                        xds = xd_tu * TILE_S
                        yds = yd_tu * TILE_S
                        # Remove room offset to be collision index
                        # x_tu = xd_tu - self.room_x_tu
                        # y_tu = yd_tu - self.room_y_tu
                        # Cursor position global pos
                        xs = xds - self.camera.rect.x
                        ys = yds - self.camera.rect.y
                        # w = self.selected_sprite["sprite_region"][2]
                        # h = self.selected_sprite["sprite_region"][3]

                        # pg.draw.rect(NATIVE_SURF, "green", [xs, ys, w, h], 1)

                        # end_selection_rect = pg.Rect(
                        #     xds, yds, TILE_S, TILE_S
                        # )

                        self.selection_rect = self.start_selection_rect.union(
                            [xds, yds, TILE_S, TILE_S]
                        )
                        selection_rect_xd = self.selection_rect.x - self.camera.rect.x
                        selection_rect_yd = self.selection_rect.y - self.camera.rect.y
                        pg.draw.rect(
                            NATIVE_SURF, "green", [
                                selection_rect_xd, selection_rect_yd, self.selection_rect.width, self.selection_rect.height
                            ], 1
                        )

                    elif self.game.is_lmb_just_released:
                        for xu in range(self.selection_rect.width // TILE_S):
                            for yu in range(self.selection_rect.height // TILE_S):
                                xd_tu = (self.selection_rect.x // TILE_S) + xu
                                yd_tu = (self.selection_rect.y // TILE_S) + yu

                                # xd = x + self.camera.rect.x
                                # yd = y + self.camera.rect.y
                                # xd_tu = xd // TILE_S
                                # yd_tu = yd // TILE_S

                                xds = xd_tu * TILE_S
                                yds = yd_tu * TILE_S
                                # Remove room offset to be collision index
                                x_tu = int(xd_tu - self.room_x_tu)
                                y_tu = int(yd_tu - self.room_y_tu)
                                # Cursor position global pos
                                xs = xds - self.camera.rect.x
                                ys = yds - self.camera.rect.y
                                w = self.selected_sprite["sprite_region"][2]
                                h = self.selected_sprite["sprite_region"][3]

                                xds = xd_tu * TILE_S
                                yds = yd_tu * TILE_S
                                # Remove room offset to be collision index
                                x_tu = int(xd_tu - self.room_x_tu)
                                y_tu = int(yd_tu - self.room_y_tu)
                                # Cursor position global pos
                                xs = xds - self.camera.rect.x
                                ys = yds - self.camera.rect.y
                                w = self.selected_sprite["sprite_region"][2]
                                h = self.selected_sprite["sprite_region"][3]

                                # Mouse position -> index -> get item in selected layer
                                item = self.selected_layer[y_tu *
                                                           self.room_w_tu + x_tu]

                                # Can only draw on 0, empty cells only
                                if item == 0:
                                    # Check if sprite right side and bottom side does not overshoot room rect
                                    r = xds + \
                                        self.selected_sprite["sprite_region"][2]
                                    b = yds + \
                                        self.selected_sprite["sprite_region"][3]
                                    # Does not overshoot? Copy selected and insert to selected layer
                                    if not r > self.room_rect.right and not b > self.room_rect.bottom:

                                        # Check first if any part of body overlap
                                        for y in range(self.selected_sprite["sprite_region"][3] // TILE_S):
                                            for x in range(self.selected_sprite["sprite_region"][2] // TILE_S):

                                                yc = y_tu + y
                                                xc = x_tu + x

                                                # Check if it is occupied
                                                cell = self.selected_layer[
                                                    yc * self.room_w_tu + xc
                                                ]

                                                # If the body is overlapping occupied cell, return
                                                if cell != 0:
                                                    return

                                        # Here, body does not overlap, free to insert

                                        # If this sprite w or h is bigger than 1 tile, chop into 1 tile and add to layers list
                                        for y in range(self.selected_sprite["sprite_region"][3] // TILE_S):
                                            for x in range(self.selected_sprite["sprite_region"][2] // TILE_S):
                                                new_sprite = copy.deepcopy(
                                                    self.selected_sprite
                                                )

                                                new_sprite["xds"] = xds + \
                                                    (x * TILE_S)
                                                new_sprite["yds"] = yds + \
                                                    (y * TILE_S)

                                                new_sprite["sprite_region"][0] += (
                                                    x * TILE_S)
                                                new_sprite["sprite_region"][1] += (
                                                    y * TILE_S)

                                                new_sprite["sprite_region"][2] = TILE_S
                                                new_sprite["sprite_region"][3] = TILE_S

                                                yc = y_tu + y
                                                xc = x_tu + x

                                                # Check if it is occupied
                                                cell = self.selected_layer[
                                                    yc * self.room_w_tu + xc
                                                ]

                                                # If the body is overlapping occupied cell, return
                                                if cell != 0:
                                                    return

                                                self.selected_layer[
                                                    yc * self.room_w_tu + xc
                                                ] = new_sprite

                                        # # If this sprite has bitmask type, then update it
                                        if new_sprite["sprite_bitmask_type"] != "none":
                                            self.update_bitmasks(
                                                x_tu, y_tu, xds, yds
                                            )

                        self.sound_manager.play_sound("cursor")

                    if self.game.is_rmb_just_pressed:
                        pos = pg.mouse.get_pos()
                        x = pos[0] // self.game.resolution
                        y = (pos[1] // self.game.resolution) - (
                            self.game.y_offset // self.game.resolution
                        )
                        # 0 - 9
                        x = clamp(
                            x, NATIVE_RECT.x, NATIVE_RECT.x + NATIVE_RECT.width
                        )
                        # 0 - 19
                        y = clamp(
                            y, NATIVE_RECT.y, NATIVE_RECT.y + NATIVE_RECT.height - TILE_S
                        )

                        xd = x + self.camera.rect.x
                        yd = y + self.camera.rect.y
                        xd_tu = xd // TILE_S
                        yd_tu = yd // TILE_S
                        xds = xd_tu * TILE_S
                        yds = yd_tu * TILE_S
                        # Remove room offset to be collision index
                        # x_tu = xd_tu - self.room_x_tu
                        # y_tu = yd_tu - self.room_y_tu
                        # Cursor position global pos
                        xs = xds - self.camera.rect.x
                        ys = yds - self.camera.rect.y
                        # w = self.selected_sprite["sprite_region"][2]
                        # h = self.selected_sprite["sprite_region"][3]

                        # pg.draw.rect(NATIVE_SURF, "green", [xs, ys, w, h], 1)

                        self.start_selection_rect = pg.Rect(
                            xds, yds, TILE_S, TILE_S
                        )

                    elif self.game.is_rmb_pressed:
                        pos = pg.mouse.get_pos()
                        x = pos[0] // self.game.resolution
                        y = (pos[1] // self.game.resolution) - (
                            self.game.y_offset // self.game.resolution
                        )
                        # 0 - 9
                        x = clamp(
                            x, NATIVE_RECT.x, NATIVE_RECT.x + NATIVE_RECT.width
                        )
                        # 0 - 19
                        y = clamp(
                            y, NATIVE_RECT.y, NATIVE_RECT.y + NATIVE_RECT.height - TILE_S
                        )

                        xd = x + self.camera.rect.x
                        yd = y + self.camera.rect.y
                        xd_tu = xd // TILE_S
                        yd_tu = yd // TILE_S
                        xds = xd_tu * TILE_S
                        yds = yd_tu * TILE_S
                        # Remove room offset to be collision index
                        # x_tu = xd_tu - self.room_x_tu
                        # y_tu = yd_tu - self.room_y_tu
                        # Cursor position global pos
                        xs = xds - self.camera.rect.x
                        ys = yds - self.camera.rect.y
                        # w = self.selected_sprite["sprite_region"][2]
                        # h = self.selected_sprite["sprite_region"][3]

                        # pg.draw.rect(NATIVE_SURF, "green", [xs, ys, w, h], 1)

                        # end_selection_rect = pg.Rect(
                        #     xds, yds, TILE_S, TILE_S
                        # )

                        self.selection_rect = self.start_selection_rect.union(
                            [xds, yds, TILE_S, TILE_S]
                        )
                        selection_rect_xd = self.selection_rect.x - self.camera.rect.x
                        selection_rect_yd = self.selection_rect.y - self.camera.rect.y
                        pg.draw.rect(
                            NATIVE_SURF, "red", [
                                selection_rect_xd, selection_rect_yd, self.selection_rect.width, self.selection_rect.height
                            ], 1
                        )

                    elif self.game.is_rmb_just_released:
                        for xu in range(self.selection_rect.width // TILE_S):
                            for yu in range(self.selection_rect.height // TILE_S):
                                xd_tu = (self.selection_rect.x // TILE_S) + xu
                                yd_tu = (self.selection_rect.y // TILE_S) + yu

                                # xd = x + self.camera.rect.x
                                # yd = y + self.camera.rect.y
                                # xd_tu = xd // TILE_S
                                # yd_tu = yd // TILE_S

                                xds = xd_tu * TILE_S
                                yds = yd_tu * TILE_S
                                # Remove room offset to be collision index
                                x_tu = int(xd_tu - self.room_x_tu)
                                y_tu = int(yd_tu - self.room_y_tu)
                                # Cursor position global pos
                                xs = xds - self.camera.rect.x
                                ys = yds - self.camera.rect.y
                                w = self.selected_sprite["sprite_region"][2]
                                h = self.selected_sprite["sprite_region"][3]

                                xds = xd_tu * TILE_S
                                yds = yd_tu * TILE_S
                                # Remove room offset to be collision index
                                x_tu = int(xd_tu - self.room_x_tu)
                                y_tu = int(yd_tu - self.room_y_tu)
                                # Cursor position global pos
                                xs = xds - self.camera.rect.x
                                ys = yds - self.camera.rect.y
                                w = self.selected_sprite["sprite_region"][2]
                                h = self.selected_sprite["sprite_region"][3]

                                # Mouse position -> index -> get item in selected layer
                                item = self.selected_layer[y_tu *
                                                           self.room_w_tu + x_tu]

                                # Found occupied
                                if item != 0:
                                    self.selected_layer[
                                        y_tu * self.room_w_tu + x_tu
                                    ] = 0

                                    # If this sprite has bitmask type, then update it
                                    if item["sprite_bitmask_type"] != "none":
                                        self.update_bitmasks(
                                            x_tu, y_tu, xds, yds
                                        )

                        self.sound_manager.play_sound("cancel")

                # Move camera
                self.offset.x += (
                    self.game.is_right_pressed - self.game.is_left_pressed
                ) * self.camera_speed

                self.offset.y += (
                    self.game.is_down_pressed - self.game.is_up_pressed
                ) * self.camera_speed

                self.camera.update(dt)

        elif self.state == "menu":
            # Do not update when curtain is lerping
            if self.curtain.is_done_lerping == True:
                # Tap pause?
                if self.game.is_pause_just_pressed == True:
                    # Curtain go to opaque
                    self.sound_manager.play_sound("cancel")
                    self.curtain.go_to_opaque()
                    return

                # In menu attempt to click on menu
                if self.game.is_lmb_just_released:
                    # Get mouse positions
                    pos = pg.mouse.get_pos()
                    x = pos[0] // self.game.resolution
                    y = (pos[1] // self.game.resolution) - (
                        self.game.y_offset // self.game.resolution
                    )
                    # 0 - 9
                    x = clamp(
                        x, NATIVE_RECT.x, NATIVE_RECT.x + NATIVE_RECT.width
                    )
                    # 0 - 19
                    y = clamp(
                        y, NATIVE_RECT.y, NATIVE_RECT.y + NATIVE_RECT.height - TILE_S
                    )

                    x_tu = x // TILE_S
                    y_tu = y // TILE_S
                    xs = x_tu * TILE_S
                    ys = y_tu * TILE_S

                    pg.draw.rect(NATIVE_SURF, "white", [
                                 xs, ys, TILE_S, TILE_S], 1)

                    item = self.menu_collisions[
                        y_tu * NATIVE_W_TU + x_tu
                    ]

                    # If clicked on non 0 cell, quit to normal
                    if item != 0:
                        self.selected_sprite = item
                        self.selected_layer = self.layers_list[self.selected_sprite["sprite_layer"]]
                        self.sound_manager.play_sound("accept")
                        # Handle door select
                        if self.selected_sprite["sprite_type"] == "door":
                            # Add extra target data
                            target_room_name = input(
                                "Enter target_room_name: ")
                            self.sound_manager.play_sound("cursor")

                            target_stage_no = int(
                                input("Enter target_stage_no: "))
                            self.sound_manager.play_sound("accept")

                            # Add target pair
                            self.selected_sprite["door_target"] = f"stage_{
                                target_stage_no}_{target_room_name}_game.json"

                        # Curtain go to opaque
                        self.curtain.go_to_opaque()
                    return

        self.curtain.update(dt)

    def set_state(self, value):
        old_state = value
        self.state = value

        # From normal
        if old_state == "normal":
            # To menu
            if self.state == "menu":
                pass

        # From menu
        elif old_state == "menu":
            # To normal
            if self.state == "normal":
                pass
