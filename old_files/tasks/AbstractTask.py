import os
import time
from qgis.utils import iface

from PyQt5.QtCore import QObject, pyqtSignal

from old_files.tools import FileRWriter


# from tools.FileRWriter import FileRWriter


class AbstractTask(QObject):
    progress = pyqtSignal(str, int, int)  # log/editor, text_style, mess_text
    finished = pyqtSignal(str, int, int)

    # required fields
    ID = 'ID'
    FLIGHT_NUM = 'FLIGHT_NUM'
    TIME = 'TIME'
    AZIMUTH = 'AZIMUTH'
    AZ_DIFF = 'AZ_DIFF'
    CLASS = 'CLASS'
    PAIR_NUM = 'PAIR_NUM'

    CSV_FORMATS = ('.txt', '.csv')
    SHP_FORMAT = '.shp'

    CSV_PARAMS = {  # values by default
        'xField': 'LON',
        'yField': 'LAT',
        'delimiter': '\t',
        'crs': 'epsg:4326'
    }

    def __init__(self, params, out_tool):
        super().__init__()
        self.out = out_tool
        self._isRunning = True
        self.isConsole = False
        self.isMetric = True  # if true - coordinates in metric

        self.params = params  # dictionary
        self.input_name = params.get('INPUT')
        self.output_path = params.get('OUTPUT')

        self.input_path = ''
        self.input_ext = ''
        self.output_name = ''
        self.output_ext = ''
        self.geom_type = 'Point'
        self.csv_params = self.CSV_PARAMS

    def stop(self):
        self._isRunning = False

    def print(self, mess_text, mess_type=0, which_editor=0):
        if not self.isConsole:
            if self._isRunning:
                time.sleep(1)
                self.progress.emit(mess_text, mess_type, which_editor)
            else:
                time.sleep(1)
                self.finished.emit(mess_text, mess_type, which_editor)
        else:
            print(mess_text)

    def input_metadata(self):
        wr = FileRWriter()

        if self.isConsole:
            self.input_path = self.input_name
            in_fn, self.input_ext = os.path.splitext(self.input_path)
        else:
            # # vlayer = QgsProject.instance().mapLayersByName(self.input_name)[0]
            vlayer = [i for i in iface.mapCanvas().layers() if i.name() == self.input_name][0]
            info, self.input_path, self.input_ext, self.csv_params = \
                wr.vlayer_metadata(vlayer, self.input_path, self.input_ext, self.csv_params)

            for line in info[1:]:
                self.print(line, info[0])

    def output_metadata(self):
        out_fn, self.output_ext = os.path.splitext(self.output_path)
        self.output_name = os.path.basename(out_fn)

    def extract_metadata(self):
        self.input_metadata()
        self.output_metadata()

    def read_data(self):
        wr = FileRWriter()

        # csv format
        if self.input_ext in self.CSV_FORMATS:
            signal, mess, gdf = wr.read_csv_with_params(self.input_path, self.csv_params)
            self.print(mess, signal)

            if gdf is not None and self.isMetric:
                signal, mess, gdf = wr.check_metric(self.input_name, gdf)
                self.print(mess, signal)

        # shapefile
        elif self.input_ext == self.SHP_FORMAT:
            signal, mess, gdf = wr.read_shapefile(self.input_path)
            self.print(mess, signal)

            if gdf is not None:
                signal, mess, gdf = wr.check_geometry(gdf, self.geom_type, self.input_path)
                self.print(mess, signal)

                if gdf is not None and self.isMetric:
                    signal, mess, gdf = wr.check_metric(self.input_name, gdf)
                    self.print(mess, signal)

        # wrong format
        else:
            self.print(f'\nФормат файла {self.input_path} не распознан!', -1)
            gdf = None

        return gdf

    def write_result(self, gdf):
        wr = FileRWriter()

        # csv format
        if self.output_ext in self.CSV_FORMATS:
            signal, mess, uri = wr.write_csv_file(gdf, self.output_path, self.csv_params)
            self.print(mess, signal)

            if not self.isConsole:
                wr.upload_to_legend(uri, self.output_name, "delimitedtext")

        # shapefile
        elif self.output_ext == self.SHP_FORMAT:
            signal, mess = wr.write_shapefile(gdf, self.output_path)
            self.print(mess, signal)

            if not self.isConsole:
                wr.upload_to_legend(self.output_path, self.output_name, 'ogr')

        else:
            self.print(f'\nФайл не был сохранен! Неправильный формат данных!', -1)

    def process_data(self, data):
        pass

    def run(self):
        """Run task process"""
        pass
