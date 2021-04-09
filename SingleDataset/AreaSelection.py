import ipywidgets as widgets
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.patches import Rectangle as RectanglePatch
from Interfaces.AreaSelectionInterface import AreaSelectionInterface

class AreaSelection(AreaSelectionInterface):
    def __init__(self):
        self.map_out = widgets.Output()
        self.bottom_lat = widgets.BoundedIntText(min=-90, max=90, description='Bottom Lat:')
        self.top_lat = widgets.BoundedIntText(min=-90, max=90, value=10, description='Top Lat:')
        self.left_lon = widgets.BoundedIntText(min=-180, max=180, description='Left Lon:')
        self.right_lon = widgets.BoundedIntText(min=-180, max=180, value=10, description='Right Lon:')
        self.update_area_minmax()
        hplot_area_selection = widgets.VBox([self.bottom_lat, self.left_lon, self.top_lat, self.right_lon])
        area_on_map_out = widgets.interactive_output(self.show_area,
                                                     {'left': self.left_lon,
                                                      'bottom': self.bottom_lat,
                                                      'top': self.top_lat,
                                                      'right': self.right_lon})
        self.main_vbox = widgets.VBox([hplot_area_selection, self.map_out])

    def get_widget(self) -> widgets.VBox:
        return self.main_vbox

    def get_area(self) -> dict:
        return {'left': self.left_lon.value,
                'bottom': self.bottom_lat.value,
                'top': self.top_lat.value,
                'right': self.right_lon.value}

    def update_area_minmax(self):
        mindiff = 10
        self.bottom_lat.max = self.top_lat.value - mindiff
        self.top_lat.min = self.bottom_lat.value + mindiff
        self.left_lon.max = self.right_lon.value - mindiff
        self.right_lon.min = self.left_lon.value + mindiff

    def show_again(self):
        """After 'Parentwidget' is reshown, this has to be called in order to show the MPL figure again"""
        with self.map_out:
            fig = plt.figure('Areaselection')
        if len(fig.axes) == 0:
            fig.add_subplot(projection=ccrs.PlateCarree()).stock_img()  # First axis is static background, should only be plotted once
            ax1 = fig.axes[0]
            ax2 = fig.add_subplot(projection=ccrs.PlateCarree(), label='rectangle', sharex=ax1, sharey=ax1)
            ax2.patch.set_facecolor('none')  # Make background for second axis transparent
        self.show_area(left=self.left_lon.value,
                       bottom=self.bottom_lat.value,
                       top=self.top_lat.value,
                       right=self.right_lon.value)

    def show_area(self, left, bottom, right, top):
        self.update_area_minmax()
        fig = plt.figure(num='Areaselection')
        ax = fig.get_axes()[1]
        ax.cla()
        ax.patch.set_facecolor('none')
        rect = RectanglePatch([left, bottom], right - left, top - bottom)
        ax.add_patch(rect)
        plt.draw()