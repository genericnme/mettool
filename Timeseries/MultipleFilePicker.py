import re
from pathlib import Path

import ipywidgets as widgets
from IPython.display import HTML, display
from datetime import time, datetime
from os import path
import pandas as pd
from typing import List

from Interfaces.FilePickerInterface import FilePickerInterface
from Timeseries.DatasetFile import DatasetFile
from Timeseries.DatasetFileFilter import DatasetFileFilter

style = {'description_width': 'initial'}


class MultipleFilePicker(FilePickerInterface):

    def __init__(self, root_dir: path = None):
        self.root_dir: path = root_dir
        if self.root_dir is None:
            self.root_dir = path.join(path.sep, 'p', 'fastdata', 'slmet', 'slmet111', 'met_data', 'ecmwf', 'era5', 'nc')

        # filers and filter (multiple selection widget)
        self.dataset_files_selection: widgets.SelectMultiple = widgets.SelectMultiple()
        self.filter_selection: widgets.SelectMultiple = widgets.SelectMultiple()
        self.filter_specification_box: FilterBox = FilterBox()
        self.filter_specification: widgets.Box = widgets.Box([])

        self.datasets: List[DatasetFile] = []
        self.dataset_filters: List[DatasetFileFilter] = []

        self.recently_removed_datasets: List[List[DatasetFile]] = [[]]

        self.datebox_main: DateSelector = DateSelector()

        button_collect: widgets.Button = widgets.Button(description='Collect Datasets',
                                                        disabled=False,
                                                        button_style='success',
                                                        # 'success', 'info', 'warning', 'danger' or ''
                                                        tooltip='Collects datasets within the given time interval',
                                                        # icon='fa-bomb',
                                                        style=style
                                                        )

        def button_collect_clicked(collect_button: widgets.Button):
            self.datasets = []
            # check if dates are valid
            if self.datebox_main.evaluate_dates():
                # collect available datasets from specified start and end datetime objects
                if self.collect_datasets(date_start=self.datebox_main.get_start_date(),
                                         date_end=self.datebox_main.get_end_date()):
                    # if any datasets were found, initialize further widgets for filtering of selected files
                    self.init_dataset_specification()
                else:
                    notify(
                        'No datasets were found from ' + str(self.datebox_main.get_start_date()) + ' to ' + str(
                            self.datebox_main.get_end_date()))

        button_collect.on_click(button_collect_clicked)

        self.date_selection_box: widgets.VBox = widgets.VBox([self.datebox_main, button_collect],
                                                             layout=widgets.Layout(display='flex',
                                                                                   flex_flow='row wrap',
                                                                                   justify_content='space-around',
                                                                                   align_items='center'
                                                                                   )
                                                             )
        self.dataset_specification_box: widgets.Box = widgets.Box()

        self.main_component: widgets.Accordion = widgets.Accordion(children=[self.date_selection_box])
        self.main_component.set_title(0, 'Selection Interval')
        self.main_component.selected_index = 0

    def collect_datasets(self, date_start: datetime, date_end: datetime) -> bool:
        """Checks for available datasets between start and end datetime objects and adds them to dataset list ('self.datasets').
        Returns: True if datasets were found, False otherwise"""
        # print('Collecting datasets between ' + str(date_start) + " and " + str(date_end))

        dates_between: pd.DatetimeIndex = pd.date_range(date_start, date_end, freq='h')
        for date_elem in dates_between:
            dataset_file: DatasetFile = DatasetFile(root_dir=self.root_dir, param=date_elem)
            # print(dataset_file)

            if dataset_file.exists():
                self.datasets.append(dataset_file)
            # else:
            #     print("File '" + path.join(self.root_dir, dataset_file.get_filepath()) + "' does not exist")
        return bool(self.datasets)  # return whether name-path map is empty

    def init_dataset_specification(self):
        """initialize widgets for display and filtering of selected files (filtering)"""
        display_formats = ['Filename', 'Date', 'Path']

        # datasets
        self.dataset_files_selection = widgets.SelectMultiple(
            options=[],
            description='Time Series Datasets:',
            disabled=False,
            style=style,
            layout=widgets.Layout(width='auto')
        )
        self.update_selected_dataset_files()

        # display format
        dataset_display_format: widgets.ToggleButtons = widgets.ToggleButtons(
            options=display_formats,
            selected=display_formats[0],
            description='Display:',
            disabled=False,
            button_style='',  # 'success', 'info', 'warning', 'danger' or ''
            tooltips=['display filename', 'display date', 'display path'],
            style=style
        )

        def dataset_format_change(change):
            """Sets display format of dataset files"""
            display_format = change['new']
            # print(display_format)
            for dataset in self.datasets:
                dataset.set_display_format(display_format)
            self.update_selected_dataset_files()

        dataset_display_format.observe(dataset_format_change, names=['value'])

        undo_button: widgets.Button = widgets.Button(description='Undo',
                                                     disabled=False,
                                                     button_style='info',
                                                     # 'success', 'info', 'warning', 'danger' or ''
                                                     tooltip='Undo recent dataset changes',
                                                     # icon='fa-smile-o',
                                                     style=style
                                                     )

        def undo_button_clicked(button_undo: widgets.Button):
            """Populates datasets with recently removed sets. (Manually removed datasets only. Filters are treated separately.)"""
            # print('undoing recent changes')
            if self.recently_removed_datasets:
                recently_removed: list = self.recently_removed_datasets.pop()
                self.datasets.extend(recently_removed)
                self.update_selected_dataset_files()

        undo_button.on_click(undo_button_clicked)

        remove_selected_files_button: widgets.Button = widgets.Button(description='Remove selected',
                                                                      disabled=False,
                                                                      button_style='warning',
                                                                      # 'success', 'info', 'warning', 'danger' or ''
                                                                      tooltip='Remove selected datasets',
                                                                      # icon='fa-bomb',
                                                                      style=style
                                                                      )

        def remove_selected_files_button_clicked(button_remove: widgets.Button):
            self.remove_datasets(datasets_to_remove=self.dataset_files_selection.value)

        remove_selected_files_button.on_click(remove_selected_files_button_clicked)

        dataset_buttons_box: widgets.VBox = widgets.VBox([undo_button, remove_selected_files_button])

        dataset_selection_box: widgets.HBox = widgets.HBox([self.dataset_files_selection, dataset_buttons_box])

        dataset_box: widgets.VBox = widgets.VBox([dataset_display_format, dataset_selection_box])

        # filter

        self.filter_selection = widgets.SelectMultiple(
            options=[],
            description='Filters:',
            disabled=False,
            style=style,
            layout=widgets.Layout(width='auto')
        )

        create_filter_button: widgets.Button = widgets.Button(description='Create filter',
                                                              disabled=False,
                                                              button_style='info',
                                                              # 'success', 'info', 'warning', 'danger' or ''
                                                              tooltip='Create filter for selected datasets',
                                                              # icon='fa-filter',
                                                              style=style
                                                              )

        def create_filter_button_clicked(button_create: widgets.Button):
            if len(self.filter_specification.children) == 0:
                filter_options: list = ['Frequency', 'Interval', 'Regular expression']
                filter_options_dropdown: widgets.Dropdown = widgets.Dropdown(
                    options=filter_options,
                    value=filter_options[0],
                    description='Filter options:',
                    disabled=False,
                    style=style
                )

                apply_filter_button: widgets.Button = widgets.Button(description='Apply filter',
                                                                     disabled=False,
                                                                     button_style='',
                                                                     # 'success', 'info', 'warning', 'danger' or ''
                                                                     tooltip='Apply specified filter',
                                                                     # icon='fa-bomb',
                                                                     style=style,
                                                                     layout=widgets.Layout(display='flex',
                                                                                           align_self='center'
                                                                                           )
                                                                     )

                def apply_filter_button_clicked(button_apply: widgets.Button):
                    new_dataset_files: List[DatasetFile] = self.filter_specification_box.filter(datasets=self.datasets)
                    filtered_files = [dataset for dataset in self.datasets if dataset not in new_dataset_files]
                    if len(filtered_files) != 0:
                        self.dataset_filters.append(DatasetFileFilter(
                            filtered_datasets=filtered_files,
                            description=self.filter_specification_box.get_description()))
                        self.update_selected_filters()

                        self.datasets = new_dataset_files
                        self.update_selected_dataset_files()

                        self.filter_specification.layout.display = 'none'
                        self.filter_specification_box = FilterBox()
                        self.filter_specification.children = []

                apply_filter_button.on_click(apply_filter_button_clicked)

                def filter_options_change(filter_change):
                    filter_option = filter_change['new']
                    if filter_option == filter_options[0]:  # default
                        if not isinstance(self.filter_specification_box, FrequencyFilterBox):
                            self.filter_specification_box = FrequencyFilterBox()

                    elif filter_option == filter_options[1]:  # interval
                        if not isinstance(self.filter_specification_box, IntervalFilterBox):
                            self.filter_specification_box = IntervalFilterBox()

                    elif filter_option == filter_options[2]:  # regular expression
                        if not isinstance(self.filter_specification_box, RegexFilterBox):
                            self.filter_specification_box = RegexFilterBox(format_options=display_formats)

                    self.filter_specification.children = [filter_options_dropdown, self.filter_specification_box,
                                                          apply_filter_button]

                filter_options_dropdown.observe(filter_options_change, names=['value'])
                filter_options_change(filter_change={'new': filter_options[0]})

                self.filter_specification.layout = widgets.Layout(display='flex',
                                                                  flex_flow='column wrap',
                                                                  align_items='flex-start'
                                                                  )
            elif self.filter_specification.layout.display == 'none':
                self.filter_specification.layout.display = 'flex'

            else:
                self.filter_specification.layout.display = 'none'

        create_filter_button.on_click(create_filter_button_clicked)

        remove_selected_filter_button = widgets.Button(description='Remove selected',
                                                       disabled=False,
                                                       button_style='warning',
                                                       # 'success', 'info', 'warning', 'danger' or ''
                                                       tooltip='Remove selected filters',
                                                       # icon='fa-bomb',
                                                       style=style
                                                       )

        def remove_selected_filter_button_clicked(button_remove: widgets.Button):
            filter_descriptions: List[str] = self.filter_selection.value
            filters_to_to_remove: List[DatasetFileFilter] = []
            for filter_description in filter_descriptions:
                for dataset_filter in self.dataset_filters:
                    if str(dataset_filter) == filter_description:
                        filters_to_to_remove.append(dataset_filter)
            for dataset_filter in filters_to_to_remove:
                self.datasets.extend(dataset_filter.get_datasets())
            self.update_selected_dataset_files()

            self.dataset_filters = [dataset_filter for dataset_filter in self.dataset_filters if
                                    dataset_filter not in filters_to_to_remove]
            self.update_selected_filters()

        remove_selected_filter_button.on_click(remove_selected_filter_button_clicked)

        filter_buttons_box: widgets.VBox = widgets.VBox([create_filter_button, remove_selected_filter_button])

        filter_selection_box = widgets.HBox([self.filter_selection, filter_buttons_box])

        filter_box: widgets.HBox = widgets.HBox(
            [filter_selection_box, self.filter_specification],
            layout=widgets.Layout(display='flex',
                                  flex_flow='column wrap',
                                  align_items='flex-start'
                                  )
        )

        # confirm_button = widgets.Button(description='Confirm',
        #                                 disabled=False,
        #                                 button_style='success',  # 'success', 'info', 'warning', 'danger' or ''
        #                                 tooltip='Confirm selected datasets',
        #                                 # icon='fa-wheelchair-alt',
        #                                 style=style,
        #                                 width='100%',
        #                                 height='auto'
        #                                 )

        # def confirm_button_clicked(b):
        #     # TODO -> file paths to main
        #     print(self.get_file_paths())

        # confirm_button.on_click(confirm_button_clicked)

        # confirm_button_box = widgets.HBox(children=[confirm_button], layout=widgets.Layout(display='flex',
        #                                                                                    flex_flow='column',
        #                                                                                    align_items='center',
        #                                                                                    width='100%',
        #                                                                                    height='auto')
        #                                   )

        self.dataset_specification_box = widgets.VBox([dataset_box, filter_box])

        self.main_component.children = [self.date_selection_box, self.dataset_specification_box]
        self.main_component.set_title(1, 'Dataset Filtering')
        self.main_component.selected_index = 1

    def update_selected_dataset_files(self):  # [DatasetFile]
        """Sorts datasets and populates MultipleSelection with their names"""
        # print('updating dataset list')

        self.datasets = sorted(self.datasets, key=lambda file: file.date)
        self.dataset_files_selection.options = [str(dataset) for dataset in self.datasets]
        self.dataset_files_selection.style = style

    def update_selected_filters(self):
        """Sorts filters and populates MultipleSelection with their descriptions"""
        # print('updating filter list')

        self.dataset_filters = sorted(self.dataset_filters,
                                      key=lambda dataset_filter: dataset_filter.description)

        self.filter_selection.options = [str(dataset_filter) for dataset_filter in self.dataset_filters]
        self.filter_selection.style = style

    def remove_datasets(self, datasets_to_remove: list = None):
        """Removes datasets from MultipleSelection. Appends removed datasets to another list, so they can be recalled."""
        # print('removing datasets')
        if datasets_to_remove is not None:
            removed_datasets = []
            for dataset_attr in datasets_to_remove:
                for dataset in self.datasets:
                    if str(dataset_attr) == str(dataset):
                        removed_datasets.append(dataset)
            self.datasets = [dataset for dataset in self.datasets if dataset not in removed_datasets]
            self.recently_removed_datasets.append(removed_datasets)
            self.update_selected_dataset_files()

    def get_widget(self) -> widgets:
        return self.main_component

    def get_file_paths(self) -> list:
        return [str(dataset.get_filepath()) for dataset in self.datasets]

    def get_file_dates(self) -> list:
        return [dataset.get_date() for dataset in self.datasets]


