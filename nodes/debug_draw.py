from constants import *


class DebugDraw:

    def __init__(self):
        self.layers = [
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        ]

    def add(self, obj):
        layer = obj["layer"]
        self.layers[layer].append(obj)

    def draw(self):
        # Loop over each layer
        for layer in self.layers:
            for obj in layer:

                # Text?
                if obj["type"] == "text":
                    FONT.render_to(
                        NATIVE_SURF,
                        (obj["x"], obj["y"]),
                        obj["text"],
                        "white",
                        "black"
                    )

                # Rect?
                if obj["type"] == "rect":
                    pg.draw.rect(
                        NATIVE_SURF,
                        obj["color"],
                        obj["rect"],
                        obj["width"],
                    )

                # Rect?
                if obj["type"] == "line":
                    pg.draw.line(
                        NATIVE_SURF,
                        obj["color"],
                        obj["start"],
                        obj["end"],
                        obj["width"],
                    )

                # Rect?
                if obj["type"] == "circle":
                    pg.draw.circle(
                        NATIVE_SURF,
                        obj["color"],
                        obj["center"],
                        obj["radius"],
                    )

                # Rect?
                if obj["type"] == "surf":
                    NATIVE_SURF.blit(
                        obj["surf"],
                        (obj["x"], obj["y"]),
                    )

        # Empty it
        self.layers = [
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        ]
