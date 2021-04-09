from Timeseries.DatasetFile import DatasetFile


class DatasetFileFilter:

    def __init__(self, description: str = '', filtered_datasets=None):
        if filtered_datasets is None:
            filtered_datasets = []
        self.description = description
        self.filtered_datasets = filtered_datasets

    def get_name(self):
        return self.description

    def __str__(self):
        return self.description

    def get_datasets(self):
        return self.filtered_datasets
