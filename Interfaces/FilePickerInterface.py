from ipywidgets import Widget


class FilePickerInterface:
    def get_widget(self) -> Widget:
        """Returns main widget containing all other widgets to let user pick desired files"""
        pass

    def get_file_paths(self) -> list:
        """Get list of selected paths"""
        pass
