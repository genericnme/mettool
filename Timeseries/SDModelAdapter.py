from SingleDataset.SDModel import SDModel

class SDModelAdapter():
    """Adapter for SDModel, providing necessary methods for TimeseriesModel."""
    def __init__(self):
        self.sdmodel = SDModel()

    def open_dset(self, path, dropvars):
        self.sdmodel.open_dset(path, dropvars)

    def add_var_to_plot(self, varname):
        self.sdmodel.add_var_to_plot(varname)

    def get_mean(self, area, plevs, level):
        return self.sdmodel.get_mean(area, plevs, level)