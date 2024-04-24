from constants import *


class Background:
    def __init__(self, sprite_sheet, camera, stage_no, desired_background_names):
        self.sprite_sheet_surf = sprite_sheet
        self.camera = camera
        self.stage_no = stage_no
        self.desired_background_names = desired_background_names

    def update_prop(self, sprite_sheet, stage_no, desired_background_names):
        self.sprite_sheet_surf = sprite_sheet
        self.stage_no = stage_no
        self.desired_background_names = desired_background_names

    def draw(self):
        # Stage 1 backgrounds
        if self.stage_no == 1:
            if "sky" in self.desired_background_names:
                x = (-self.camera.rect.x * 0.05) % NATIVE_W
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x, 0), (0, 0, 320, 160)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x - NATIVE_W, 0), (0, 0, 320, 160)
                )

            if "clouds" in self.desired_background_names:
                x = (-self.camera.rect.x * 0.1) % NATIVE_W
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x, 0), (0, 160, 320, 160)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x - NATIVE_W, 0), (0, 160, 320, 160)
                )

            if "temple" in self.desired_background_names:
                x = (-self.camera.rect.x * 0.25) % NATIVE_W
                y = (-self.camera.rect.y * 0.25) % NATIVE_H
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x, y), (0, 320, 320, 160)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x - NATIVE_W, y), (0, 320, 320, 160)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x, y - NATIVE_H), (0, 320, 320, 160)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x - NATIVE_W, y - NATIVE_H), (0, 320, 320, 160)
                )

            if "trees" in self.desired_background_names:
                x = (-self.camera.rect.x * 0.5) % NATIVE_W
                # 1
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x, 32), (432, 368, 80, 144)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x - NATIVE_W, 32), (432, 368, 80, 144)
                )
                # 2
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf, (x + 96, 64),
                    (432, 368, 80, 144)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x + 96 - NATIVE_W, 64), (432, 368, 80, 144)
                )
                # 3
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf, (x + 160, 32),
                    (432, 368, 80, 144)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x + 160 - NATIVE_W, 32), (432, 368, 80, 144)
                )
                # 4
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf, (x + 224, 16),
                    (432, 368, 80, 144)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x + 224 - NATIVE_W, 16), (432, 368, 80, 144)
                )

            if "blue_glow" in self.desired_background_names:
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (0, 48), (0, 480, 320, 128)
                )

        # Stage 2 backgrounds
        if self.stage_no == 2:
            if "rock" in self.desired_background_names:
                x = (-self.camera.rect.x * 0.25) % NATIVE_W
                y = (-self.camera.rect.y * 0.25) % NATIVE_H
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x, y), (0, 0, 320, 160)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x - NATIVE_W, y), (0, 0, 320, 160)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x, y - NATIVE_H), (0, 0, 320, 160)
                )
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (x - NATIVE_W, y - NATIVE_H), (0, 0, 320, 160)
                )

            if "orange_glow" in self.desired_background_names:
                NATIVE_SURF.blit(
                    self.sprite_sheet_surf,
                    (0, 48), (0, 160, 320, 128)
                )
