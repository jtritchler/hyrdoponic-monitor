import board
import busio
import adafruit_ds18x20
import adafruit_onewire.bus

class TemperatureSensor:
    """
    A class to access a temperature sensor.
    """

    def __init__(self, port: board.Pin):
        """
        Initializes the TemperatureSensor class.

        :param port: The port to which the temperature sensor is connected.
        """
        self.port = port
        self.sensor = self._initialize_sensor()

    def _initialize_sensor(self):
        """
        Initializes the temperature sensor.

        :return: The initialized temperature sensor.
        """
        try:
            onewire_bus = adafruit_onewire.bus.OneWireBus(self.port)
        except ValueError:
            raise ValueError("Unsupported port")

        devices = onewire_bus.scan()
        if not devices:
            raise RuntimeError("No temperature sensors found")

        return adafruit_ds18x20.DS18X20(onewire_bus, devices[0])

    def read_temperature(self) -> float:
        """
        Reads the temperature from the sensor.

        :return: The temperature in Celsius.
        """
        return self.sensor.temperature