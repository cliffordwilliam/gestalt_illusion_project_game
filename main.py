from constants import *
from nodes.game import Game


# game = Game("JsonEditor")
# game = Game("RoomEditor")
game = Game("World")

# The Main loop
while 1:
    # Fps limit and get dt
    dt = CLOCK.tick(FPS)

    # Use this for game
    # for event in pg.event.get(EVENTS):
    # REMOVE IN BUILD -> EDITOR_EVENTS
    for event in pg.event.get(EDITOR_EVENTS):
        # Update the game input flags
        game.event(event)

    # Draw game current scene
    game.current_scene.draw()

    # Update game current scene
    game.current_scene.update(dt)

    # REMOVE IN BUILD
    game.debug_draw.add(
        {
            "type": "text",
            "layer": 4,
            "x": 0,
            "y": 0,
            "text": f"fps: {int(CLOCK.get_fps())}"
        }
    )

    # Debug draw
    game.debug_draw.draw()

    # Scale the native to window surface
    scaled_native_surf = pg.transform.scale_by(NATIVE_SURF, game.resolution)
    game.window_surf.blit(scaled_native_surf, (0, game.y_offset))
    pg.display.update()

    # Cleanup the just pressed game events for next frame
    game.is_up_just_pressed = False
    game.is_down_just_pressed = False
    game.is_left_just_pressed = False
    game.is_right_just_pressed = False

    game.is_enter_just_pressed = False
    game.is_pause_just_pressed = False
    game.is_jump_just_pressed = False

    # Cleanup the just released game events for next frame
    game.is_up_just_released = False
    game.is_down_just_released = False
    game.is_left_just_released = False
    game.is_right_just_released = False

    game.is_enter_just_released = False
    game.is_pause_just_released = False
    game.is_jump_just_released = False

    # REMOVE IN BUILD (Cleanup the just released game events for next frame)
    game.is_lmb_just_pressed = False
    game.is_rmb_just_pressed = False
    game.is_mmb_just_pressed = False

    game.is_lmb_just_released = False
    game.is_rmb_just_released = False
    game.is_mmb_just_released = False
