import json
import time
from adafruit_jwt import JWT
from wifimanager import WiFiManager

class GoogleSheetsManager:
    '''
    A class to manage Google Sheets operations including creating an access token,
    writing to a Google Sheet, and reading from a Google Sheet.
    '''

    def __init__(self, wifi: WiFiManager, private_key: str, client_email: str, kid: str):
        '''
        Initializes the GoogleSheetsManager class.

        :param wifi: An instance of the WiFiManager class to handle the HTTP requests.
        :param private_key: The private key for the service account.
        :param client_email: The client email for the service account.
        :param kid: The key ID for the service account.
        '''
        self.wifi = wifi
        self.private_key = tuple(map(int, private_key.split(', ')))
        self.client_email = client_email
        self.kid = kid
        self.access_token = None
        self.exp = None

    def create_access_token(self) -> str:
        '''
        Creates an access token for Google Sheets API.

        :return: The access token as a string.
        '''
        iat = int(time.time())
        exp = iat + 3600
        payload = {
            'iss': self.client_email,
            'sub': self.client_email,
            'aud': 'https://sheets.googleapis.com/',
            'iat': iat,
            'exp': exp
        }
        additional_headers = {'kid': self.kid}

        jwt_token = JWT.generate(
            payload,
            self.private_key,
            headers=additional_headers,
            algo='RS256'
        )

        self.access_token = jwt_token
        self.exp = exp
        return self.access_token

    def write_to_sheet(
            self,
            spreadsheet_id: str,
            sheet_name: str,
            range_name: str,
            values: list,
            append: False
    ) -> None:
        '''
        Writes data to a Google Sheet.

        :param spreadsheet_id: The ID of the Google Sheet.
        :param sheet_name: The name of the sheet in the Google Sheet.
        :param range_name: The range in the sheet to write data to.
        :param values: The data to write to the sheet.
        :param append: A boolean value indicating whether to append the data to the end of the range.
        '''
        if not self.access_token or int(time.time()) >= self.exp:
            self.create_access_token()
        if append:
            url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}!{range_name}:append?valueInputOption=USER_ENTERED'
        else:
            url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}!{range_name}?valueInputOption=USER_ENTERED'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            'range': f'{sheet_name}!{range_name}',
            'majorDimension': 'ROWS',
            'values': values
        }

        response = self.wifi.post(url, data=data, headers=headers)

        if not response:
            raise Exception('Failed to write to sheet')
        else:
            return response

    def read_from_sheet(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        range_name: str
    ) -> list:
        '''
        Reads data from a Google Sheet.

        :param spreadsheet_id: The ID of the Google Sheet.
        :param sheet_name: The name of the sheet in the Google Sheet.
        :param range_name: The range in the sheet to read data from.
        :return: The data read from the sheet as a list.
        '''
        if not self.access_token or int(time.time()) >= self.exp:
            self.create_access_token()

        url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}!{range_name}'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        response = self.wifi.get(url, headers=headers)

        if response:
            return json.loads(response).get('values', [])
        else:
            raise Exception('Failed to read from sheet')
