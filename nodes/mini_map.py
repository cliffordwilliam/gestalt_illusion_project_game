from constants import *


class MiniMap:
    '''
    How to use: 
        1: Create it before player and room
        2: Call its draw method
        3: When room change call my add room method

    What will happen:
        1: This thing will draw the added room is rel pos to player pos
    '''

    def __init__(self, state, player):
        # Update the is inventory
        self.state = state

        # Get player
        self.player = player

        # TODO: Have the world load save data, then pass to me, and I use it to set this
        self.rooms = []
        self.visited_rooms = set()

        # Imagine this like a sticker, where you draw on it first, then stick to native
        self.mini_map_surface = pg.Surface((NATIVE_W, NATIVE_H))
        self.mini_map_surface.set_colorkey("black")
        self.mini_map_surface.fill("black")

        self.room_colors = {
            "outline": {
                1: "#e5e3bc"
            },
            "fill": {
                1: "#492a1e"
            },
            "door_color": {
                1: "#5a3729"
            }
        }

        if self.state == "gameplay":
            # Gameplay surface needs to be transparent
            self.mini_map_surface.set_alpha(100)

            # Whole minimap topleft anchor, change this to move the entire thing
            self.x = TILE_S * 0
            self.y = TILE_S * 8

            # Padding from left and bottom, update room top left
            self.padding = TILE_S // 4
            self.x += self.padding
            self.y -= self.padding

            # Set minimap size
            self.w = TILE_S * 2
            self.h = TILE_S * 2

            # Get the right and bottom
            self.r = self.x + self.w
            self.b = self.y + self.h

            # Determine where the center of the map is at to draw player icon
            self.offset_x = (self.w // 2) + self.x
            self.offset_y = (self.h // 2) + self.y
            # To draw player since rect is 2 by 2, need to shift the tl by 1
            self.offset_x_1 = self.offset_x
            self.offset_y_1 = self.offset_y - 1

        elif self.state == "inventory":
            # Inventory mode topleft
            self.x = TILE_S * 7
            self.y = TILE_S * 2

            # Inventory mode size
            self.w = TILE_S * 11
            self.h = TILE_S * 6

            # Get the right and bottom
            self.r = self.x + self.w
            self.b = self.y + self.h

            # Determine where the center of the map is at to draw player icon
            self.offset_x = (self.w // 2) + self.x
            self.offset_y = (self.h // 2) + self.y
            # To draw player since rect is 2 by 2, need to shift the tl by 1
            self.offset_x_1 = self.offset_x
            self.offset_y_1 = self.offset_y - 1

            # Draw here ONCE, then stick this to inventory curtain base surface

            # Draw the background on the sticker
            pg.draw.rect(
                self.mini_map_surface, "black", (
                    self.x, self.y, self.w, self.h
                )
            )

            # Get player pos
            player_x_tu = 0
            player_y_tu = 0

            # Iterate over each room
            for data in self.rooms:
                # Get room rect
                room_rect = data["rect"]

                # Get room stage no
                room_stage_no = data["stage_no"]

                outline_color = self.room_colors["outline"][room_stage_no]
                fill_color = self.room_colors["fill"][room_stage_no]

                # Get room 4 points with the player offset and minimap position offset
                x = room_rect[0] - (
                    player_x_tu // TILE_S
                ) + self.offset_x
                y = room_rect[1] - (
                    player_y_tu // TILE_S
                ) + self.offset_y
                r = x + room_rect[2]
                b = y + room_rect[3]

                # Ensure 4 rects points are in the minimap 4 points
                x = clamp(x, self.x, self.r)
                y = clamp(y, self.y, self.b)
                r = clamp(r, self.x, self.r)
                b = clamp(b, self.y, self.b)

                # Compute the w and h for drawing
                w = r - x
                h = b - y

                # Draw the room
                pg.draw.rect(
                    self.mini_map_surface,
                    fill_color,
                    (x, y, w, h),
                )

                # Draw the room
                pg.draw.rect(
                    self.mini_map_surface,
                    outline_color,
                    (x, y, w, h),
                    1
                )

                # Get the doors
                for door in data["doors_pos"]:
                    # Get room 4 points with the player offset and minimap position offset
                    x = door["xtu"] - (
                        player_x_tu // TILE_S
                    ) + self.offset_x
                    y = door["ytu"] - (
                        player_y_tu // TILE_S
                    ) + self.offset_y
                    r = x + 1
                    b = y + 1

                    # Ensure 4 rects points are in the minimap 4 points
                    x = clamp(x, self.x, self.r)
                    y = clamp(y, self.y, self.b)
                    r = clamp(r, self.x, self.r)
                    b = clamp(b, self.y, self.b)

                    # Compute the w and h for drawing
                    w = r - x
                    h = b - y

                    door_color = self.room_colors["door_color"][room_stage_no]

                    # Draw the door
                    pg.draw.rect(
                        self.mini_map_surface,
                        door_color,
                        (x, y, w, h),
                        1
                    )

            # Draw the white frame
            pg.draw.rect(
                self.mini_map_surface, "white",
                (self.x, self.y, self.w, self.h), 1
            )

            # Inventory mode draw player rel to center offset
            player_x_tu = self.player.rect.center[0] // TILE_S + self.offset_x
            player_y_tu = self.player.rect.center[1] // TILE_S + self.offset_y

            # Draw center - represent player
            pg.draw.rect(
                self.mini_map_surface, "red",
                (player_x_tu, player_y_tu, 1, 2)
            )

    # Redraw ONCE again, with new player position or new room
    def redraw_inventory_mini_map(self):
        # Draw here ONCE, then stick this to inventory curtain base surface

        # Draw the background on the sticker
        pg.draw.rect(
            self.mini_map_surface, "black", (
                self.x, self.y, self.w, self.h
            )
        )

        # Get player pos
        player_x_tu = 0
        player_y_tu = 0

        # Iterate over each room
        for data in self.rooms:
            # Get room rect
            room_rect = data["rect"]

            # Get room stage no
            room_stage_no = data["stage_no"]

            outline_color = self.room_colors["outline"][room_stage_no]
            fill_color = self.room_colors["fill"][room_stage_no]

            # Get room 4 points with the player offset and minimap position offset
            x = room_rect[0] - (
                player_x_tu // TILE_S
            ) + self.offset_x
            y = room_rect[1] - (
                player_y_tu // TILE_S
            ) + self.offset_y
            r = x + room_rect[2]
            b = y + room_rect[3]

            # Ensure 4 rects points are in the minimap 4 points
            x = clamp(x, self.x, self.r)
            y = clamp(y, self.y, self.b)
            r = clamp(r, self.x, self.r)
            b = clamp(b, self.y, self.b)

            # Compute the w and h for drawing
            w = r - x
            h = b - y

            # Draw the room
            pg.draw.rect(
                self.mini_map_surface,
                fill_color,
                (x, y, w, h),
            )

            # Draw the room
            pg.draw.rect(
                self.mini_map_surface,
                outline_color,
                (x, y, w, h),
                1
            )

            # Get the doors
            for door in data["doors_pos"]:
                # Get room 4 points with the player offset and minimap position offset
                x = door["xtu"] - (
                    player_x_tu // TILE_S
                ) + self.offset_x
                y = door["ytu"] - (
                    player_y_tu // TILE_S
                ) + self.offset_y
                r = x + 1
                b = y + 1

                # Ensure 4 rects points are in the minimap 4 points
                x = clamp(x, self.x, self.r)
                y = clamp(y, self.y, self.b)
                r = clamp(r, self.x, self.r)
                b = clamp(b, self.y, self.b)

                # Compute the w and h for drawing
                w = r - x
                h = b - y

                door_color = self.room_colors["door_color"][room_stage_no]

                # Draw the door
                pg.draw.rect(
                    self.mini_map_surface,
                    door_color,
                    (x, y, w, h),
                    1
                )

        # Draw the white frame
        pg.draw.rect(
            self.mini_map_surface, "white",
            (self.x, self.y, self.w, self.h), 1
        )

        # Inventory mode draw player rel to center offset
        player_x_tu = self.player.rect.center[0] // TILE_S + self.offset_x
        player_y_tu = self.player.rect.center[1] // TILE_S + self.offset_y

        # To draw player since rect is 2 by 2, need to shift the tl by 1
        self.offset_x_1 = player_x_tu
        self.offset_y_1 = player_y_tu - 1

        # Draw center - represent player
        pg.draw.rect(
            self.mini_map_surface, "red",
            (self.offset_x_1, self.offset_y_1, 1, 2)
        )

    def add_room(self, data):
        room_name = data["name"]

        # This given room not added yet?
        if room_name not in self.visited_rooms:
            # Add it to list, to be drawn
            self.rooms.append(data)

            # Add it to set, to check, no dup
            self.visited_rooms.add(room_name)

    def draw(self, surf=NATIVE_SURF):
        # In inventory mode, no player offset
        if self.state == "inventory":
            # Stick sticker to inventory base curtain
            surf.blit(self.mini_map_surface, (0, 0))

        # In inventory mode, no player offset
        elif self.state == "gameplay":
            # Draw the background on the sticker / Things are drawn within this thing so technically this is a clear
            pg.draw.rect(
                self.mini_map_surface, "black", (
                    self.x, self.y, self.w, self.h
                )
            )

            # Get player pos
            player_x_tu = self.player.rect.center[0]
            player_y_tu = self.player.rect.center[1]

            # Iterate over each room
            for data in self.rooms:
                # Get room rect
                room_rect = data["rect"]

                # Get room stage no
                room_stage_no = data["stage_no"]

                outline_color = self.room_colors["outline"][room_stage_no]
                fill_color = self.room_colors["fill"][room_stage_no]

                # Get room 4 points with the player offset and minimap position offset
                x = room_rect[0] - (
                    player_x_tu // TILE_S
                ) + self.offset_x
                y = room_rect[1] - (
                    player_y_tu // TILE_S
                ) + self.offset_y
                r = x + room_rect[2]
                b = y + room_rect[3]

                # Ensure 4 rects points are in the minimap 4 points
                x = clamp(x, self.x, self.r)
                y = clamp(y, self.y, self.b)
                r = clamp(r, self.x, self.r)
                b = clamp(b, self.y, self.b)

                # Compute the w and h for drawing
                w = r - x
                h = b - y

                # Draw the room
                pg.draw.rect(
                    self.mini_map_surface,
                    fill_color,
                    (x, y, w, h),
                )

                # Draw the room
                pg.draw.rect(
                    self.mini_map_surface,
                    outline_color,
                    (x, y, w, h),
                    1
                )

                # Get the doors
                for door in data["doors_pos"]:
                    # Get room 4 points with the player offset and minimap position offset
                    x = door["xtu"] - (
                        player_x_tu // TILE_S
                    ) + self.offset_x
                    y = door["ytu"] - (
                        player_y_tu // TILE_S
                    ) + self.offset_y
                    r = x + 1
                    b = y + 1

                    # Ensure 4 rects points are in the minimap 4 points
                    x = clamp(x, self.x, self.r)
                    y = clamp(y, self.y, self.b)
                    r = clamp(r, self.x, self.r)
                    b = clamp(b, self.y, self.b)

                    # Compute the w and h for drawing
                    w = r - x
                    h = b - y

                    door_color = self.room_colors["door_color"][room_stage_no]

                    # Draw the door
                    pg.draw.rect(
                        self.mini_map_surface,
                        door_color,
                        (x, y, w, h),
                        1
                    )

            # Draw the white frame
            pg.draw.rect(
                self.mini_map_surface, "white",
                (self.x, self.y, self.w, self.h), 1
            )

            # Draw center - represent player
            pg.draw.rect(
                self.mini_map_surface, "red",
                (self.offset_x_1, self.offset_y_1, 1, 2)
            )

            # Stick the gameplay sirface to the native
            NATIVE_SURF.blit(self.mini_map_surface, (0, 0))
