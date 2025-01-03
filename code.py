# SPDX-FileCopyrightText: 2024 J. Michael Tritchler
#
# SPDX-License-Identifier: MIT

import os
import time
import board
from wifimanager import WiFiManager
from timesetter import TimeSetter
from googlesheetsmanager import GoogleSheetsManager
from sdcard import SDCard
from waterdepthsensor import WaterDepthSensor
from temperaturesensor import TemperatureSensor
from phsensor import PhSensor

# Initialize the SD card
sd_card = SDCard(board.SPI(), board.SD_CS, "/sd")

# Initialize the pH sensor
ph_sensor = PhSensor(board.A5, sd_card, "ph_calibration.json")
# Initialize the water depth sensor
water_depth_sensor = WaterDepthSensor(board.A3, sd_card, "water_depth_calibration.json")
# Initailize the temperature sensor
temp_sensor = TemperatureSensor(board.A4)

# Connect to WiFi
wifi = WiFiManager()
print('Waiting for WiFi connection...')
wifi.connect(
    os.getenv('CIRCUITPY_WIFI_SSID'),
    os.getenv('CIRCUITPY_WIFI_PASSWORD')
)
time.sleep(1)

# Set the system time
time_setter = TimeSetter(wifi, os.getenv('TZ_OFFSET'))
time_setter.set_time()

# Create an instance of the GoogleSheetsManager class
gsm = GoogleSheetsManager(
    wifi,
    os.getenv('GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY'),
    os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL'),
    os.getenv('GOOGLE_SERVICE_ACCOUNT_KID')
)
# Set the Google Sheets ID, Tab, and Cells
sheets_id = os.getenv('GOOGLE_SHEETS_ID')
tab_id = os.getenv('GOOGLE_SHEETS_TAB_ID')
cells = 'A1:D1'

while True:
    ts = time.time()
    try:
        data = [[
            ts,
            f'=EPOCHTODATE({ts} - 28800)',
            f'{temp_sensor.read_temperature():.2f}',
            f'{water_depth_sensor.read_depth():.2f}',
            f'{ph_sensor.read_ph():.2f}'
        ]]
        gsm.write_to_sheet(sheets_id, tab_id, cells, data, append=True)
    except:
        pass
    # Update every 15 minutes
    time.sleep(900)
