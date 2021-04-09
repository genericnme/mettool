import ipywidgets as widgets
from metpy.units import units


class TimeseriesLevel:
    levels = ""
    plevs = []
    plevels_selection = widgets.Dropdown()

    def __init__(self):
        self.levels = "1000, 800, 900, 700, 600, 500, 400, 300, 200, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10"
        self.plevs = [float(i) for i in self.levels.split(sep=',')] * units.hPa
        self.plevs[::-1].sort()
        self.plevels_selection = widgets.Dropdown(
            description='Pressurelevel: ',
            disabled=False,
            options=self.plevs,
            value=self.plevs[4],
        )

    def get_plevs(self) -> list:
        """Returns list of pressure levels. Sorted and with unit"""
        return self.plevs;

    def get_press_index(self):
        """Get pressure niveau corresponding to the index in the DataArrays"""
        plevs_reversed = list(self.plevs)[::-1]
        return plevs_reversed.index(self.plevels_selection.value)
