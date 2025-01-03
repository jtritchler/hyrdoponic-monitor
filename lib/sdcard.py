import os
import storage
import adafruit_sdcard
import busio
import digitalio
import board

class SDCard:
    '''
    A class to manage file operations on an SD card using the adafruit_sdcard library.
    '''

    def __init__(self, spi, cs_pin, mount_point: str):
        '''
        Initializes the SDCard class.

        :param spi: The SPI bus.
        :param cs_pin: The chip select pin for the SD card.
        :param mount_point: The mount point of the SD card.
        '''
        self.spi = spi
        self.cs = digitalio.DigitalInOut(cs_pin)
        self.sdcard = adafruit_sdcard.SDCard(self.spi, self.cs)
        self.mount_point = mount_point
        self.vfs = storage.VfsFat(self.sdcard)
        storage.mount(self.vfs, self.mount_point)

    def file_exists(self, file_path: str) -> bool:
        '''
        Checks if a file exists on the SD card.

        :param file_path: The path to the file to check.
        :return: True if the file exists, False otherwise.
        '''
        full_path = f'{self.mount_point}/{file_path}'
        try:
            os.stat(full_path)
        except OSError:
            return False
        return True

    def read_file(self, file_path: str) -> str:
        '''
        Reads the contents of a file on the SD card.

        :param file_path: The path to the file to read.
        :return: The contents of the file as a string.
        :raises FileNotFoundError: If the file does not exist.
        '''
        full_path = f'{self.mount_point}/{file_path}'
        if not self.file_exists(file_path):
            raise OSError(f'File {full_path} does not exist.')
        with open(full_path, 'r') as file:
            return file.read()

    def write_file(self, file_path: str, data: str) -> None:
        '''
        Writes data to a file on the SD card.

        :param file_path: The path to the file to write.
        :param data: The data to write to the file.
        '''
        full_path = f'{self.mount_point}/{file_path}'
        with open(full_path, 'w') as file:
            file.write(data)

    def append_file(self, file_path: str, data: str) -> None:
        '''
        Appends data to a file on the SD card.

        :param file_path: The path to the file to append to.
        :param data: The data to append to the file.
        '''
        full_path = f'{self.mount_point}/{file_path}'
        with open(full_path, 'a') as file:
            file.write(data)
    
    def remove_file(self, file_path: str) -> None:
        """
        Removes a file from the SD card.

        :param file_path: The path to the file to remove.
        :raises FileNotFoundError: If the file does not exist.
        """
        full_path = f"{self.mount_point}/{file_path}"
        if self.file_exists(file_path):
            os.remove(full_path)

    def list_directory(self, dir_path: str) -> list:
        '''
        Lists the contents of a directory on the SD card.

        :param dir_path: The path to the directory to list.
        :return: A list of file and directory names in the specified directory and filesizes.
        :raises OSError: If the directory does not exist.
        '''
        full_path = f'{self.mount_point}/{dir_path}'
        try:
            contents = os.listdir(full_path)
        except OSError:
            raise OSError(f'Directory {dir_path} does not exist.')

        result = []
        for file in contents:
            file_path = f'{full_path}/{file}'
            try:
                stats = os.stat(file_path)
                filesize = stats[6]
                isdir = stats[0] & 0x4000

                if filesize < 1000:
                    sizestr = str(filesize) + ' bytes'
                elif filesize < 1000000:
                    sizestr = '%0.1f KB' % (filesize / 1000)
                else:
                    sizestr = '%0.1f MB' % (filesize / 1000000)

                prettyprintname = file
                if isdir:
                    prettyprintname = f'{file}/'

                result.append([prettyprintname, filesize])
            except OSError:
                result.append([file, 'Error reading file'])

        return result