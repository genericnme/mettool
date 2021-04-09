from datetime import datetime
from pandas import Timestamp
from os import path
from typing import List

file_prefix = 'ecmwf_era5_'
file_suffix = '.nc'


class DatasetFile:

    def __init__(self, root_dir: path = '', param=None):
        self.root: path = root_dir
        if isinstance(param, Timestamp):
            date: Timestamp = param
            self.date: datetime = date.to_pydatetime()
            self.filename: str = self.date_to_filename(date=date)
            self.filepath: path = self.date_to_filepath(date=date)
        elif isinstance(param, path):
            filepath: path = param
            self.filename = self.path_to_filename(filepath=filepath)
            self.date = self.path_to_date(filepath=filepath)
            self.filepath = filepath
        else:
            self.date = None
            self.filepath = None
            self.filename = None
            # TODO -> print statement as debug
            print(str(param) + ' is not of type ' + str(type(datetime)) + ' or ' + str(type(path)))
        self.display_formats: List[str] = ['filename', 'date', 'path']
        self.display_format = self.display_formats[0]

    def set_display_format(self, display_format: str):
        """Sets display format of string representation. Formats are: 'filename', 'date' and 'path'"""
        display_format = display_format.lower()
        if display_format in self.display_formats:
            self.display_format = display_format

    def date_to_filename(self, date: datetime) -> str:
        """Converts a date into a filename"""
        year = f"{date.year % 100:02d}"
        month = f"{date.month:02d}"
        return file_prefix + year + month + f"{date.day:02d}" + f"{date.hour:02d}" + file_suffix

    def path_to_date(self, filepath: path) -> datetime:
        """Converts a path into a date"""
        filename = self.path_to_filename(filepath)
        if filename.startswith(file_prefix) and filename.endswith(file_suffix):  # check if filename syntax is correct
            filename = filename[len(file_prefix):-len(file_suffix)]

            # day and hour from filename
            # month = int(filename[2:4])
            day = int(filename[4:6])
            hour = int(filename[6:8])

            # month and year from path to file
            # split path to file into directories
            directories = []
            while 1:
                filename, directory_name = path.split(filepath)

                if directory_name != "":
                    directories.append(directory_name)
                elif path != "":
                    directories.append(filename)
                    break

            # obtain by directory_name length
            year = None
            month = None
            for directory_name in directories:
                # print(directory_name)
                if month is None and len(directory_name) == 2:
                    try:
                        month = int(directory_name)
                    except ValueError:
                        pass
                elif year is None and len(directory_name) == 4:
                    try:
                        year = int(directory_name)
                    except ValueError:
                        pass
                elif year is not None and month is not None:
                    return datetime(year=year, month=month, day=day, hour=hour)

            # obtain by two directories previous to filename
            # try:
            #     month = int(directories[0])
            #     year = int(directories[1])
            # except ValueError:
            #     pass  # ignore and raise SyntaxError

        raise SyntaxError("Syntax of '" + filename + "' is incorrect")

    def get_date(self) -> datetime:
        return self.date

    def get_year(self) -> int:
        return self.date.year

    def get_month(self) -> int:
        return self.date.month

    def get_day(self) -> int:
        return self.date.day

    def get_hour(self) -> int:
        return self.date.hour

    def path_to_filename(self, filepath: path) -> str:
        """Returns filename (tail) from path"""
        head, tail = path.split(filepath)
        return tail or path.basename(head)

    def date_to_filepath(self, date: datetime) -> path:
        """Converts date to path"""
        filename = self.date_to_filename(date=date)
        year = f"{date.year:04d}"
        month = f"{date.month:02d}"
        return path.join(self.root, year, month, filename)

    def get_filename(self) -> str:
        return self.filename

    def get_filepath(self) -> path:
        return self.filepath

    def exists(self) -> bool:
        """Checks if DatasetFile exists"""
        return path.isfile(self.get_filepath())

    def __str__(self):
        if self.display_format == self.display_formats[1]:
            return str(self.get_date())
        elif self.display_format == self.display_formats[2]:
            return self.get_filepath()
        else:
            return self.get_filename()
