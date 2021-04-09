import ipywidgets as widgets
from Interfaces.FilePickerInterface import FilePickerInterface

class DummyFp(FilePickerInterface):
    """ Dummy FilePicker without functionality """
    def __init__(self):
        self.dummyWidget = widgets.HBox(layout=widgets.Layout(width='300px', height='300px'))
        self.filenames = ['./data/era5_19120612.nc']

    def get_widget(self) -> widgets.HBox:
        return self.dummyWidget

    def get_file_paths(self) -> list:
        return self.filenames