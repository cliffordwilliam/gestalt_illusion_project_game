from constants import *
from nodes.animator import Animator
from nodes.kinematic import Kinematic
from nodes.timer import Timer


class Goblin:
    def __init__(self, id, sprite_sheet, sprite_sheet_flip, animation_data, camera, xds, yds, game, room, quadtree, player):
        # Get player
        self.player = player

        # Get game
        self.game = game

        # Get room
        self.room = room

        # Get camera
        self.camera = camera

        # Get quadtree
        self.quadtree = quadtree

        # Id for quadtree bookeeping, for quick relocation in quad
        self.id = id

        # Name
        self.name = "Goblin"

        # Parents load once and pass to me
        self.sprite_sheet = sprite_sheet
        self.sprite_sheet_flip = sprite_sheet_flip
        self.current_sprite_sheet = self.sprite_sheet

        # Parents load once and pass to me
        self.aniamtion_data = animation_data

        # Surface offset
        self.surface_offset_x = 37
        self.surface_offset_y = 30

        # Init starting region
        self.region = self.aniamtion_data["idle"]["frames_list"][0]["region"]

        # Rect
        self.rect = pg.FRect(0, 0, 6, 31)
        self.rect.midbottom = (xds + (TILE_S // 2), yds + TILE_S)
        # self.rect.y -= self.rect.height - TILE_S

        # State
        self.state = "idle"

        # Direction input, updated by timer and wall / when not on floor
        self.direction = 0

        # Animator node
        self.animator = Animator(self, self.aniamtion_data, "idle")
        self.animator.add_event_listener(
            self.on_attack_animation_end, "animation_end"
        )

        # Movement
        self.max_run = 0.017
        self.max_fall = 0.270
        self.gravity = 0.000533
        self.velocity = Vector2()

        # Kinematic
        self.kinematic = Kinematic(
            self,
            self.game,
            self.room,
            self.camera,
            self.quadtree
        )

        # Timer to toggle between idle and run
        self.idle_timer = Timer(2000)
        self.run_timer = Timer(4000)
        self.idle_timer.add_event_listener(self.on_idle_timer_end, "timer_end")
        self.run_timer.add_event_listener(self.on_run_timer_end, "timer_end")

        # For indicating the sprite flip or not, easier to read
        self.facing_direction = 1

        # On player enter go to attack
        self.aggro_rect = pg.FRect(0, 0, 80, 47)

        # On player enter call player hit
        self.hit_rect = pg.FRect(0, 0, 40, 31)

    # Animation callback
    def on_attack_animation_end(self):
        # Player is still in the aggor rect, play the attack animation again
        if self.player in self.quadtree.search(self.aggro_rect):
            # region Set current sprite sheet input based on where player is right now
            # Player on left or right? Positive rel_player_pos = right
            rel_player_pos = self.player.rect.center[0] - self.rect.center[0]

            # Only update sprite sheet if player is not exactly where I am in x axis, flip or no flip sprite sheet
            if rel_player_pos != 0:

                # I am facing right?
                if self.current_sprite_sheet == self.sprite_sheet:
                    # Player on my left?
                    if rel_player_pos < 0:
                        # Update sprite sheet to flip (this will determine dir input for vel in run entry)
                        self.current_sprite_sheet = self.sprite_sheet_flip

                # I am facing left?
                elif self.current_sprite_sheet == self.sprite_sheet_flip:
                    # Player on my right?
                    if rel_player_pos > 0:
                        # Update sprite sheet to normal (this will determine dir input for vel in run entry)
                        self.current_sprite_sheet = self.sprite_sheet

            # Replay the attack anim, stay in attack state
            self.animator.set_current_animation("attack")

        # Player is not in aggro, exit to idle state
        else:
            self.set_state("idle")

    # Timer callback
    def on_idle_timer_end(self):
        self.set_state("run")

    # Timer callback
    def on_run_timer_end(self):
        self.set_state("idle")

    # Called by kinematic
    def on_collide(self, cells):
        # Unpack all found collided cells type and name
        for cell in cells:
            # Prioritize solids, found solid first? Stop
            if cell["sprite_type"] == "solid":
                return True

            # Found door next? Stop
            elif cell["sprite_type"] == "door":
                return True

            # Found thin? Stop
            elif cell["sprite_type"] == "thin":
                return True

    def draw(self):
        xds = (self.rect.x - self.surface_offset_x) - self.camera.rect.x
        yds = (self.rect.y - self.surface_offset_y) - self.camera.rect.y
        NATIVE_SURF.blit(
            self.current_sprite_sheet,
            (xds, yds),
            self.region
        )

        if self.game.is_debug:
            x = self.aggro_rect.x - self.camera.rect.x
            y = self.aggro_rect.y - self.camera.rect.y
            w = self.aggro_rect.width
            h = self.aggro_rect.height

            # Owner real rect
            self.game.debug_draw.add(
                {
                    "type": "rect",
                    "layer": 1,
                    "rect": [x, y, w, h],
                    "color": "red",
                    "width": 1
                }
            )

            x = self.hit_rect.x - self.camera.rect.x
            y = self.hit_rect.y - self.camera.rect.y
            w = self.hit_rect.width
            h = self.hit_rect.height

            # Owner real rect
            self.game.debug_draw.add(
                {
                    "type": "rect",
                    "layer": 1,
                    "rect": [x, y, w, h],
                    "color": "yellow",
                    "width": 1
                }
            )

    def update(self, dt):
        # Update animation node
        self.animator.update(dt)

        # region Update velocity with gravity
        self.velocity.y += self.gravity * dt
        self.velocity.y = min(self.velocity.y, self.max_fall)
        # endregion Update velocity with gravity

        # region Update x velocity with direction
        self.velocity.x = self.direction * self.max_run
        # endregion Update x velocity with direction

        # Get old position
        old_position_x = self.rect.x
        old_position_y = self.rect.y

        # Update pos with vel
        self.kinematic.move(dt)

        # Update aggro rect to follow rect
        self.aggro_rect.midbottom = self.rect.midbottom

        # Update hit rect to follow rect, depends on my sprite sheet
        if self.current_sprite_sheet == self.sprite_sheet:
            self.hit_rect.midleft = self.rect.center
            self.hit_rect.y -= TILE_S
        elif self.current_sprite_sheet == self.sprite_sheet_flip:
            self.hit_rect.midright = self.rect.center
            self.hit_rect.y -= TILE_S

        # Idle
        if self.state == "idle":
            self.idle_timer.update(dt)

            # Exit to run are taken care of timers

            # Exit to attack
            if self.player in self.quadtree.search(self.aggro_rect):
                self.set_state("attack")
                return

            # In state logic

        # Run
        elif self.state == "run":
            self.run_timer.update(dt)

            # Exit to idle are taken care of timers

            # Exit to attack
            if self.player in self.quadtree.search(self.aggro_rect):
                self.set_state("attack")
                return

            # In state logic
            # Walked off cliff?
            if not self.kinematic.is_on_floor:
                # Flip
                self.direction *= -1

                # Update sprite to follow direction
                if self.direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                    self.facing_direction = 1
                elif self.direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip
                    self.facing_direction = -1

                # Go back in time (before off floor is true), set current pos to prev frame pos
                self.rect.x = old_position_x
                self.rect.y = old_position_y

            # Pressing against wall?
            elif self.kinematic.is_on_wall:
                # Flip direction
                self.direction *= -1

                # Update sprite to follow direction
                if self.direction == 1:
                    self.current_sprite_sheet = self.sprite_sheet
                    self.facing_direction = 1
                elif self.direction == -1:
                    self.current_sprite_sheet = self.sprite_sheet_flip
                    self.facing_direction = -1

                # Go back in time (before on wall is true), set current pos to prev frame pos
                self.rect.x = old_position_x + self.direction
                self.rect.y = old_position_y

        # Idle
        elif self.state == "attack":
            # Exit to idle are taken care of animation end callback

            # In state logic

            # During active hit box frame
            if self.animator.frame_index == 2 or self.animator.frame_index == 3:
                # Player inside it?
                if self.hit_rect.colliderect(self.player):

                    # Player on left or right? Positive rel_player_pos = right
                    rel_player_pos = self.player.rect.center[0] - \
                        self.rect.center[0]

                    pain_direction_from = -1 if rel_player_pos < 0 else 1

                    # Call player hurt callback
                    self.player.ouch(pain_direction_from)

    # Set state
    def set_state(self, value):
        old_state = self.state
        self.state = value

        # From idle
        if old_state == "idle":
            # To run
            if self.state == "run":
                self.run_timer.reset()

                # Set direction input based on sprite sheet right now
                # Use current sprite sheet to determine direction
                if self.current_sprite_sheet == self.sprite_sheet:
                    self.direction = 1
                elif self.current_sprite_sheet == self.sprite_sheet_flip:
                    self.direction = -1

                # Play run animation
                self.animator.set_current_animation("run")

            # To attack
            elif self.state == "attack":
                # Set current sprite sheet input based on where player is right now
                # Player on left or right? Positive rel_player_pos = right
                rel_player_pos = self.player.rect.center[0] - \
                    self.rect.center[0]

                # Only update sprite sheet if player is not exactly where I am in x axis
                if rel_player_pos != 0:

                    # I am facing right?
                    if self.current_sprite_sheet == self.sprite_sheet:
                        # Player on my left?
                        if rel_player_pos < 0:
                            # Update sprite sheet to flip (this will determine dir input for vel in run entry)
                            self.current_sprite_sheet = self.sprite_sheet_flip

                    # I am facing left?
                    elif self.current_sprite_sheet == self.sprite_sheet_flip:
                        # Player on my right?
                        if rel_player_pos > 0:
                            # Update sprite sheet to normal (this will determine dir input for vel in run entry)
                            self.current_sprite_sheet = self.sprite_sheet

                # Set direction input to 0
                self.direction = 0

                # Play attack animation
                self.animator.set_current_animation("attack")

        # From run
        elif old_state == "run":
            # To idle
            if self.state == "idle":
                self.idle_timer.reset()

                # Set direction input to 0
                self.direction = 0

                # Play idle animation
                self.animator.set_current_animation("idle")

            # To attack
            elif self.state == "attack":
                # Set current sprite sheet input based on where player is right now
                # Player on left or right? Positive rel_player_pos = right
                rel_player_pos = self.player.rect.center[0] - \
                    self.rect.center[0]

                # Only update sprite sheet if player is not exactly where I am in x axis
                if rel_player_pos != 0:

                    # I am facing right?
                    if self.current_sprite_sheet == self.sprite_sheet:
                        # Player on my left?
                        if rel_player_pos < 0:
                            # Update sprite sheet to flip (this will determine dir input for vel in run entry)
                            self.current_sprite_sheet = self.sprite_sheet_flip

                    # I am facing left?
                    elif self.current_sprite_sheet == self.sprite_sheet_flip:
                        # Player on my right?
                        if rel_player_pos > 0:
                            # Update sprite sheet to normal (this will determine dir input for vel in run entry)
                            self.current_sprite_sheet = self.sprite_sheet

                # Set direction input to 0
                self.direction = 0

                # Play attack animation
                self.animator.set_current_animation("attack")

        # From run
        elif old_state == "attack":
            # To idle
            if self.state == "idle":
                self.idle_timer.reset()

                # Set direction input to 0
                self.direction = 0

                # Play idle animation
                self.animator.set_current_animation("idle")
