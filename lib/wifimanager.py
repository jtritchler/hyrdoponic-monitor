import wifi
import socketpool
import ssl
import adafruit_requests

class WiFiManager:
    """
    A class to manage WiFi connections and HTTP requests using CircuitPython.
    """

    def __init__(self):
        """
        Initializes the WiFiManager class.
        """
        self.pool: socketpool.SocketPool = None
        self.requests: adafruit_requests.Session = None

    def connect(self, ssid: str, password: str) -> None:
        """
        Connects to a WiFi network.

        :param ssid: The SSID of the WiFi network.
        :param password: The password of the WiFi network.
        """
        try:
            wifi.radio.connect(ssid, password)
            self.pool = socketpool.SocketPool(wifi.radio)
            self.requests = adafruit_requests.Session(self.pool, ssl.create_default_context())
            print("Connected to WiFi")
        except Exception as e:
            print("Failed to connect to WiFi:", e)

    def reconnect(self, ssid: str, password: str) -> None:
        """
        Reconnects to a WiFi network.

        :param ssid: The SSID of the WiFi network.
        :param password: The password of the WiFi network.
        """
        self.disconnect()
        self.connect(ssid, password)

    def disconnect(self) -> None:
        """
        Disconnects from the WiFi network.
        """
        try:
            wifi.radio.disconnect()
            print("Disconnected from WiFi")
        except Exception as e:
            print("Failed to disconnect from WiFi:", e)
    
    def is_connected(self) -> bool:
        """
        Checks if the WiFi is connected.

        :return: True if connected, False otherwise.
        """
        return wifi.radio.connected

    def get(self, url: str, headers: dict = None, timeout: int = 10) -> str:
        """
        Performs a GET request.

        :param url: The URL to send the GET request to.
        :param headers: Optional headers to include in the GET request.
        :param timeout: Optional timeout for the request in seconds.
        :return: The response text from the GET request.
        """
        try:
            response = self.requests.get(url, headers=headers, timeout=timeout)
            return response.text
        except Exception as e:
            print("GET request failed:", e)
            return None

    def post(self, url: str, data: dict, headers: dict = None, timeout: int = 10) -> str:
        """
        Performs a POST request.

        :param url: The URL to send the POST request to.
        :param data: The data to send in the POST request.
        :param headers: Optional headers to include in the POST request.
        :param timeout: Optional timeout for the request in seconds.
        :return: The response text from the POST request.
        """
        try:
            response = self.requests.post(url, json=data, headers=headers, timeout=timeout)
            return response.text
        except Exception as e:
            print("POST request failed:", e)
            return None