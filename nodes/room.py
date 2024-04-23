from constants import *
from nodes.quadtree import QuadTree
from nodes.background import Background


class Room:
    '''
    How to use: 
        1: Give me room name
        2: Room name is used to load json game room, not editor
        3: Room data is extracted
        4: There are bg layers and 1 collision layer, collision layer is the lookup table
        5: I have room rect for camera limit and player reposition after transition
        6: Manually typed bg is also extracted to draw the hard coded background, make sure that you type in the correct available bg for distict stages
        7: Use my name setter to change room, if new room is in same stage, I will not re import the image for this stage
        8: Any sprite names that are in game actors list, will be instanced and placed in layer, replacing the dict

    What will happen:
        1: You need to call my bg layer draw, This func, for every frame draws the bg
        2: Same goes with fg, fg includes the collision layer first, then the fg
        3: I have update func to update all actors in my bg layers
        4: Collision layers may have actors, these will be moved to the draw update collision layer. Where stuffs are drawn and updated
    '''

    def __init__(self, game, camera, name):
        # Get game
        self.game = game

        # Get camera
        self.camera = camera

        # Get room name
        self.name = name

        # Room name -> read room data json
        self.room_data = {}
        with open(JSONS_PATHS[self.name], "r") as data:
            self.room_data = load(data)

        # Get the background layers
        self.background_layers = self.room_data["background_layer"]

        # Prepare to collect animation data for this stage
        self.animation_data = {}

        # Read each sprite in background layer
        for layer in self.background_layers:
            for sprite in layer:
                # Find animated sprites?
                if sprite != 0:
                    if sprite["sprite_type"] == "animated_background":
                        # Load the animation data for this sprite
                        with open(
                            JSONS_PATHS[
                                f"{
                                sprite["sprite_name"]
                                }_animation.json"
                            ], "r"
                        ) as data:
                            animation_data = load(data)

                        # Collect it
                        self.animation_data[
                            sprite["sprite_name"]
                        ] = animation_data

        # Get the actor layer (enemies, goblins)
        self.actor_layer = self.room_data["actor_layer"]

        # Get the solid layer
        self.collision_layer = self.room_data["solid_layer"]

        # get the foreground layer
        self.foreground_layers = self.room_data["foreground_layer"]

        # Get the stage number
        self.stage_no = self.room_data["stage_no"]

        # Room rect, room camera limit
        self.rect = self.room_data["room_rect"]
        self.x_tu = self.rect[0] // TILE_S
        self.y_tu = self.rect[1] // TILE_S
        self.w_tu = self.rect[2] // TILE_S
        self.h_tu = self.rect[3] // TILE_S

        # Update the camera limit
        self.camera.set_limit(
            pg.Rect(
                self.rect[0],
                self.rect[1],
                self.rect[2],
                self.rect[3],
            )
        )

        # Room background names that it needs to draw
        self.desired_background_names = self.room_data["desired_background_names"]

        # Load this room sprite sheet
        self.sprite_sheet_png_name = self.room_data["sprite_sheet_name"]
        self.sprite_sheet_path = PNGS_PATHS[self.sprite_sheet_png_name]
        self.sprite_sheet_surf = pg.image.load(
            self.sprite_sheet_path
        ).convert_alpha()

        # Init the background drawer
        self.background = Background(
            self.sprite_sheet_surf,
            self.camera,
            self.stage_no,
            self.desired_background_names
        )

        # Check if there are any actors in background_layers
        for room in self.background_layers:
            for sprite in room:
                if sprite != 0:
                    # Found?
                    if sprite["sprite_type"] == "animated_background":
                        # Add a new pair instance, value is the instance itself
                        sprite["instance"] = self.game.actors[sprite["sprite_name"]](
                            self.sprite_sheet_surf,
                            self.animation_data[sprite["sprite_name"]],
                            self.camera,
                            sprite["xds"],
                            sprite["yds"]
                        )

        # Quadtree init, as big as current room, FRect because kid size might be decimal
        self.quadtree = QuadTree(pg.FRect(self.rect), self)

        # Read actor layer
        for i in range(len(self.actor_layer)):
            # Get the dict / obj
            obj = self.actor_layer[i]

            # Init the actor from game all actors list
            instance = self.game.actors[obj["sprite_name"]](i)

            # Set the instance position
            instance.rect.x = obj["xds"]
            instance.rect.y = obj["yds"]
            instance.rect.y -= instance.rect.height - TILE_S

            # Replace the dict / obj with the instance
            self.actor_layer[i] = instance

            # Collect actor to the quadtree
            self.quadtree.insert(instance)

        # REMOVE IN BUILD
        self.grid_surface = pg.Surface((NATIVE_W, NATIVE_H))
        self.grid_surface.set_colorkey("black")
        self.grid_surface.fill("black")
        self.grid_surface.set_alpha(100)

    def add_room_to_mini_map(self, mini_map):

        # Prepare door container
        doors_pos = []

        # Collect door position
        for cell in self.collision_layer:
            if cell != 0:
                if cell["sprite_type"] == "door":
                    xtu = cell["xds"] // TILE_S
                    ytu = cell["yds"] // TILE_S
                    doors_pos.append({"xtu": xtu, "ytu": ytu})

        # Pack data for mini map
        mini_map_data = {
            "name": self.name,
            "rect": [self.x_tu, self.y_tu, self.w_tu, self.h_tu],
            "doors_pos": doors_pos
        }

        # Add to mini map, it uses set, so dupplicates are impossible
        mini_map.add_room(mini_map_data)

    def draw(self):
        # Debug draw grid
        if self.game.is_debug:
            # Clear grid surf
            self.grid_surface.fill("black")

            # Draw new grid lines
            for i in range(NATIVE_W_TU):
                offset = TILE_S * i
                xd = (offset - self.camera.rect.x) % NATIVE_W
                yd = (offset - self.camera.rect.y) % NATIVE_H
                pg.draw.line(
                    self.grid_surface, "grey58", (xd, 0), (xd, NATIVE_H)
                )
                pg.draw.line(
                    self.grid_surface, "grey58", (0, yd), (NATIVE_W, yd)
                )
            xd = -self.camera.rect.x % NATIVE_W
            yd = -self.camera.rect.y % NATIVE_H
            pg.draw.line(self.grid_surface, "grey66", (xd, 0), (xd, NATIVE_H))
            pg.draw.line(self.grid_surface, "grey66", (0, yd), (NATIVE_W, yd))
            FONT.render_to(
                NATIVE_SURF, (xd + FONT_W, yd + FONT_H), f"{
                    (int(self.camera.rect.x) - 1) // NATIVE_W + 1}{
                    (int(self.camera.rect.y) - 1) // NATIVE_H + 1}", "grey100"
            )

            # Add to debug draw
            self.game.debug_draw.add(
                {
                    "type": "surf",
                    "layer": 0,
                    "x": 0,
                    "y": 0,
                    "surf": self.grid_surface,
                }
            )

        # Draw the background
        self.background.draw()

        # Turn camera coord into tu
        cam_x_tu = self.camera.rect.x // TILE_S
        cam_y_tu = self.camera.rect.y // TILE_S

        # Turn tu into index, by sub cam offset
        cam_x_tu = int(cam_x_tu - self.x_tu)
        cam_y_tu = int(cam_y_tu - self.y_tu)

        # Handle each background_layers
        for layer in self.background_layers:
            # Turn camera top left coord to index and the rest of the cells that is in camera
            # Iterate over rows (camera width)
            for row in range(NATIVE_H_TU_EXTRA_ONE):  # NATIVE_H_TU + 1
                # Iterate over columns (camera height)
                for col in range(NATIVE_W_TU_EXTRA_ONE):  # NATIVE_W_TU + 1
                    # Compute index
                    index = (
                        cam_y_tu + row
                    ) * self.w_tu + (
                        cam_x_tu + col
                    )

                    # Makes sure its in index (because this iterates extra 1 to right and down of camera)
                    if 0 <= index < len(layer):
                        # Get item with index
                        item = layer[index]

                        # Find something?
                        if item != 0:
                            # Its an actor? let it draw itself
                            if item["sprite_type"] == "animated_background":
                                instance = item["instance"]
                                instance.draw()
                                continue

                            # Not actor? turn the coord to draw coord
                            xd = item["xds"] - self.camera.rect.x
                            yd = item["yds"] - self.camera.rect.y

                            # Draw this sprite with the draw coord
                            NATIVE_SURF.blit(
                                self.sprite_sheet_surf,
                                (xd, yd),
                                item["sprite_region"]
                            )

        # Actors move around, cannot use lookup, use quadtree to find them. Pass a rect to it and it will returns the actors in it

        # Handle each actor in camera
        for actor in self.quadtree.search(self.camera.rect):
            # Let the actor draw themselves
            actor.draw()

        # Turn camera top left coord to index and the rest of the cells that is in camera
        # Iterate over rows (camera width)
        for row in range(NATIVE_H_TU_EXTRA_ONE):  # NATIVE_H_TU + 1
            # Iterate over columns (camera height)
            for col in range(NATIVE_W_TU_EXTRA_ONE):  # NATIVE_W_TU + 1
                # Compute index
                index = (
                    cam_y_tu + row
                ) * self.w_tu + (
                    cam_x_tu + col
                )

                # Makes sure its in index (because this iterates extra 1 to right and down of camera)
                if 0 <= index < len(self.collision_layer):
                    # Get item with index
                    item = self.collision_layer[index]

                    # Find something
                    if item != 0:
                        # Turn this solid tile coord to draw coord
                        xd = item["xds"] - self.camera.rect.x
                        yd = item["yds"] - self.camera.rect.y

                        # Draw this sprite with the draw coord
                        NATIVE_SURF.blit(
                            self.sprite_sheet_surf,
                            (xd, yd),
                            item["sprite_region"]
                        )

        # Handle each foreground_layers
        for layer in self.foreground_layers:
            # Turn camera top left coord to index and the rest of the cells that is in camera
            # Iterate over rows (camera width)
            for row in range(NATIVE_H_TU_EXTRA_ONE):  # NATIVE_H_TU + 1
                # Iterate over columns (camera height)
                for col in range(NATIVE_W_TU_EXTRA_ONE):  # NATIVE_W_TU + 1
                    # Compute index
                    index = (
                        cam_y_tu + row
                    ) * self.w_tu + (
                        cam_x_tu + col
                    )

                    # Makes sure its in index (because this iterates extra 1 to right and down of camera)
                    if 0 <= index < len(layer):
                        # Get item with index
                        item = layer[index]

                        # Find something
                        if item != 0:
                            # Turn this foreground tile coord to draw coord
                            xd = item["xds"] - self.camera.rect.x
                            yd = item["yds"] - self.camera.rect.y

                            # Draw this sprite with the draw coord
                            NATIVE_SURF.blit(
                                self.sprite_sheet_surface,
                                (xd, yd),
                                item["sprite_region"]
                            )

        # Draw quadtree for debug
        if self.game.is_debug:
            self.quadtree.draw(self.game, self.camera)

    def update(self, dt):
        # Turn camera coord into tu
        cam_x_tu = self.camera.rect.x // TILE_S
        cam_y_tu = self.camera.rect.y // TILE_S

        # Turn tu into index, by sub cam offset
        cam_x_tu = int(cam_x_tu - self.x_tu)
        cam_y_tu = int(cam_y_tu - self.y_tu)

        # Handle each background_layers
        for layer in self.background_layers:
            # Turn camera top left coord to index and the rest of the cells that is in camera
            # Iterate over rows (camera width)
            for row in range(NATIVE_H_TU_EXTRA_ONE):  # NATIVE_H_TU + 1
                # Iterate over columns (camera height)
                for col in range(NATIVE_W_TU_EXTRA_ONE):  # NATIVE_W_TU + 1
                    # Calculate index for the current tile
                    # Compute index
                    index = (
                        cam_y_tu + row
                    ) * self.w_tu + (
                        cam_x_tu + col
                    )

                    # Makes sure its in index (because this iterates extra 1 to right and down of camera)
                    if 0 <= index < len(layer):
                        # Get item with index
                        item = layer[index]

                        # Find something
                        if item != 0:
                            # Found actor? let it update itself
                            if item["sprite_type"] == "animated_background":
                                instance = item["instance"]
                                instance.update(dt)

        # Actors move around, cannot use lookup, use quadtree to find them. Pass a rect to it and it will returns the actors in it

        # Handle each actor in camera
        for actor in self.quadtree.search(self.camera.rect):
            # Let the actor update themselves
            actor.update(dt)
