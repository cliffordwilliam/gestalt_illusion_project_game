from constants import *
from nodes.animator import Animator
from nodes.kinematic import Kinematic
from nodes.timer import Timer


class Goblin:
    def __init__(self, id, sprite_sheet, sprite_sheet_flip, animation_data, camera, xds, yds, game, room, quadtree):
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
        self.aggro_rect = pg.FRect(0, 0, 80, 31)

        # On player enter call player hit
        self.hit_rect = pg.FRect(0, 0, 40, 31)

    # Animation callback
    def on_attack_animation_end(self):
        pass

    # Timer callback
    def on_idle_timer_end(self):
        self.set_state("run")

    # Timer callback
    def on_run_timer_end(self):
        self.set_state("idle")

    # Called by kinematic
    def on_collide(self, cells):
        pass

    def draw(self):
        xds = (self.rect.x - self.surface_offset_x) - self.camera.rect.x
        yds = (self.rect.y - self.surface_offset_y) - self.camera.rect.y
        NATIVE_SURF.blit(
            self.current_sprite_sheet,
            (xds, yds),
            self.region
        )

    def update(self, dt):
        # Update animation node
        self.animator.update(dt)

        # Update pos with vel
        self.kinematic.move(dt)
