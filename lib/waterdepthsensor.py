import json
import analogio
import board
from sdcard import SDCard

class WaterDepthSensor:
    """
    A class to convert analog input to water depth.
    """

    def __init__(self, pin: board.Pin, sd_card: SDCard, calibration_file: str):
        """
        Initializes the WaterDepthSensor class.

        :param pin: The pin to which the water depth sensor is connected.
        :param sd_card: An instance of the SDCard class.
        :param calibration_file: The file path to save/load the calibration data.
        """
        self.pin = analogio.AnalogIn(pin)
        self.sd_card = sd_card
        self.calibration_file = calibration_file
        self.calibration_data = self.load_calibration_data()

    def read_voltage(self) -> float:
        """
        Reads the voltage from the water depth sensor.

        :return: The voltage in volts.
        """
        return (self.pin.value * 3.3) / 65536

    def read_depth(self) -> float:
        """
        Reads the water depth from the sensor.

        :return: The water depth in inches.
        """
        voltage = self.read_voltage()
        if voltage > self.calibration_data['voltage_6']:
            slope = self.calibration_data['slope_1_6']
            intercept = self.calibration_data['intercept_1_6']
        else:
            slope = self.calibration_data['slope_6_12']
            intercept = self.calibration_data['intercept_6_12']
        depth = slope * voltage + intercept
        return depth

    def calibrate(self):
        """
        Calibrates the water depth sensor using depths of 1 inch, 6 inches, and 12 inches.
        """
        print("Calibrating water depth sensor...")

        # Read voltage for 1 inch
        input("Place the sensor in 1 inch of water and press Enter...")
        voltage_1 = self.read_voltage()
        print(f"Voltage at 1 inch: {voltage_1:.3f} V")

        # Read voltage for 6 inches
        input("Place the sensor in 6 inches of water and press Enter...")
        voltage_6 = self.read_voltage()
        print(f"Voltage at 6 inches: {voltage_6:.3f} V")

        # Read voltage for 12 inches
        input("Place the sensor in 12 inches of water and press Enter...")
        voltage_12 = self.read_voltage()
        print(f"Voltage at 12 inches: {voltage_12:.3f} V")

        # Calculate linear regression for 1 inch to 6 inches
        slope_1_6 = (6.00 - 1.00) / (voltage_6 - voltage_1)
        intercept_1_6 = 6.00 - slope_1_6 * voltage_6

        # Calculate linear regression for 6 inches to 12 inches
        slope_6_12 = (12.00 - 6.00) / (voltage_12 - voltage_6)
        intercept_6_12 = 12.00 - slope_6_12 * voltage_12

        # Save calibration data to file
        self.calibration_data = {
            "voltage_6": voltage_6,
            "slope_1_6": slope_1_6,
            "intercept_1_6": intercept_1_6,
            "slope_6_12": slope_6_12,
            "intercept_6_12": intercept_6_12
        }
        self.save_calibration_data()

        print("Calibration complete.")
        print(f"Slope (1 inch to 6 inches): {slope_1_6:.3f}")
        print(f"Intercept (1 inch to 6 inches): {intercept_1_6:.3f}")
        print(f"Slope (6 inches to 12 inches): {slope_6_12:.3f}")
        print(f"Intercept (6 inches to 12 inches): {intercept_6_12:.3f}")

    def save_calibration_data(self):
        """
        Saves the calibration data to a file on the SD memory card.
        """
        data = json.dumps(self.calibration_data)
        self.sd_card.write_file(self.calibration_file, data)

    def load_calibration_data(self):
        """
        Loads the calibration data from a file on the SD memory card.
        """
        if self.sd_card.file_exists(self.calibration_file):
            data = self.sd_card.read_file(self.calibration_file)
            return json.loads(data)
        else:
            self.calibrate()
            return self.calibration_data
