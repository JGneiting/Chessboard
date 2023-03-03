import pygame
from BoardFiles import set_5v
import time

if __name__ == "__main__":
    set_5v(False)
    time.sleep(1)
    set_5v(True)

    pygame.mixer.pre_init()
    pygame.init()
    pygame.mixer.init()

    sound = pygame.mixer.Sound("GameSounds/Pirates of the Caribbean Theme.ogg")
    playing = sound.play()
    while playing.get_busy():
        pygame.time.delay(100)
