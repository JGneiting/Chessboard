import board
import neopixel
from BoardFiles import set_5v
from NeopixelLights.LightManager import BoardLights

set_5v(True)

pixels = BoardLights()

# pixels.highlight_square("B1", (255, 0, 255))
# pixels.highlight_square("C1")
# pixels.highlight_square("D1", (255, 0, 255))
# pixels.highlight_square("E1")
# pixels.highlight_square("F1", (255, 0, 255))
# pixels.highlight_square("G1")
# pixels.highlight_square("H1", (255, 0, 255))


while True:

    key = input("Enter square: ")
    if key == "q":
        break

    pixels.lights.fill((0, 120, 0))
    pixels.highlight_square(key)



set_5v(False)
