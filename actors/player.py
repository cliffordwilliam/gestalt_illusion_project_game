from constants import *
from nodes.animator import Animator
from nodes.kinematic import Kinematic
from nodes.timer import Timer


class Player:
    def __init__(self, game, room, camera, world):
        # Dependencies
        self.game = game
        self.room = room
        self.camera = camera
        self.world = world

        # Id for quadtree bookeeping, for quick relocation in quad
        # Each room loop over and use index to set id, since player is only 1
        # And count starts from 0, so there is only 1 -1
        self.id = -1

        # Name
        self.name = "Player"

        # Player sprite sheets, flip or no flip
        self.sprite_sheet = pg.image.load(
            PNGS_PATHS["player_sprite_sheet.png"]
        )
        self.sprite_sheet_flip = pg.image.load(
            PNGS_PATHS["player_flip_sprite_sheet.png"]
        )
        self.current_sprite_sheet = self.sprite_sheet

        # Surface offset
        self.surface_offset_x = 21
        self.surface_offset_y = 14

        # Read json animation data
        self.aniamtion_data = {}
        with open(JSONS_PATHS["player_animation.json"], "r") as data:
            self.aniamtion_data = load(data)

        # Init starting region
        self.region = self.aniamtion_data["idle"]["frames_list"][0]["region"]

        # State
        self.state = "idle"

        # Facing direction (when direction is 0, I still need to know where I am facing, this determine when I turn)
        self.facing_direction = 1
        self.old_facing_direction = self.facing_direction

        # Direction input
        self.direction = 0

        # Animator node
        self.animator = Animator(self, self.aniamtion_data, "idle")

        # Rect
        self.rect = pg.FRect(0, 0, 6, 31)

        # Movement
        self.hurt_max_run = 0.0225
        self.normal_max_run = 0.09
        self.max_run = self.normal_max_run
        self.run_lerp_weight = 0.2
        self.max_fall = 0.270
        self.normal_gravity = 0.000533
        self.heavy_gravity = 0.001066
        self.gravity = self.normal_gravity
        self.jump_vel = -0.2330
        self.velocity = Vector2()
        self.pain_direction_from = self.direction

        # Kinematic
        self.kinematic = Kinematic(
            self,
            self.game,
            self.room,
            self.camera,
            self.room.quadtree
        )

        # Camera anchor
        self.camera_anchor = Vector2(
            self.rect.center[0] + (self.facing_direction * TILE_S),
            self.rect.center[1]
        )

        # Set to false on next frame immediately after falling for 1 frame distance
        self.is_thin_fall = False

        # Timer to toggle between idle and run
        self.hurt_timer = Timer(500)
        self.invincibility_timer = Timer(1000)
        self.hurt_timer.add_event_listener(
            self.on_hurt_timer_end, "timer_end"
        )
        self.invincibility_timer.add_event_listener(
            self.on_invincibility_timer_end, "timer_end"
        )

        # Invincibility flag after getting hurt
        self.is_invincible = False

        # To not draw (used for blinking or whatever you want)
        self.is_hidden = False

    # Called by enemies to damage player
    def ouch(self, pain_direction_from):
        # Cannot get hurt when I am invincible
        if self.is_invincible:
            return

        # Prevent when vverlap in multiple frames will call this over and over again
        if self.state != "hurt":
            # Update the pain from direction
            self.pain_direction_from = pain_direction_from

            # Exit to hurt
            self.set_state("hurt")

            # Reset hurt timer
            self.hurt_timer.reset()

    # When invincible timer is over
    def on_invincibility_timer_end(self):
        # Reset is_invincible flag
        self.is_invincible = False

        # Reset is hidden, make sure that player is visible after blinking
        self.is_hidden = False

    # Called when hurt timer is over
    def on_hurt_timer_end(self):
        # Set invicibility to true
        self.is_invincible = True

        # Reset invincibility_timer
        self.invincibility_timer.reset()

        # Exit to down if next frame going down is empty pixel
        if not self.kinematic.is_on_floor:
            self.set_state("down")
            return

        # Exit to idle if next frame going down is floor
        if self.kinematic.is_on_floor:
            # I am not pressing anything or next frame is solid pixel wall? Idle
            if self.direction == 0 or self.kinematic.is_on_wall:
                self.set_state("idle")
                return

        # Exit to up if next frame going down is floor
        if self.kinematic.is_on_floor:
            # I just press jump this frame
            if self.game.is_jump_just_pressed:
                self.set_state("up")
                return

        # Exit to run if next frame going down is floor
        if self.kinematic.is_on_floor:
            # I am pressing direction AND next frame is NOT solid pixel wall? Run
            if self.direction != 0 and not self.kinematic.is_on_wall:
                self.set_state("run")
                return

        # Exit to crouch if next frame going down is floor
        if self.kinematic.is_on_floor:
            # I am holding down crouch this frame
            if self.game.is_down_pressed:
                self.set_state("crouch")
                return

    # Called by kinematic - this is for static things
    def on_collide(self, cells):
        # These are cells where my future self next frame would collide

        # Unpack all given found collided cells type and name
        for cell in cells:
            self.collided_cell_type = cell["sprite_type"]
            self.collided_cell_name = cell["sprite_name"]

            # Prioritize solids, found solid first? Stop
            if cell["sprite_type"] == "solid":
                return True

            # Found thin?
            elif cell["sprite_type"] == "thin":
                # Not passing thru?
                if self.is_thin_fall == False:
                    # If I am falling
                    if self.velocity.y > 0:
                        # Player real rect feet flushed on it? Stop
                        if (self.rect.bottom - cell["yds"]) == 0:
                            return True

            # Found door next?
            elif cell["sprite_type"] == "door":
                # Announce to world
                self.world.on_player_hit_door(cell)

                # Get door direction
                door_direction = cell["door_direction"]

                # Based on direction, update my vel and tell kinematic to stop
                if door_direction == "left":
                    self.velocity.y = 0
                    return False

                elif door_direction == "right":
                    self.velocity.y = 0
                    return False

                elif door_direction == "up":
                    self.velocity.y /= 1.25
                    self.velocity.x = 0
                    return False

                elif door_direction == "down":
                    self.velocity.x = 0
                    return False

    def draw(self):
        # Draw player to native surface if NOT hidden
        if not self.is_hidden:
            # Compute draw coords
            xds = (self.rect.x - self.surface_offset_x) - self.camera.rect.x
            yds = (self.rect.y - self.surface_offset_y) - self.camera.rect.y

            # Draw me with draw coords
            NATIVE_SURF.blit(
                self.current_sprite_sheet, (xds, yds), self.region
            )

        # Debug draw states
        if self.game.is_debug:

            # Base
            x = self.rect.x - self.camera.rect.x
            y = self.rect.y - self.camera.rect.y

            # State
            self.game.debug_draw.add(
                {
                    "type": "text",
                    "layer": 3,
                    "x": x,
                    "y": y - FONT_H,
                    "text": f"state: {self.state}"
                }
            )

            # Facing
            self.game.debug_draw.add(
                {
                    "type": "text",
                    "layer": 3,
                    "x": x,
                    "y": y - (2 * FONT_H) - 1,
                    "text": f"face: {self.facing_direction}"
                }
            )

            # On wall?
            self.game.debug_draw.add(
                {
                    "type": "text",
                    "layer": 3,
                    "x": x,
                    "y": y - (3 * FONT_H) - 2,
                    "text": f"wall: {self.kinematic.is_on_wall}"
                }
            )

            # On floor?
            self.game.debug_draw.add(
                {
                    "type": "text",
                    "layer": 3,
                    "x": x,
                    "y": y - (4 * FONT_H) - 3,
                    "text": f"floor: {self.kinematic.is_on_floor}"
                }
            )

            # Invincible?
            self.game.debug_draw.add(
                {
                    "type": "text",
                    "layer": 3,
                    "x": x,
                    "y": y - (5 * FONT_H) - 4,
                    "text": f"invicible: {self.is_invincible}"
                }
            )

            # Name?
            self.game.debug_draw.add(
                {
                    "type": "text",
                    "layer": 3,
                    "x": x,
                    "y": y - (6 * FONT_H) - 5,
                    "text": f"name: {self.name}"
                }
            )

    def update(self, dt):
        # Update animation node
        self.animator.update(dt)

        # Update y velocity with gravity
        self.velocity.y += self.gravity * dt
        self.velocity.y = min(self.velocity.y, self.max_fall)

        # Update x velocity with direction
        self.velocity.x = pg.math.lerp(
            self.velocity.x,
            self.direction * self.max_run,
            self.run_lerp_weight
        )
        if abs(self.velocity.x) < 0.001:
            self.velocity.x = 0

        # Was on floor for hurt state
        # Hurt state does not have fall state, need to manually remove velocity when falling
        old_on_floor = self.kinematic.is_on_floor

        # Update pos with vel
        self.kinematic.move(dt)

        # If previously is thin false was true, then I had moved down by 1px
        self.is_thin_fall = False

        # Update facing direction and old facing direction
        if self.direction != 0:
            self.old_facing_direction = self.facing_direction

        # Get horizontal input direction
        self.direction = self.game.is_right_pressed - self.game.is_left_pressed

        # Update facing direction and old facing direction
        if self.direction != 0:
            self.facing_direction = self.direction

        # Idle
        if self.state == "idle":

            # Exit logic first

            # Exit to down if next frame going down is empty pixel
            if not self.kinematic.is_on_floor:
                self.set_state("down")
                return

            # Exit to up if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I just press jump this frame
                if self.game.is_jump_just_pressed:
                    self.set_state("up")
                    return

            # Exit to run if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I am pressing direction AND next frame is NOT solid pixel wall? Run
                if self.direction != 0 and not self.kinematic.is_on_wall:
                    self.set_state("run")
                    return

            # Exit to crouch if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I am holding down crouch this frame
                if self.game.is_down_pressed:
                    self.set_state("crouch")
                    return

            # Then state logic

            # I am invincible? Start timer toggle it back to normal
            if self.is_invincible == True:
                self.invincibility_timer.update(dt)

            # I am invincible?
            if self.is_invincible:
                # Flip hidden back and fort each frame
                self.is_hidden = not self.is_hidden

        # Run
        elif self.state == "run":

            # Exit logic first

            # Exit to down if next frame going down is empty pixel
            if not self.kinematic.is_on_floor:
                self.set_state("down")
                return

            # Exit to idle if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I am not pressing anything or next frame is solid pixel wall? Idle
                if self.direction == 0 or self.kinematic.is_on_wall:
                    self.set_state("idle")
                    return

            # Exit to up if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I just press jump this frame
                if self.game.is_jump_just_pressed:
                    self.set_state("up")
                    return

            # Exit to crouch if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I am holding down crouch this frame
                if self.game.is_down_pressed:
                    self.set_state("crouch")
                    return

            # Then state logic

            # Update sprite flip / no flip with facing
            if self.facing_direction == 1:
                self.current_sprite_sheet = self.sprite_sheet
            elif self.facing_direction == -1:
                self.current_sprite_sheet = self.sprite_sheet_flip

            # Face direction prev was different?
            if self.old_facing_direction != self.facing_direction:
                # Play turn animation
                self.animator.set_current_animation("turn")

            # I am invincible? Start timer toggle it back to normal
            if self.is_invincible == True:
                self.invincibility_timer.update(dt)

            # I am invincible?
            if self.is_invincible:
                # Flip hidden back and fort each frame
                self.is_hidden = not self.is_hidden

        # Crouch
        elif self.state == "crouch":

            # Exit logic first

            # Exit to down if next frame going down is empty pixel
            if not self.kinematic.is_on_floor:
                self.set_state("down")
                return

            # Exit to idle if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I am not pressing anything or next frame is solid pixel wall? Idle
                if self.direction == 0 or self.kinematic.is_on_wall:
                    # Not pressing down?
                    if not self.game.is_down_pressed:
                        self.set_state("idle")
                        return

            # Next frame going down is solid pixel?
            if self.kinematic.is_on_floor:
                # Down is held? And jump was just pressed?
                if self.game.is_down_pressed and self.game.is_jump_just_pressed:
                    # If solid pixel is thin
                    if self.collided_cell_type == "Thin":
                        # Set pass thru to true, after move, next frame this will be set to false
                        self.is_thin_fall = True
                        return
                    else:
                        # If solid pixel is NOT thin? Exit up
                        self.set_state("up")
                        return

            # Exit to run if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I am pressing direction AND next frame is NOT solid pixel wall? Run
                if self.direction != 0 and not self.kinematic.is_on_wall:
                    # Not pressing down?
                    if not self.game.is_down_pressed:
                        self.set_state("run")
                        return

            # Then state logic

            # Remove direction input, next frame cannot move
            self.direction = 0

            # Update sprite flip / no flip with facing
            if self.facing_direction == 1:
                self.current_sprite_sheet = self.sprite_sheet

                # Since direction is 0, need to update old face here myself
                self.old_facing_direction = 1

            elif self.facing_direction == -1:
                self.current_sprite_sheet = self.sprite_sheet_flip

                # Since direction is 0, need to update old face here myself
                self.old_facing_direction = -1

            # I am invincible? Start timer toggle it back to normal
            if self.is_invincible == True:
                self.invincibility_timer.update(dt)

            # I am invincible?
            if self.is_invincible:
                # Flip hidden back and fort each frame
                self.is_hidden = not self.is_hidden

        # Up
        elif self.state == "up":

            # Exit logic first

            # If vel is going down? Exit to down
            if self.velocity.y > 0:
                self.set_state("down")
                return

            # Then state logic

            # Jump was released while going up? Heavy gravity
            if self.game.is_jump_just_released == True:
                self.gravity = self.heavy_gravity

            # Update sprite flip / no flip with facing
            if self.facing_direction == 1:
                self.current_sprite_sheet = self.sprite_sheet
            elif self.facing_direction == -1:
                self.current_sprite_sheet = self.sprite_sheet_flip

            # I am invincible? Start timer toggle it back to normal
            if self.is_invincible == True:
                self.invincibility_timer.update(dt)

            # I am invincible?
            if self.is_invincible:
                # Flip hidden back and fort each frame
                self.is_hidden = not self.is_hidden

        # Down
        elif self.state == "down":

            # Exit to idle if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I am not pressing anything or next frame is solid pixel wall? Idle
                if self.direction == 0 or self.kinematic.is_on_wall:
                    self.set_state("idle")
                    return

            # Exit to up if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I just press jump this frame
                if self.game.is_jump_just_pressed:
                    self.set_state("up")
                    return

            # Exit to run if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I am pressing direction AND next frame is NOT solid pixel wall? Run
                if self.direction != 0 and not self.kinematic.is_on_wall:
                    self.set_state("run")
                    return

            # Exit to crouch if next frame going down is floor
            if self.kinematic.is_on_floor:
                # I am holding down crouch this frame
                if self.game.is_down_pressed:
                    self.set_state("crouch")
                    return

            # Then state logic

            # Update sprite flip / no flip with facing
            if self.facing_direction == 1:
                self.current_sprite_sheet = self.sprite_sheet
            elif self.facing_direction == -1:
                self.current_sprite_sheet = self.sprite_sheet_flip

            # I am invincible? Start timer toggle it back to normal
            if self.is_invincible == True:
                self.invincibility_timer.update(dt)

            # I am invincible?
            if self.is_invincible:
                # Flip hidden back and fort each frame
                self.is_hidden = not self.is_hidden

        # Hurt
        elif self.state == "hurt":

            # Exit is done by hurt timer end callback

            # Then state logic

            # Fell off while sliding in hurt? Reset velocity
            if old_on_floor and not self.kinematic.is_on_floor:
                self.velocity.y = 0

            # Override player input with the pain direction from
            self.direction = self.pain_direction_from

            # Count the timer down
            self.hurt_timer.update(dt)

            # Flip hidden back and fort each frame
            self.is_hidden = not self.is_hidden

        # Update my camera anchor to follow me
        self.camera_anchor[0] = self.rect.center[0] + (
            self.facing_direction * TILE_S
        )
        self.camera_anchor[1] = self.rect.center[1]

    # Set state
    def set_state(self, value):
        old_state = self.state
        self.state = value

        # From idle
        if old_state == "idle":

            # To run
            if self.state == "run":

                # Update sprite flip / no flip with facing
                if self.facing_direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.facing_direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip

                # Face direction prev was SAME?
                if self.old_facing_direction == self.facing_direction:
                    # Play run transition animation
                    self.animator.set_current_animation("idle_to_run")

                # Face direction prev was different?
                elif self.old_facing_direction != self.facing_direction:
                    # Play turn to run transition animation
                    self.animator.set_current_animation("turn")

            # To crouch
            elif self.state == "crouch":
                # Play crouch animation
                self.animator.set_current_animation("crouch")

            # To up
            elif self.state == "up":
                # Set jump vel
                self.velocity.y = self.jump_vel

                # Play up animation
                self.animator.set_current_animation("up")

            # To down
            elif self.state == "down":
                # Remove grav build up if fall off cliff
                self.velocity.y = 0

                # set Heavy gravity
                self.gravity = self.heavy_gravity

                # Play up down transition animation
                self.animator.set_current_animation("up_to_down")

            # To hurt
            elif self.state == "hurt":
                # Prevent from going up, (as if falling)
                self.velocity.y = 0

                # Slow down max run
                self.max_run = self.hurt_max_run

                # Play hurt animation
                self.animator.set_current_animation("hurt")

        # From run
        elif old_state == "run":
            # To idle
            if self.state == "idle":
                # Play run_to_idle animation
                self.animator.set_current_animation("run_to_idle")

            # To crouch
            elif self.state == "crouch":
                # Play crouch animation
                self.animator.set_current_animation("crouch")

            # To up
            elif self.state == "up":
                # Set jump vel
                self.velocity.y = self.jump_vel

                # Play up animation
                self.animator.set_current_animation("up")

            # To down
            elif self.state == "down":
                # Remove grav build up
                self.velocity.y = 0

                # set Heavy gravity
                self.gravity = self.heavy_gravity

                # Play up down transition animation
                self.animator.set_current_animation("up_to_down")

            # To hurt
            elif self.state == "hurt":
                # If was going up, stop it
                self.velocity.y = 0

                # Slow down max run
                self.max_run = self.hurt_max_run

                # Play hurt animation
                self.animator.set_current_animation("hurt")

        # From crouch
        elif old_state == "crouch":
            # To idle
            if self.state == "idle":
                # Play idle animation
                self.animator.set_current_animation("crouch_to_idle")

            # To run
            elif self.state == "run":

                # Update sprite flip / no flip with facing
                if self.facing_direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.facing_direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip

                # Face direction prev was SAME?
                if self.old_facing_direction == self.facing_direction:
                    # Play run transition animation
                    self.animator.set_current_animation("idle_to_run")

                # Face direction prev was different?
                elif self.old_facing_direction != self.facing_direction:
                    # Play turn to run transition animation
                    self.animator.set_current_animation("turn")

            # To up
            elif self.state == "up":
                # Set jump vel
                self.velocity.y = self.jump_vel

                # Play up animation
                self.animator.set_current_animation("up")

            # To down
            elif self.state == "down":
                # Remove grav build up
                self.velocity.y = 0

                # set Heavy gravity
                self.gravity = self.heavy_gravity

                # Play up down transition animation
                self.animator.set_current_animation("up_to_down")

            # To hurt
            elif self.state == "hurt":
                # If was going up, stop it
                self.velocity.y = 0

                # Slow down max run
                self.max_run = self.hurt_max_run

                # Play hurt animation
                self.animator.set_current_animation("hurt")

        # From up
        elif old_state == "up":
            # To down
            if self.state == "down":
                # set Heavy gravity
                self.gravity = self.heavy_gravity

                # Play up down transition animation
                self.animator.set_current_animation("up_to_down")

            # To hurt
            elif self.state == "hurt":
                # If was going up, stop it
                self.velocity.y = 0

                # Slow down max run
                self.max_run = self.hurt_max_run

                # Play hurt animation
                self.animator.set_current_animation("hurt")

        # From down
        elif old_state == "down":
            # Reset gravity
            self.gravity = self.normal_gravity

            # To idle
            if self.state == "idle":
                # Play land animation
                self.animator.set_current_animation("land")

            # To run
            elif self.state == "run":

                # Update sprite flip / no flip with facing
                if self.facing_direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.facing_direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip

                # Face direction prev was SAME?
                if self.old_facing_direction == self.facing_direction:
                    # Play run transition animation
                    self.animator.set_current_animation("idle_to_run")

                # Face direction prev was different?
                elif self.old_facing_direction != self.facing_direction:
                    # Play turn to run transition animation
                    self.animator.set_current_animation("turn")

            # To crouch
            elif self.state == "crouch":
                # Play crouch animation
                self.animator.set_current_animation("crouch")

            # To up
            elif self.state == "up":
                # Set jump vel
                self.velocity.y = self.jump_vel

                # Play up animation
                self.animator.set_current_animation("up")

            # To hurt
            elif self.state == "hurt":
                # If was going up, stop it
                self.velocity.y = 0

                # Slow down max run
                self.max_run = self.hurt_max_run

                # Play hurt animation
                self.animator.set_current_animation("hurt")

        # From hurt
        elif old_state == "hurt":
            # Reset max run
            self.max_run = self.normal_max_run

            # To idle
            if self.state == "idle":
                # Play land animation
                self.animator.set_current_animation("land")

            # To run
            elif self.state == "run":

                # Update sprite flip / no flip with facing
                if self.facing_direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                elif self.facing_direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip

                # Face direction prev was SAME?
                if self.old_facing_direction == self.facing_direction:
                    # Play run transition animation
                    self.animator.set_current_animation("idle_to_run")

                # Face direction prev was different?
                elif self.old_facing_direction != self.facing_direction:
                    # Play turn to run transition animation
                    self.animator.set_current_animation("turn")

            # To crouch
            elif self.state == "crouch":
                # Play crouch animation
                self.animator.set_current_animation("crouch")

            # To up
            elif self.state == "up":
                # Set jump vel
                self.velocity.y = self.jump_vel

                # Play up animation
                self.animator.set_current_animation("up")

            # To down
            elif self.state == "down":
                # Remove grav build up if fall off cliff
                self.velocity.y = 0

                # set Heavy gravity
                self.gravity = self.heavy_gravity

                # Play up down transition animation
                self.animator.set_current_animation("up_to_down")
