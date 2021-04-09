from ipywidgets import Widget


class AreaSelectionInterface():
    def get_widget(self) -> Widget:
        """Returns main widget containing all other widgets to let user select an area"""
        pass

    def get_area(self) -> dict:
        """Returns dictionary defining a rectangle with keys: ['right', 'left', 'top', 'bottom']
            Values are integer coordinates. right/left ∈ [-180, 180]; top/bottom ∈ [-90, 90]
        """
        pass
