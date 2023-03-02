import pygame
from BoardFiles import set_5v

set_5v(True)


pygame.mixer.pre_init()
pygame.init()
pygame.mixer.init()

sound = pygame.mixer.Sound("/home/pi/Music/MooMooMeadows.mp3")
playing = sound.play()
while playing.get_busy():
    pygame.time.delay(100)
