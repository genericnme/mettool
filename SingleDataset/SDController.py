import ipywidgets as widgets
from metpy.units import units
import matplotlib.pyplot as plt
import matplotlib.patches as mplpatches

from SingleDataset.DebugCapturer import dbg
from SingleDataset import Plotconfiguration as pconf
from SingleDataset.SDModel import SDModel

class SDController:
    def __init__(self, view):
        self.view = view
        self.model = SDModel()
        #self.model = Timeseries_model()
        self.plevs = []  # list of Pressureniveaus to interpolate to. Important: These are sorted Values with units

        # csec-specific parameters:
        self.start_end_cords = []  # will contain start and endpoint as to dicts with 'lat' and 'lon' as keys
        self.x_ax_var = 'index'
        self.csec_steps = 100
        # hplot-specific parameters:
        # self.area = None  # {'left': 0, 'right': 10, 'top': 10, 'bottom': 0}
        self.hplot_level = (0, 0)  # (index, Value)
        self.configs = dict()

    def get_all_var_names(self):
        return [ele for ele in list(self.model.get_all_var_names()) if
                ele not in ['a', 'b', 'p0', 'ps']]

    def get_added_var_wid(self):
        return list(self.configs.values())

    def get_added_var_names(self):
        return list(self.configs.keys())

    def get_plevs(self):
        return self.plevs

    def get_plottypes(self):
        return SDModel.plottypes

    def set_plevs(self, levels):
        try:
            plevs = [float(i) for i in levels.split(sep=',')] * units.hPa
        except Exception as e:
            print(e)
            return
        plevs[::-1].sort()
        self.plevs = plevs
        self.view.update_plev_options()

    def set_hplot_plev(self, level):
        if level is not None:
            self.hplot_level = (list(self.get_plevs())[::-1].index(level), level)

    def set_csec_xvar(self, x_ax_var):
        self.x_ax_var = x_ax_var

    def set_csec_steps(self, steps):
        self.csec_steps = steps

    def open_dset(self, path):
        if not self.model.dataset_opened():
            self.model.open_dset(path)
            self.view.update_viable_vars(self.get_all_var_names())

    def add_var(self, varname):
        pc = pconf.Plotconfiguration()
        self.model.add_var_to_plot(varname, pc)
        self.configs[varname] = self.__create_varconf_wid(pc, varname)

    def remove_var(self, varname):
        self.model.remove_var(varname)

    def plot(self, plottype):
        if not self.model.dataset_opened():
            raise Exception('No Dataset opened')
        elif len(self.model.get_plotvar_names()) == 0:
            raise Exception('No variables added to plot')
        if plottype == SDModel.plottypes[1]:
            self.model.do_horizontal_plot(self.plevs, self.hplot_level, area=self.view.areaSelection.get_area())
        elif plottype == SDModel.plottypes[0]:
            if len(self.start_end_cords) != 2:
                raise Exception('Start-/Endpoint not selected')
            self.model.do_csec_plot(self.plevs, self.start_end_cords[0], self.start_end_cords[1],
                                    x_ax_var=self.x_ax_var, steps=self.csec_steps)
        self.model.reset_data_vars()

    def on_click_on_map(self, event):
        try:
            self.start_end_cords.append({'lon': round(event.xdata), 'lat': round(event.ydata)})
        except TypeError:  # Click outside of map results in NoneType for xdata/ydata
            return
        if len(self.start_end_cords) > 2:  # In future custom path may be added
            self.start_end_cords.clear()
        fig = plt.figure(num='Pointselection')
        ax = fig.get_axes()[1]
        ax.cla()
        ax.patch.set_facecolor('none')
        # plt.gca().stock_img()
        for mrk, text in zip(self.start_end_cords, ['Start', 'End']):
            ax.plot(mrk['lon'], mrk['lat'], '+-r', ms=25, zorder=2)
            ax.annotate(text, xy=(mrk['lon'] - 10, mrk['lat'] - 18))

    # Dynamically create Widgets to configure options for variables individually
    def __create_varconf_wid(self, pc, varname):
        cmap = widgets.interactive(pc.set_cmap, cmap=plt.colormaps())
        grades = widgets.interactive(pc.set_grades, grades=(5, 20))
        fill = widgets.interactive(pc.set_fill, fill=True)
        remove_btn = widgets.Button(description='Remove')
        remove_btn.on_click(self.__get_remove_btn_handler(varname))
        return widgets.VBox([cmap, grades, fill, remove_btn])

    def __get_remove_btn_handler(self, varname):
        def f(b):
            self.configs.pop(varname)
            self.view.update_added_vars()

        return f
