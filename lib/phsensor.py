import json
import analogio
import board
import time
from sdcard import SDCard

class PhSensor:
    '''
    A class to access the pH value from an Atlas Scientific analog pH sensor.
    '''

    def __init__(self, pin: board.Pin, sd_card: SDCard, calibration_file: str):
        '''
        Initializes the PHSensor class.

        :param pin: The pin to which the pH sensor is connected.
        :param sd_card: An instance of the SDCard class.
        :param calibration_file: The file path to save/load the calibration data.
        '''
        self.pin = analogio.AnalogIn(pin)
        self.sd_card = sd_card
        self.calibration_file = calibration_file
        self.calibration_data = self.load_calibration_data()

    def read_voltage(self) -> float:
        '''
        Reads the voltage from the pH sensor.

        :return: The voltage in volts.
        '''
        return (self.pin.value * 3.3) / 65536

    def read_ph(self) -> float:
        '''
        Reads the pH value from the pH sensor.

        :return: The pH value.
        '''
        voltage = self.read_voltage()
        if voltage > self.calibration_data['voltage_7']:
            slope = self.calibration_data['slope_4_7']
            intercept = self.calibration_data['intercept_4_7']
        else:
            slope = self.calibration_data['slope_7_10']
            intercept = self.calibration_data['intercept_7_10']
        ph_value = slope * voltage + intercept
        return ph_value

    def calibrate(self):
        '''
        Calibrates the pH sensor using pH values of 4.00, 7.00, and 10.00.
        '''
        print('Calibrating pH sensor...')

        # Read voltage for pH 4.00
        input('Place the sensor in pH 4.00 solution and press Enter...')
        voltage_4 = self.read_voltage()
        print(f'Voltage at pH 4.00: {voltage_4:.3f} V')

        # Read voltage for pH 7.00
        input('Place the sensor in pH 7.00 solution and press Enter...')
        voltage_7 = self.read_voltage()
        print(f'Voltage at pH 7.00: {voltage_7:.3f} V')

        # Read voltage for pH 10.00
        input('Place the sensor in pH 10.00 solution and press Enter...')
        voltage_10 = self.read_voltage()
        print(f'Voltage at pH 10.00: {voltage_10:.3f} V')

        # Calculate linear regression for pH 4.00 to 7.00
        slope_4_7 = (7.00 - 4.00) / (voltage_7 - voltage_4)
        intercept_4_7 = 7.00 - slope_4_7 * voltage_7

        # Calculate linear regression for pH 7.00 to 10.00
        slope_7_10 = (10.00 - 7.00) / (voltage_10 - voltage_7)
        intercept_7_10 = 10.00 - slope_7_10 * voltage_10

        # Save calibration data to file
        self.calibration_data = {
            'voltage_7': voltage_7,
            'slope_4_7': slope_4_7,
            'intercept_4_7': intercept_4_7,
            'slope_7_10': slope_7_10,
            'intercept_7_10': intercept_7_10
        }
        self.save_calibration_data()

        print('Calibration complete.')
        print(f'Slope (4.00 to 7.00): {slope_4_7:.3f}')
        print(f'Intercept (4.00 to 7.00): {intercept_4_7:.3f}')
        print(f'Slope (7.00 to 10.00): {slope_7_10:.3f}')
        print(f'Intercept (7.00 to 10.00): {intercept_7_10:.3f}')

    def save_calibration_data(self):
        '''
        Saves the calibration data to a file on the SD memory card.
        '''
        data = json.dumps(self.calibration_data)
        self.sd_card.write_file(self.calibration_file, data)

    def load_calibration_data(self):
        '''
        Loads the calibration data from a file on the SD memory card.
        '''
        if self.sd_card.file_exists(self.calibration_file):
            data = self.sd_card.read_file(self.calibration_file)
            return json.loads(data)
        else:
            self.calibrate()
            return self.calibration_data
