from Interfaces.FilePickerInterface import FilePickerInterface
from ipyfilechooser import FileChooser
from pathlib import Path

class SingleFilePicker(FilePickerInterface):
    def __init__(self):
        self.filename = None
        def file_change(chooser):
            chooser.title = '<b>Selected file</b>'
            self.filename = chooser.selected
        self.fc = FileChooser(str(Path.home()))
        self.fc.show_hidden = False
        self.fc.use_dir_icons = True
        self.fc.filter_pattern = "*.nc";
        self.fc.title = '<b>Select NetCDF Dataset</b>'
        self.fc.register_callback(file_change)
        #self.fc.reset(path='..', filename='era5_19120612.nc')

    def get_file_paths(self) -> list:
        return [self.filename]

    def get_widget(self) -> FileChooser:
        return self.fc