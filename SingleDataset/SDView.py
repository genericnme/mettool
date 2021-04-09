import ipywidgets as widgets
from IPython.core.display import display
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from SingleDataset.SDController import SDController
from SingleDataset.DebugCapturer import dbg
from SingleDataset.SingleFilePicker import SingleFilePicker
from SingleDataset.AreaSelection import AreaSelection

class SDView:
    def __init__(self):
        self.controller = SDController(self)
        self.filePicker = SingleFilePicker()
        self.areaSelection = AreaSelection()
        self.__init_outputs()
        self.__initial_plottype = self.controller.get_plottypes()[0]
        self.__init_widgets()
        # self.__plottype_change({'name': 'value', 'type': 'change', 'new': self.__initial_plottype})
        self.__init_handler()

    def show(self):
        display(self.toolbox)

    def update_viable_vars(self, options):
        self.__var_selection.options = options
        self.__add_btn.disabled = False

    def update_added_vars(self):
        self.__added_vars.children = self.controller.get_added_var_wid()
        varnames = self.controller.get_added_var_names()
        [self.__added_vars.set_title(i, name) for i, name in enumerate(varnames)]

    def update_plev_options(self):
        self.__hplot_level_selection.options = self.controller.get_plevs()

    def __init_widgets(self):
        self.__plottype_selection = widgets.Dropdown(options=self.controller.get_plottypes(),
                                                     value=self.__initial_plottype,
                                                     description='Type of plot')

        plevels_selection = widgets.interactive(self.controller.set_plevs,
                                                levels=widgets.Textarea(
                                                value="1000, 800, 900, 700, 600, 500, 400, 300, 200, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10"))
        general_options = widgets.HBox([self.__plottype_selection, plevels_selection])
        self.__var_selection = widgets.Select(description='Select Variable:', options=['No Dataset opened'])
        self.__added_vars = widgets.Accordion([], layout=widgets.Layout(width='425px'))
        self.__add_btn = widgets.Button(description="Add Variable", disabled=True)
        var_configuration = widgets.HBox([self.__var_selection, self.__add_btn, self.__added_vars])

        self.__hplot_level_selection = widgets.Dropdown(description='Pressurelevel: ')
        #hplot_configurations = widgets.HBox([hplot_area_selection, self.__hplot_level_selection])
        #hplot_all = widgets.VBox([hplot_configurations, self.areaselection_out])
        hplot_all = self.areaSelection.get_widget()

        csec_xvar = widgets.interactive(self.controller.set_csec_xvar, x_ax_var=['index', 'lat', 'lon'])
        csec_stepnum = widgets.interactive(self.controller.set_csec_steps, steps=(50, 300, 50))
        csec_all = widgets.VBox([csec_xvar, csec_stepnum, self.pointselection_out])

        nonspecific_options = [general_options, var_configuration]
        self.__pointsel_options = nonspecific_options + [csec_all]
        self.__areasel_options = nonspecific_options + [hplot_all]

        self.__options = widgets.Accordion(children=nonspecific_options)  # + [self.__initial_plottype])
        self.__options.set_title(0, 'Type of plot')
        self.__options.set_title(1, 'Variables to plot')

        self.__plot_btn = widgets.Button(description="Plot")
        plot = widgets.VBox([self.__plot_btn, self.plot_output])

        self.toolbox = widgets.Tab(children=[self.filePicker.get_widget(), self.__options, plot, dbg])
        self.toolbox.set_title(0, 'Dataset Selection')
        self.toolbox.set_title(1, 'Options')
        self.toolbox.set_title(2, 'Plot')
        self.toolbox.set_title(3, 'Debug Output')

    def __init_handler(self):
        self.__plottype_selection.observe(self.__plottype_change, 'value')
        self.__add_btn.on_click(self.__add_btn_click)
        self.__plot_btn.on_click(self.__plot_btn_click)
        self.__hplot_level_selection.observe(self.__hplot_level_change)
        self.toolbox.observe(self.__tab_change)

    def __init_outputs(self):
        # self.dbg = widgets.Output()
        self.plot_output = widgets.Output()
        self.pointselection_out = widgets.Output()
        #self.areaselection_out = widgets.Output()

    def __show_pointselection(self):
        with self.pointselection_out:
            # self.controller.plot(plottype=self.plottypes[1])
            fig = plt.figure(num='Pointselection')
            if len(fig.axes) == 0:
                fig.add_subplot(label='map', projection=ccrs.PlateCarree()).stock_img()
                ax1 = fig.axes[0]
                ax2 = fig.add_subplot(label='crosses', projection=ccrs.PlateCarree(), sharex=ax1, sharey=ax1, zorder=2)
                ax2.patch.set_facecolor('none')
                fig.canvas.mpl_connect('button_press_event', self.controller.on_click_on_map)
            plt.draw()

    def __add_btn_click(self, b):
        self.controller.add_var(self.__var_selection.value)
        self.update_added_vars()

    def __plot_btn_click(self, b):
        with self.plot_output:
            try:
                self.controller.plot(plottype=self.__plottype_selection.value)
            except Exception as e:
                #self.plot_output.clear_output()
                print(e)

    def __tab_change(self, change):
        if change['name'] == 'selected_index' and change['type'] == 'change':
            if change['new'] == 1: #  changed to options
                path = self.filePicker.get_file_paths()[0]
                if path is not None:
                    self.controller.open_dset(path)

    def __hplot_level_change(self, change):
        if change['name'] == 'value' and change['type'] == 'change':
            self.controller.set_hplot_plev(self.__hplot_level_selection.value)

    def __plottype_change(self, change):
        if change['name'] == 'value' and change['type'] == 'change':
            if change['new'] == self.controller.get_plottypes()[0]:
                plt.close('Areaselection')
                self.__options.children = self.__pointsel_options
                self.__show_pointselection()
                self.__options.set_title(2, f"{self.controller.get_plottypes()[0]} Options")
            if change['new'] == self.controller.get_plottypes()[1]:
                plt.close('Pointselection')
                self.__options.children = self.__areasel_options
                self.areaSelection.show_again()
                self.__options.set_title(2, f"{self.controller.get_plottypes()[1]} Options")
