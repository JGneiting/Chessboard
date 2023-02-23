import board
import neopixel
from BoardFiles import set_5v
from NeopixelLights.LightManager import BoardLights

set_5v(True)

pixels = BoardLights()
pixels.indicate_player("White")

# pixels.highlight_square("B1", (255, 0, 255))
# pixels.highlight_square("C1")
# pixels.highlight_square("D1", (255, 0, 255))
# pixels.highlight_square("E1")
# pixels.highlight_square("F1", (255, 0, 255))
# pixels.highlight_square("G1")
# pixels.highlight_square("H1", (255, 0, 255))


i = 0
while True:

    key = input("Enter square: ")
    if key == "q":
        break
    i += 1

    pixels.highlight_square(key)
    if i%2 == 1:
        pixels.indicate_player("Black")
    else:
        pixels.indicate_player("White")



set_5v(False)
