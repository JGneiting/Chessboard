from NeopixelLights.LightInterface import LightsInterface


if __name__ == "__main__":
    from NeopixelLights.LightManager import BoardLights
    from BoardFiles import set_5v
    import time
    set_5v(True)
    lights = BoardLights()
    lights.lights[142] = (100, 100, 0)
    lights.flush()

    time.sleep(5)

    set_5v(False)
