from metpy.interpolate import cross_section
from metpy.interpolate import log_interpolate_1d
import matplotlib.pyplot as plt
from cartopy.util import add_cyclic_point
import cartopy.crs as ccrs
import numpy as np
import xarray as xr
from SingleDataset.DebugCapturer import dbg

class SDModel:
    plottypes = ['Cross Section', 'Horizontal']
    def __init__(self):
        self.data = None
        self.__press_inter = None
        self.var_conf = dict()  # Maps Variable name to  tuple of DataArray and Plotconfiguration

    def get_all_var_names(self):
        if self.dataset_opened():
            return list(self.data.data_vars)
        else:
            return ['No Dataset opened']

    def get_plotvar_names(self):
        return self.var_conf.keys()

    def get_mean(self, area, plevs, level):
        self.slice_to_area(area)
        self.interpolate(plevs)
        means = []
        for name, (d_arr, conf) in self.var_conf.items():
            means.append(np.nanmean(d_arr[level]))
        self.reset_data_vars()
        return tuple(means)

    def dataset_opened(self) -> bool:
        return self.data is not None

    @dbg.capture()
    def open_dset(self, path='./data/era5_19120612.nc', dropvars=[]):
        self.data = xr.open_dataset(path,
                                    group=None,
                                    drop_variables=dropvars).squeeze()  # Squeeze notwendig für Interpolation (streicht time als dimension)
        #self.data = self.data.metpy.parse_cf()  # Wird u.a. benötigt, um cross_section() nutzen zu können
        self.__press_inter = self.data['PRESS']

    def add_var_to_plot(self, varname, pltconf=None):  #  Changed to standardvalue None___
        self.var_conf[varname] = (self.data[varname], pltconf)

    def remove_var(self, varname):
        if varname in self.var_conf.keys():
            self.var_conf.pop(varname)

    def reset_data_vars(self):
        self.__press_inter = self.data['PRESS']
        for name in self.var_conf.keys():
            self.var_conf[name] = (self.data[name], self.var_conf[name][1])

    @dbg.capture()
    def add_cyclic_points(self) -> None:
        press_cyc, lons = add_cyclic_point(self.__press_inter, np.array(self.__press_inter['lon'].values, dtype=int))
        d_arr = xr.DataArray(data=press_cyc,
                             dims=['hybrid', 'lat', 'lon'],
                             coords={'hybrid': ('hybrid', self.__press_inter['hybrid']),
                                     'lat': ('lat', self.__press_inter['lat']),
                                     'lon': ('lon', lons)},
                             attrs=self.__press_inter.attrs)
        d_set = xr.Dataset({'PRESS': d_arr},
                           coords={'hybrid': ('hybrid', d_arr['hybrid']),
                                   'lat': ('lat', d_arr['lat']),
                                   'lon': ('lon', lons)},
                           )
        self.__press_inter = d_set.metpy.parse_cf(varname='PRESS')
        for name, (d_arr, conf) in list(self.var_conf.items()):
            d_arr_cyc, lons = add_cyclic_point(d_arr.values, np.array(d_arr['lon'].values, dtype=int))
            d_arr = xr.DataArray(data=d_arr_cyc,
                                 dims=['hybrid', 'lat', 'lon'],
                                 coords={'hybrid': ('hybrid', d_arr['hybrid']),
                                         'lat': ('lat', d_arr['lat']),
                                         'lon': ('lon', lons)},
                                 attrs=d_arr.attrs)
            d_set = xr.Dataset({name: d_arr},
                               coords={'hybrid': ('hybrid', d_arr['hybrid']),
                                       'lat': ('lat', d_arr['lat']),
                                       'lon': ('lon', lons)},
                               )
            d_arr = d_set.metpy.parse_cf(varname=name)
            self.var_conf[name] = (d_arr, conf)

    @dbg.capture()
    def interpolate_csec(self, plevs, start, end, steps=100):
        start = (start['lat'], start['lon'])
        end = (end['lat'], end['lon'])
        xp_interp = cross_section(self.__press_inter, start, end, steps=steps)
        for name, (d_arr, conf) in list(self.var_conf.items()):
            d_arr = cross_section(d_arr, start, end, steps=steps)
            d_arr_interp = log_interpolate_1d(plevs, xp_interp, d_arr)
            # Back to DataArray:
            d_arr_interp = xr.DataArray(data=d_arr_interp,
                                        dims=['plevs', 'index'],
                                        coords={'lat': ('index', d_arr['lat']),
                                                'lon': ('index', d_arr['lon']),
                                                'plevs': ('plevs', plevs),
                                                'index': ('index', d_arr['index'])},
                                        attrs=d_arr.attrs)  # Anpassen, nicht identisch
            # Change dict entry for interpolated values
            self.var_conf[name] = (d_arr_interp, conf)

    @dbg.capture()
    def interpolate(self, plevs):
        for name, (d_arr, conf) in list(self.var_conf.items()):
            d_arr_interp = log_interpolate_1d(plevs, self.__press_inter, d_arr)
            # Back to DataArray:
            d_arr_interp = xr.DataArray(data=d_arr_interp,
                                        dims=['plevs', 'lat', 'lon'],
                                        coords={'plevs': ('plevs', plevs),
                                                'lat': ('lat', d_arr['lat']),
                                                'lon': ('lon', d_arr['lon'])},
                                        attrs=d_arr.attrs)
            # Change dict entry for interpolated values
            self.var_conf[name] = (d_arr_interp, conf)

    def slice_to_area(self, area) -> None:
        """ Slices data to the given area.
        Slicing the data is necessary to calculate zonal means
        and makes other operations such as interpolating faster.
        :param area: Dictionary defining a rectangle. Keys: ['right', 'left', 'top', 'bottom'], Values: Integer
        :return: None
        """

        #  We have to get the indices corresponding to the area (/user input)
        if area['left'] < 0 and area['right'] >= 0:
            lonslice = list(range(0, area['right']+1)) + list(range(area['left'] + 360, 361))
        elif area['left'] < 0 and area['right'] < 0:
            lonslice = slice(area['left']+360, area['right'] + 361)
        else:
            lonslice = slice(area['left'], area['right'] + 1)

        lon_start = 180 - (area['top'] + 90)
        lon_end = 180 - (area['bottom'] + 90)
        latslice = slice(lon_start, lon_end + 1)

        self.__press_inter = self.__press_inter.isel({'lat': latslice, 'lon': lonslice})
        for name, (d_arr, conf) in list(self.var_conf.items()):
            d_arr_sliced = d_arr.isel({'lat': latslice, 'lon': lonslice})
            self.var_conf[name] = (d_arr_sliced, conf)

    def do_horizontal_plot(self, pressurelevels, level, area=None, fig='Plot'):
        if area['left'] < 0 and area['right'] >= 0:
            self.add_cyclic_points()
        self.slice_to_area(area)
        self.interpolate(pressurelevels)
        fig = plt.figure(num=fig)
        plt.clf()
        ax = plt.axes(projection=ccrs.PlateCarree()) if len(fig.axes) == 0 else fig.axes[0]
        if area is not None:
            #ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
            ax.set_extent([area['left'], area['right'], area['bottom'], area['top']], crs=ccrs.PlateCarree())
        for d_arr, conf in self.var_conf.values():
            if conf.fill:
                cf = ax.contourf(d_arr['lon'], d_arr['lat'], d_arr[level[0]], conf.grades, cmap=conf.cmap,
                                 transform=ccrs.PlateCarree())
                cb = fig.colorbar(cf, orientation='horizontal')
                cb.set_label(d_arr.units, size='x-large')
            else:
                ax.contour(d_arr['lon'], d_arr['lat'], d_arr[level[0]], conf.grades, cmap=conf.cmap,
                           transform=ccrs.PlateCarree())
        ax.set_title(f"{list(self.var_conf.keys())} at {level[1]}")
        ax.coastlines()
        ax.gridlines()
        plt.draw()

    def do_csec_plot(self, pressurelevels, start, end, x_ax_var='index', steps=100, fig='Plot'):
        self.add_cyclic_points()
        self.interpolate_csec(pressurelevels, start, end, steps=steps)
        # x_ax_var = 'lon' if (abs(start['lon'] - end['lon']) > abs(start['lat'] - end['lat'])) else 'lat'  # Determines xaxis variable. (Let User decide?) lon/lat or index is possible
        fig = plt.figure(num=fig)
        plt.clf()
        ax = plt.axes() if len(fig.axes) == 0 else fig.axes[0]  # create or reuse axis
        for d_arr, conf in self.var_conf.values():
            if conf.fill:
                cf = ax.contourf(d_arr[x_ax_var], pressurelevels, d_arr, conf.grades, cmap=conf.cmap)
                cb = fig.colorbar(cf, orientation='horizontal')
                cb.set_label(d_arr.units, size='x-large')
            else:
                ax.contour(d_arr[x_ax_var], pressurelevels, d_arr, conf.grades, cmap=conf.cmap)
        # ax.set_xlim(start[x_ax_var], end[x_ax_var])
        ax.set_yscale('symlog')
        ax.set_ylim(pressurelevels.max(), pressurelevels.min())
        ax.set_ylabel('Pressure (hPa)')
        ax.set_xlabel(x_ax_var)
        ax.set_yticks(np.arange(1000, 10, -100))  # Wie anpassen?
        ax.set_yticklabels(np.arange(1000, 10, -100))
        ax.set_title(
            f"Cross Section of {list(self.var_conf.keys())} from {(start['lat'], start['lon'])} to {(end['lat'], end['lon'])}")
        plt.draw()
