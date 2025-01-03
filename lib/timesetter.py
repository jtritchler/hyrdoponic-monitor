import time
import rtc
import adafruit_ntp
from wifimanager import WiFiManager

class TimeSetter:
    """
    A class to get the time using the adafruit_ntp library and set the time using the rtc library.
    """

    def __init__(self, wifi: WiFiManager, tz_offset: int = 0):
        """
        Initializes the TimeSetter class.

        :param wifi: An instance of the WiFiManager class to handle the network connection.
        """
        self.wifi = wifi
        self.pool = self.wifi.pool
        self.ntp = adafruit_ntp.NTP(self.pool, tz_offset=tz_offset, server="pool.ntp.org")
        self.rtc = rtc.RTC()

    def set_time(self) -> None:
        """
        Gets the current time from an NTP server and sets the system time.
        """
        try:
            current_time = self.ntp.datetime
            self.rtc.datetime = current_time
            print("Time set successfully:", current_time)
        except Exception as e:
            print("Failed to set time:", e)
