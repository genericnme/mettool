from SingleDataset.DebugCapturer import dbg

import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, AutoDateFormatter, date2num
import datetime

from Timeseries.SDModelAdapter import SDModelAdapter

maxvars = 2


class TimeseriesModel:
    all_variable_names = ['a', 'b', 'p0', 'ps', 'GPH', 'TEMP', 'SH', 'OMEGA', 'PRESS', 'U', 'V', 'CLWC', 'CIWC',
                          'SIGMA',
                          'THETA_DOT_CSK', 'THETA_DOT_ASK', 'THETA_DOT_TOT', 'ZETA_DOT_TOT', 'THETA_DOT_TAS', 'THETA',
                          'ZETA',
                          'BVF', 'BVF_WET', 'TROP1', 'TROP2']

    def __init__(self):
        self.dsetpaths: list = []
        self.varnames = []

    def plot_area_mean(self, area, level, plevs, file_dates: list):
        """Creates plot for mean of added variables at the specified area and pressurelevel."""
        vars_to_drop = [var for var in TimeseriesModel.all_variable_names if var not in self.varnames + ['PRESS']]
        # print(self.dsetpaths)
        if len(self.dsetpaths) < 2:
            # raise Exception('Too few Datasets')
            with dbg:
                print("Too few Datasets (minimum is 2).")
            return
        if len(self.varnames) == 0:
            # raise Exception('No variable added')
            with dbg:
                print("No variables added.")
                return

        int_dates = []
        for date in file_dates:
            int_date = date2num(date)
            int_dates.append(int_date)

        averages = []

        for path in self.dsetpaths:
            tmp = SDModelAdapter()
            tmp.open_dset(path=path, dropvars=vars_to_drop)
            for var in self.varnames:
                tmp.add_var_to_plot(var)
            averages.append(tmp.get_mean(area=area, level=level, plevs=plevs))

        fig, ax1 = plt.subplots(num='')
        locator = AutoDateLocator()
        ax1.xaxis.set_major_locator(locator)
        ax1.xaxis.set_major_formatter(AutoDateFormatter(locator))
        plt.clf()
        #  Add labels etc etc
        if len(self.varnames) == 1:
            ax1.plot(int_dates, averages)
        elif len(self.varnames) == 2:
            ax1.plot([val[0] for val in averages])
            ax2 = ax1.twinx()
            ax2.plot([val[1] for val in averages])
        fig.autofmt_xdate()

    def set_vars(self, vars: list):
        self.varnames = []
        for varname in vars:
            if varname not in TimeseriesModel.all_variable_names:
                raise Exception(f'{varname} is not a viable variable name')
            if len(self.varnames) >= maxvars:
                raise Exception(f"Couldnt add {varname}. Maximum of {maxvars} variables already reached")
            self.varnames.append(varname)

    def set_paths(self, pathlist: list):
        self.dsetpaths = pathlist

#  tmp = Model()
#  tmp.open_dset(dropvars=vars_to_drop)  # Normally give path
#  units = []
#  for var in self.varnames:
#      tmp.add_var_to_plot(var)
#  for d_arr, conf in tmp.var_conf.values():
#      units.append(d_arr.units)
#  print(units)

#  dates = []

#  #        ax1.set_ylabel(units[0])

#  ax2.set_ylabel(units[0])
