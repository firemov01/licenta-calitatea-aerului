from enum import Enum
class WindowState(Enum):
    OPENED = 'opened'
    CLOSED = 'closed'

class Measurement:
    def __init__(self, humidity, temperature, air_quality, window_state):
        self.humidity = humidity
        self.temperature = temperature
        self.air_quality = air_quality
        self.window_state = window_state

    def __str__(self):
        return 'Humidity: ' + str(self.humidity) + ' Temperature: ' + str(self.temperature) + ' Air Quality: ' + str(self.air_quality) + ' Window State: ' + str(self.window_state)