def notify(text: str):
    display(HTML("<script>alert('{}');</script>".format(text)))


class DateSelector(widgets.HBox):

    def __init__(self, layout: widgets.Layout = None):
        if layout is None:
            layout = widgets.Layout(display='flex',
                                    flex_flow='row',
                                    align_items='center',
                                    justify_content='center',
                                    style=style)
        super().__init__(layout=layout)

        self.datetime_start: datetime = None
        self.datetime_end: datetime = None

        self.datepicker_start: widgets.DatePicker = widgets.DatePicker(
            description='Pick a Start Date:',
            disabled=False,
            style=style
        )
        self.hourpicker_start: widgets.BoundedIntText = widgets.BoundedIntText(value=0,
                                                                               min=0,
                                                                               max=23,
                                                                               step=1,
                                                                               description='Hour:',
                                                                               disabled=False,
                                                                               style=style
                                                                               )
        self.datepicker_end: widgets.DatePicker = widgets.DatePicker(
            description='Pick an End Date:',
            disabled=False,
            style=style
        )
        self.hourpicker_end: widgets.BoundedIntText = widgets.BoundedIntText(value=0,
                                                                             min=0,
                                                                             max=23,
                                                                             step=1,
                                                                             description='Hour:',
                                                                             disabled=False,
                                                                             style=style
                                                                             )

        start_date_box: widgets.VBox = widgets.VBox([self.datepicker_start, self.hourpicker_start])
        end_date_box: widgets.VBox = widgets.VBox([self.datepicker_end, self.hourpicker_end])

        self.children = [start_date_box, end_date_box]

    # checks if selected dates are valid. If they are, creates datetime objects from these dates and the selected hours
    # return: True if start and end dates are valid, False otherwise
    def evaluate_dates(self) -> bool:
        # print('Checking whether selected dates are valid')

        date_start = self.datepicker_start.value
        date_end = self.datepicker_end.value

        # evaluate if date selection is valid
        if date_start is None or date_end is None:
            if date_start is None and date_end is None:
                notify("Start and End dates are not set")
            elif date_start is None:
                notify("Start date is not set")
            elif date_end is None:
                notify("End date is not set")
            return False
        if date_start > date_end:
            notify("Start date has to be previous to end date")
            return False

        # create datetime.time object from selected hours
        time_start: time = time(hour=self.hourpicker_start.value)
        time_end: time = time(hour=self.hourpicker_end.value)

        # add selected hours to selected dates (datetime.date -> datetime.datetime)
        self.datetime_start = datetime.combine(date_start, time_start)
        self.datetime_end = datetime.combine(date_end, time_end)
        return True

    def get_end_date(self):
        return self.datetime_end

    def get_start_date(self):
        return self.datetime_start


