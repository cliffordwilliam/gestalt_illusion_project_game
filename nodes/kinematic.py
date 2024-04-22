from constants import *


class Kinematic:
    '''
    How to use: 
        1: I am always a child of a moving actor
        2: Call my move function after you have updated velocity in actor
        3: Require a callback for me to call and pass what you collided with
        4: I Have debug draw in my update

    What will happen:
        1: For every frame, the following is done on x first then y axis
        2: Get magnitude direction based of vel
        3: Update is on wall, if input direction is 0, actor is not on wall
        4: Proceed if there is magnitude direction vel
        5: Compute displacement from dt and vel, store decimal in remainder, keep the int in displacement
        6: Do while loop as long as displacement int is not 0, decrease by 1 each iteration
        7: On each iteration convert pwner pos to index
        8: Use index to lookup table for collision neighbour checks
        9: If found something in neighbour, collect in list
        10: Iterate over every found enighbour cell and do aabb with my next frame pos
        11: If I did hit something, owner callback on hit. Let owner do what they want based on what it hits, also update is on wall and is on floor
        12: Did not hit anything? Move owner rect 1 px and go to next iteration
        13: After updating both x and y, check if I am on floor and is on wall, if yes then take away the owner x velocity
    '''

    def __init__(self, owner, game, room, camera, quadtree):
        # Dependencies
        self.game = game
        self.room = room
        self.camera = camera

        # For movement while loop
        self.remainder_x = 0
        self.remainder_y = 0

        # Get owner
        self.owner = owner

        # Floor and wall flags
        self.is_on_floor = False
        self.is_on_wall = False

    def move(self, dt):
        is_moved = False

        # Debug draw rects
        if self.game.is_debug:

            # Base
            x = self.owner.rect.x - self.camera.rect.x
            y = self.owner.rect.y - self.camera.rect.y

            # Owner real rect
            self.game.debug_draw.add(
                {
                    "type": "rect",
                    "layer": 1,
                    "rect": [x, y, self.owner.rect.width, self.owner.rect.height],
                    "color": "orange",
                    "width": 1
                }
            )

        # Update direction sign for movement
        direction_x = 0
        if self.owner.velocity.x < 0:
            direction_x = -1
        elif self.owner.velocity.x > 0:
            direction_x = 1

        direction_y = 0
        if self.owner.velocity.y < 0:
            direction_y = -1
        elif self.owner.velocity.y > 0:
            direction_y = 1

        # region Update horizontal position

        # Do not do anything if there is no direction / velocity == 0
        if direction_x != 0:

            # Compute the displacement
            displacement = self.owner.velocity.x * dt

            # Turn displacement to int, store the droppped to remainder
            self.remainder_x += displacement
            displacement_x = round(self.remainder_x)
            self.remainder_x -= displacement_x
            displacement_x = abs(displacement_x)

            # Check 1px at a time for this displacement
            while displacement_x > 0:
                # Actor currrent pos -> tu index
                possible_x_tu = (
                    self.owner.rect.centerx // TILE_S
                ) - self.room.x_tu
                possible_y_tu = (
                    self.owner.rect.centery // TILE_S
                ) - self.room.y_tu

                # Possible positions to check
                actor_tl_tu = (possible_x_tu - 1, possible_y_tu - 1)
                actor_tt_tu = (possible_x_tu, possible_y_tu - 1)
                actor_tr_tu = (possible_x_tu + 1, possible_y_tu - 1)
                actor_ml_tu = (possible_x_tu - 1, possible_y_tu - 0)
                actor_mr_tu = (possible_x_tu + 1, possible_y_tu - 0)
                actor_bl_tu = (possible_x_tu - 1, possible_y_tu + 1)
                actor_bm_tu = (possible_x_tu, possible_y_tu + 1)
                actor_br_tu = (possible_x_tu + 1, possible_y_tu + 1)

                # Prepare filtered container
                possible_pos_tus = []

                # Filter positions that is needed based on my direction
                if direction_x == 0 and direction_y == 0:
                    possible_pos_tus = []

                elif direction_x == 0 and direction_y == -1:
                    possible_pos_tus = [
                        actor_tl_tu,
                        actor_tt_tu,
                        actor_tr_tu
                    ]

                elif direction_x == 1 and direction_y == -1:
                    possible_pos_tus = [
                        actor_tl_tu,
                        actor_tt_tu,
                        actor_tr_tu,
                        actor_mr_tu,
                        actor_br_tu
                    ]

                elif direction_x == 1 and direction_y == 0:
                    possible_pos_tus = [
                        actor_tr_tu,
                        actor_mr_tu,
                        actor_br_tu
                    ]

                elif direction_x == 1 and direction_y == 1:
                    possible_pos_tus = [
                        actor_bl_tu,
                        actor_bm_tu,
                        actor_br_tu,
                        actor_mr_tu,
                        actor_tr_tu
                    ]

                elif direction_x == 0 and direction_y == 1:
                    possible_pos_tus = [
                        actor_bl_tu,
                        actor_bm_tu,
                        actor_br_tu
                    ]

                elif direction_x == -1 and direction_y == 1:
                    possible_pos_tus = [
                        actor_tl_tu,
                        actor_ml_tu,
                        actor_bl_tu,
                        actor_bm_tu,
                        actor_br_tu
                    ]

                elif direction_x == -1 and direction_y == 0:
                    possible_pos_tus = [
                        actor_tl_tu,
                        actor_ml_tu,
                        actor_bl_tu
                    ]

                elif direction_x == -1 and direction_y == -1:
                    possible_pos_tus = [
                        actor_bl_tu,
                        actor_ml_tu,
                        actor_tl_tu,
                        actor_tt_tu,
                        actor_tr_tu
                    ]

                # Prepare found cells in possible positions
                possible_cells = []

                # Check each of my possible positions
                for possible_pos_tu in possible_pos_tus:
                    possible_x_tu = possible_pos_tu[0]
                    possible_y_tu = possible_pos_tu[1]

                    # Clamp tu index withing room
                    possible_x_tu = int(
                        clamp(possible_x_tu, self.room.x_tu, self.room.w_tu - 1)
                    )
                    possible_y_tu = int(
                        clamp(possible_y_tu, self.room.y_tu, self.room.h_tu - 1)
                    )

                    # Tu index -> cell
                    cell = self.room.collision_layer[
                        possible_y_tu * self.room.w_tu + possible_x_tu
                    ]

                    # Debug draw rects
                    if self.game.is_debug:

                        # Base
                        possible_xd = (
                            (possible_x_tu + self.room.x_tu) * TILE_S
                        ) - self.camera.rect.x

                        possible_yd = (
                            (possible_y_tu + self.room.y_tu) * TILE_S
                        ) - self.camera.rect.y

                        # Posssible collision rect
                        self.game.debug_draw.add(
                            {
                                "type": "rect",
                                "layer": 1,
                                "rect": [possible_xd, possible_yd, TILE_S, TILE_S],
                                "color": "green",
                                "width": 1
                            }
                        )

                    # Found something?
                    if cell != 0:
                        # Found rect? Add it to possible_cells
                        possible_cells.append(cell)

                        # Debug draw rects
                        if self.game.is_debug:

                            # Posssible found rect
                            self.game.debug_draw.add(
                                {
                                    "type": "rect",
                                    "layer": 1,
                                    "rect": [possible_xd, possible_yd, TILE_S, TILE_S],
                                    "color": "yellow",
                                    "width": 0
                                }
                            )

                # My future position (x / horizontal)
                xds = self.owner.rect.x + direction_x
                yds = self.owner.rect.y
                w = xds + self.owner.rect.width
                h = yds + self.owner.rect.height

                # Debug draw rects
                if self.game.is_debug:

                    # My future rect horizontal
                    self.game.debug_draw.add(
                        {
                            "type": "rect",
                            "layer": 1,
                            "rect": [xds - self.camera.rect.x, yds - self.camera.rect.y, self.owner.rect.width, self.owner.rect.height],
                            "color": "blue",
                            "width": 1
                        }
                    )

                # Prepare container to store collided cells
                collided_cells = []

                # Check each found cells AABB
                for cell in possible_cells:
                    # Extract cell data to do AABB
                    c_xds = cell["xds"]
                    c_yds = cell["yds"]
                    c_w = c_xds + TILE_S
                    c_h = c_yds + TILE_S

                    # AABB, my future self hit something? (x / horizontal)
                    if (c_xds < w and xds < c_w and c_yds < h and yds < c_h):
                        # Collect this cell that hits my future self
                        collided_cells.append(cell)

                        # is_on_wall = true when my future self collided
                        self.is_on_wall = True

                # Tell owner what its future self hit, then collect if it wants me to stop
                is_stop = self.owner.on_collide(collided_cells)

                # Owner wants me to stop?
                if is_stop == True:
                    # Stop
                    break

                # My future self did not hit anything if I get here

                # If my future self did not collide, then I am not on wall
                self.is_on_wall = False

                # Then move me 1px
                self.owner.rect.x += direction_x
                is_moved = True

                # Since I have moved 1 px, so deduct the distance I had to cover this frame
                displacement_x -= 1

        # endregion Update horizontal position

        # region Update vertical position

        # Do not do anything if there is no direction / velocity == 0
        if direction_y != 0:

            # Compute the displacement
            displacement = self.owner.velocity.y * dt

            # Turn displacement to int, store the droppped to remainder
            self.remainder_y += displacement
            displacement_y = round(self.remainder_y)
            self.remainder_y -= displacement_y
            displacement_y = abs(displacement_y)

            # Check 1px at a time for this displacement
            while displacement_y > 0:
                # Actor currrent pos -> tu index
                possible_x_tu = (
                    self.owner.rect.centerx // TILE_S
                ) - self.room.x_tu
                possible_y_tu = (
                    self.owner.rect.centery // TILE_S
                ) - self.room.y_tu

                # Possible positions to check
                actor_tl_tu = (possible_x_tu - 1, possible_y_tu - 1)
                actor_tt_tu = (possible_x_tu, possible_y_tu - 1)
                actor_tr_tu = (possible_x_tu + 1, possible_y_tu - 1)
                actor_ml_tu = (possible_x_tu - 1, possible_y_tu - 0)
                actor_mr_tu = (possible_x_tu + 1, possible_y_tu - 0)
                actor_bl_tu = (possible_x_tu - 1, possible_y_tu + 1)
                actor_bm_tu = (possible_x_tu, possible_y_tu + 1)
                actor_br_tu = (possible_x_tu + 1, possible_y_tu + 1)

                # Prepare filtered container
                possible_pos_tus = []

                # Filter positions that is needed based on my direction
                if direction_x == 0 and direction_y == 0:
                    possible_pos_tus = []

                elif direction_x == 0 and direction_y == -1:
                    possible_pos_tus = [
                        actor_tl_tu,
                        actor_tt_tu,
                        actor_tr_tu
                    ]

                elif direction_x == 1 and direction_y == -1:
                    possible_pos_tus = [
                        actor_tl_tu,
                        actor_tt_tu,
                        actor_tr_tu,
                        actor_mr_tu,
                        actor_br_tu
                    ]

                elif direction_x == 1 and direction_y == 0:
                    possible_pos_tus = [
                        actor_tr_tu,
                        actor_mr_tu,
                        actor_br_tu
                    ]

                elif direction_x == 1 and direction_y == 1:
                    possible_pos_tus = [
                        actor_bl_tu,
                        actor_bm_tu,
                        actor_br_tu,
                        actor_mr_tu,
                        actor_tr_tu
                    ]

                elif direction_x == 0 and direction_y == 1:
                    possible_pos_tus = [
                        actor_bl_tu,
                        actor_bm_tu,
                        actor_br_tu
                    ]

                elif direction_x == -1 and direction_y == 1:
                    possible_pos_tus = [
                        actor_tl_tu,
                        actor_ml_tu,
                        actor_bl_tu,
                        actor_bm_tu,
                        actor_br_tu
                    ]

                elif direction_x == -1 and direction_y == 0:
                    possible_pos_tus = [
                        actor_tl_tu,
                        actor_ml_tu,
                        actor_bl_tu
                    ]

                elif direction_x == -1 and direction_y == -1:
                    possible_pos_tus = [
                        actor_bl_tu,
                        actor_ml_tu,
                        actor_tl_tu,
                        actor_tt_tu,
                        actor_tr_tu
                    ]

                # Prepare found cells in possible positions
                possible_cells = []

                # Check each of my possible positions
                for possible_pos_tu in possible_pos_tus:
                    possible_x_tu = possible_pos_tu[0]
                    possible_y_tu = possible_pos_tu[1]

                    # Clamp tu index withing room
                    possible_x_tu = int(
                        clamp(possible_x_tu, self.room.x_tu, self.room.w_tu - 1)
                    )
                    possible_y_tu = int(
                        clamp(possible_y_tu, self.room.y_tu, self.room.h_tu - 1)
                    )

                    # Tu index -> cell
                    cell = self.room.collision_layer[
                        possible_y_tu * self.room.w_tu + possible_x_tu
                    ]

                    # Debug draw rects
                    if self.game.is_debug:

                        # Base
                        possible_xd = (
                            (possible_x_tu + self.room.x_tu) * TILE_S
                        ) - self.camera.rect.x

                        possible_yd = (
                            (possible_y_tu + self.room.y_tu) * TILE_S
                        ) - self.camera.rect.y

                        # Posssible collision rect
                        self.game.debug_draw.add(
                            {
                                "type": "rect",
                                "layer": 1,
                                "rect": [possible_xd, possible_yd, TILE_S, TILE_S],
                                "color": "green",
                                "width": 1
                            }
                        )

                    # Found something?
                    if cell != 0:
                        # Found rect? Add it to possible_cells
                        possible_cells.append(cell)

                        # Debug draw rects
                        if self.game.is_debug:

                            # Posssible found rect
                            self.game.debug_draw.add(
                                {
                                    "type": "rect",
                                    "layer": 1,
                                    "rect": [possible_xd, possible_yd, TILE_S, TILE_S],
                                    "color": "yellow",
                                    "width": 0
                                }
                            )

                # My future position (y / vertical)
                xds = self.owner.rect.x
                yds = self.owner.rect.y + direction_y
                w = xds + self.owner.rect.width
                h = yds + self.owner.rect.height

                # Debug draw rects
                if self.game.is_debug:

                    # My future rect horizontal
                    self.game.debug_draw.add(
                        {
                            "type": "rect",
                            "layer": 1,
                            "rect": [xds - self.camera.rect.x, yds - self.camera.rect.y, self.owner.rect.width, self.owner.rect.height],
                            "color": "blue",
                            "width": 1
                        }
                    )

                # Prepare container to store collided cells
                collided_cells = []

                # Check each found cells AABB
                for cell in possible_cells:
                    # Extract cell data to do AABB
                    c_xds = cell["xds"]
                    c_yds = cell["yds"]
                    c_w = c_xds + TILE_S
                    c_h = c_yds + TILE_S

                    # AABB, my future self hit something? (y / vertical)
                    if (c_xds < w and xds < c_w and c_yds < h and yds < c_h):
                        # Collect this cell that hits my future self
                        collided_cells.append(cell)

                        # is_on_floor = true when my future self collided if I AM GOING DOWN
                        if direction_y == 1:
                            self.is_on_floor = True

                # Tell owner what its future self hit, then collect if it wants me to stop
                is_stop = self.owner.on_collide(collided_cells)

                # Owner wants me to stop?
                if is_stop == True:
                    # Stop
                    break

                # My future self did not hit anything if I get here

                # If my future self did not collide, then I am not on floor
                self.is_on_floor = False

                # Then move me 1px
                self.owner.rect.y += direction_y
                is_moved = True

                # Since I have moved 1 px, so deduct the distance I had to cover this frame
                displacement_y -= 1

        # endregion Update vertical position

        # Owner moved? relocate them in quadtree
        if is_moved:
            self.room.quadtree.relocate(self.owner)
