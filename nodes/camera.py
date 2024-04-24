from constants import *


class Camera:
    def __init__(self, target=None, game=None):
        # Get game for debug draw
        self.game = game

        self.rect = pg.FRect(0, 0, NATIVE_W, NATIVE_H)
        self.target = target
        self.lerp_weight = 0.01

        self.limit_top = -9999
        self.limit_bottom = 9999
        self.limit_left = -9999
        self.limit_right = 9999

    def set_target(self, value):
        # value = vector
        self.target = value

    def set_limit(self, value):
        # value = rect
        self.limit_top = value.y
        self.limit_bottom = value.y + value.height
        self.limit_left = value.x
        self.limit_right = value.x + value.width

    def update(self, dt):
        # Do not do anything if there is no target, nothing to follow
        if self.target == None:
            return

        # Prevent target to be in a pos where cam is outside of room x
        left = self.limit_left + NATIVE_W // 2
        right = self.limit_right - NATIVE_W // 2
        self.target.x = clamp(self.target.x, left, right)

        # Prevent target to be in a pos where cam is outside of room y
        top = self.limit_top + NATIVE_H // 2
        bottom = self.limit_bottom - NATIVE_H // 2
        self.target.y = clamp(self.target.y, top, bottom)

        # This gets the topleft - lerp works with topleft only
        target_x = self.target.x - (NATIVE_W // 2)
        target_y = self.target.y - (NATIVE_H // 2)

        # Update horizontal position when I am not on target
        if self.rect.x != target_x:
            self.rect.x = lerp(
                self.rect.x,
                target_x,
                self.lerp_weight * dt
            )
            if abs(self.rect.x) < 0.001:
                self.rect.x = 0

            # Snap to target if close enough x
            diff = abs(self.rect.x - target_x)
            if diff < 1:
                self.rect.x = target_x

        # Update vertical position when I am not on target
        if self.rect.y != target_y:
            self.rect.y = lerp(
                self.rect.y,
                target_y,
                self.lerp_weight * dt
            )
            if abs(self.rect.y) < 0.001:
                self.rect.y = 0

            # Snap to target if close enough y
            diff = abs(self.rect.y - target_y)
            if diff < 1:
                self.rect.y = target_y

        # Debug draw
        if self.game != None:
            if self.game.is_debug:
                # Draw my center
                x = (NATIVE_W // 2) - 1
                y = (NATIVE_H // 2) - 1

                self.game.debug_draw.add(
                    {
                        "type": "line",
                        "layer": 5,
                        "start": (x, (NATIVE_H // 2) + 3),
                        "end": (x, (NATIVE_H // 2) - 4),
                        "color": "red",
                        "width": 2
                    }
                )

                self.game.debug_draw.add(
                    {
                        "type": "line",
                        "layer": 5,
                        "start": ((NATIVE_W // 2) + 3, y),
                        "end": ((NATIVE_W // 2) - 4, y),
                        "color": "red",
                        "width": 2
                    }
                )

                # Draw target
                target_center_x = target_x + (NATIVE_W // 2)
                target_center_y = target_y + (NATIVE_H // 2)
                x = target_center_x - self.rect.x
                y = target_center_y - self.rect.y

                self.game.debug_draw.add(
                    {
                        "type": "circle",
                        "layer": 5,
                        "color": "yellow",
                        "center": (x, y),
                        "radius": 2
                    }
                )