class FilterBox(widgets.Box):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout.visibility = 'visible'

    def get_description(self) -> str:
        return 'Base Filter'

    def filter(self, datasets: List[DatasetFile]) -> List[DatasetFile]:
        return datasets


class FrequencyFilterBox(FilterBox):
    ID: int = 0

    def __init__(self, **kwargs):

        self.frequency_options = ['2nd', '3rd', '5th']
        self.frequency_selection: widgets.Dropdown = widgets.Dropdown(
            options=self.frequency_options,
            value=self.frequency_options[0],
            description='Remove every',
            disabled=False,
            style=style
        )

        info_label2: widgets.Label = widgets.Label(value='dataset file', style=style)

        layout = widgets.Layout(display='flex',
                                flex_flow='row nowrap',
                                justify_content='flex-start',
                                align_items='flex-start',
                                )

        children = [self.frequency_selection, info_label2]

        super().__init__(**kwargs, children=children, layout=layout)

    def get_description(self) -> str:
        return 'Every ' + str(self.frequency_selection.value) + ' (' + str(FrequencyFilterBox.ID) + ')'

    def filter(self, datasets: List[DatasetFile]) -> List[DatasetFile]:
        timescale = self.frequency_selection.value
        frequency: int = 1
        if timescale == self.frequency_options[0]:
            frequency = 2
        elif timescale == self.frequency_options[1]:
            frequency = 3
        elif timescale == self.frequency_options[2]:
            frequency = 5
        filtered_datasets = [dataset for dataset in datasets if dataset not in datasets[frequency - 1::frequency]]
        if len(filtered_datasets) != len(datasets):
            FrequencyFilterBox.ID += 1
        return filtered_datasets


