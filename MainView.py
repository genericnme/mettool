import ipywidgets as widgets
from IPython.core.display import display, HTML
from ipyfilechooser import FileChooser

from SingleDataset.SDView import SDView
from Timeseries.TimeseriesView import TimeseriesView
from pathlib import Path
from os import path

ts_btn = widgets.Button(description="Timeseries")
sd_btn = widgets.Button(description="Single Dataset")
ask_root_dir: bool = False


class MainView:
    def __init__(self):
        self.main_hbox = widgets.HBox([ts_btn, sd_btn])
        ts_btn.on_click(self.ts_btn_click)
        sd_btn.on_click(self.sd_btn_click)

    def show(self):
        display(self.main_hbox)

    def ts_btn_click(self, b):
        ts_btn.disabled = True
        sd_btn.disabled = True

        if ask_root_dir:
            fc: FileChooser = FileChooser(str(Path.home()))
            fc.show_only_dirs = True
            fc.title = '<b>Select root directory</b>'

            # root_dir_text: widgets.Text = widgets.Text(
            #     value=str(Path.home()),
            #     placeholder="e.g. /home/2020/01/ecmwf_era5_21020900.nc -> root dir: /home",
            #     description='Root directory:',
            #     disabled=False,
            #     style={'description_width': 'initial'},
            #     layout=widgets.Layout(width='50%')
            # )
            lbl_info = widgets.Label(value='e.g. /home/2020/01/ecmwf_era5_21020900.nc -> root dir: /home')

            ts_start_btn = widgets.Button(description="Confim",
                                          style={'description_width': 'initial'},
                                          button_style='success'
                                          )

            root_dir_box = widgets.HBox([fc, lbl_info, ts_start_btn],
                                        layout=widgets.Layout(display='flex',
                                                              flex_flow='column',
                                                              align_items='flex-start'
                                                              )
                                        )

            def start(b: widgets.Button):
                root_dir = fc.selected_path
                if root_dir is not None:
                    view = TimeseriesView(root_dir=root_dir)
                    root_dir_box.layout.visible = 'hidden'
                    view.show()
                else:
                    display(HTML("<script>alert('{}');</script>".format("No root directory selected")))
            ts_start_btn.on_click(start)
            display(root_dir_box)

        else:
            view = TimeseriesView()
            view.show()

    def sd_btn_click(self, b):
        ts_btn.disabled = True
        sd_btn.disabled = True
        view = SDView()
        view.show()
