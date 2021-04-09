from ipywidgets import Output
from Timeseries.TimeseriesModel import TimeseriesModel
from SingleDataset.DebugCapturer import dbg

class TimeseriesController:
    def __init__(self, view):
        self.view = view
        self.model = TimeseriesModel()
        self.plot_out = Output()

    def get_plottable_vars(self):
        return [var for var in TimeseriesModel.all_variable_names if var not in ['a', 'b', 'p0', 'ps']]

    def plot(self):
        self.model.set_paths(self.view.fp.get_file_paths())
        vars = self.view.var_select.value
        with dbg:
            try:
                self.model.set_vars(vars)
            except Exception as e:
                print(e)

        area = self.view.areaSelection.get_area()
        with self.plot_out:
            self.model.plot_area_mean(area, self.view.level_selection.get_press_index(), self.view.level_selection.plevs, self.view.fp.get_file_dates())