class IntervalFilterBox(FilterBox):

    def __init__(self, **kwargs):
        self.interval_selection: DateSelector = DateSelector()

        children = [self.interval_selection]

        super().__init__(**kwargs, children=children)

    def get_description(self) -> str:
        return 'From ' + str(self.interval_selection.get_start_date()) + ' until ' + str(
            self.interval_selection.get_end_date())

    def filter(self, datasets: List[DatasetFile]) -> List[DatasetFile]:
        if self.interval_selection.evaluate_dates():
            start_date = self.interval_selection.get_start_date()
            end_date = self.interval_selection.get_end_date()
            filtered_datasets = []
            for dataset in datasets:
                if not start_date <= dataset.get_date() <= end_date:
                    filtered_datasets.append(dataset)
            return filtered_datasets
        return datasets


class RegexFilterBox(FilterBox):

    def __init__(self, format_options: List[str], **kwargs):

        self.display_options = format_options

        placeholders = ['.*00.nc$ -> first hour of each day', '^2020-04 -> april of 2020']
        self.regex_selection: widgets.Text = widgets.Text(
            value='',
            placeholder=placeholders[0],
            description='Expression:',
            disabled=False,
            style=style,
            layout=widgets.Layout(display='flex',
                                  align_self='unset'
                                  )
        )

        self.format_selection: widgets.Dropdown = widgets.Dropdown(
            options=format_options,
            value=format_options[0],
            description=' regarding',
            disabled=False,
            style=style
        )

        def format_selection_change(change):
            selected_format = change['new']
            if selected_format == format_options[1]:
                self.regex_selection.placeholder = placeholders[1]
            else:
                self.regex_selection.placeholder = placeholders[0]

        self.format_selection.observe(format_selection_change, names=['value'])

        children = [self.regex_selection, self.format_selection]

        layout = widgets.Layout(display='flex',
                                flex_flow='row nowrap',
                                align_items='flex-start'
                                )

        super().__init__(**kwargs, children=children, layout=layout)

    def get_description(self) -> str:
        return str(self.regex_selection.value)

    def filter(self, datasets: List[DatasetFile]) -> List[DatasetFile]:
        pattern = re.compile(self.regex_selection.value)
        filtered_datasets = []
        for dataset in datasets:
            dataset.set_display_format(self.format_selection.value)
            matches: bool = bool(re.match(pattern=pattern, string=str(dataset)))
            if not matches:
                filtered_datasets.append(dataset)
        return filtered_datasets
