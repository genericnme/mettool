import ipywidgets as widgets
from IPython.core.display import display
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from os import path

from SingleDataset.AreaSelection import AreaSelection
from Timeseries.MultipleFilePicker import MultipleFilePicker
from Timeseries.TimeseriesController import TimeseriesController
from Timeseries.TimeseriesLevel import TimeseriesLevel
from SingleDataset.DebugCapturer import dbg
from Timeseries.TimeseriesModel import maxvars

class TimeseriesView:
    def __init__(self, root_dir: path = None):
        self.fp = MultipleFilePicker(root_dir)
        self.controller = TimeseriesController(self)
        self.areaSelection = AreaSelection()
        self.level_selection = TimeseriesLevel()
        self.__init_widgets()

    def __init_widgets(self):
        plot_btn = widgets.Button(description='Plot')
        plot_btn.on_click(self.on_plot_btn_click)
        plot_tab = widgets.HBox([plot_btn, self.controller.plot_out])

        self.var_select = widgets.SelectMultiple(options=self.controller.get_plottable_vars())
        self.var_select.observe(self.var_selection_change)


        options_tab = widgets.Accordion([self.areaSelection.get_widget(), self.var_select, self.level_selection.plevels_selection])
        options_tab.set_title(0, 'Areaselection')
        options_tab.set_title(1, 'Select variables')
        options_tab.set_title(2, 'Pressurelevel')

        self.main_tab = widgets.Tab([self.fp.get_widget(), options_tab, plot_tab, dbg])
        self.main_tab.set_title(0, 'Dset selection')
        self.main_tab.set_title(1, 'Areaselection')
        self.main_tab.set_title(2, 'Plot')
        self.main_tab.set_title(3, 'DeBuG output')

        self.main_tab.observe(self.main_tab_change)

    def show(self):
        display(self.main_tab)

    def on_plot_btn_click(self, b):
        self.controller.plot() #  self.areaSelection.getArea()

    def var_selection_change(self, change):
        if change['name'] == 'value' and change['type'] == 'change':
            if len(change['new']) > maxvars:
                print(f"Too many variables selected! (more than {maxvars})")

    def main_tab_change(self, change):
        if change['name'] == 'selected_index' and change['type'] == 'change':
            if change['new'] == 1:  # changed to areaselect
                self.areaSelection.show_again()