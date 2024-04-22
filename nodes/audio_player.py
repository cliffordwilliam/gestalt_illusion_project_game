import pygame


class SoundManager:
    def __init__(self):
        self.sounds = {}

    def load_sound(self, name, path):
        sound = pygame.mixer.Sound(path)
        self.sounds[name] = sound

    def play_sound(self, name, loop=0):
        if name in self.sounds:
            self.sounds[name].play(loop)

    def stop_sound(self, name):
        if name in self.sounds:
            self.sounds[name].stop()

    def stop_all_sounds(self):
        pygame.mixer.stop()

    def set_volume(self, name, volume):
        if name in self.sounds:
            self.sounds[name].set_volume(volume)

    def get_volume(self, name):
        if name in self.sounds:
            return self.sounds[name].get_volume()
        return None

    def reset_sounds(self):
        self.sounds = {}
