import os
from dateutil import parser

import pandas as pd

from .AbstractTask import AbstractTask
from old_files.tools import ExceptionHandle
from old_files.tools import FileRWriter


# from AbstractTask import AbstractTask
# from tools.decorators import ExceptionHandle
# from tools.FileRWriter import FileRWriter
# from common.SplinesArray import *


class VariationsTask(AbstractTask):

    def __init__(self, params, out_tool):
        super(VariationsTask, self).__init__(params, out_tool)
        # self.magn_format = "%d-%m-%YT%H:%M:%S,%f"
        # self.var_format = "%m-%d-%yT%H:%M:%S,%f"

        self.magn_files = params.get('INPUT')
        self.var_files = params.get('VAR')
        self.const_magn = params.get('CONST')  # 61038

        self.isConsole = False

    def read_magn(self):
        wr = FileRWriter()
        if len(self.magn_files) > 0:
            s, m, gdf = wr.read_csv_with_params(self.magn_files[0], self.CSV_PARAMS)
            self.print(f'\nReading the first magn {self.magn_files[0]} {gdf.shape}')
            if len(self.magn_files[1:]) > 0:
                for f in self.magn_files[1:]:
                    s, m, g = wr.read_csv_with_params(f, self.CSV_PARAMS)
                    self.print(f'\nReading others magn {f} {g.shape}')
                    gdf = gdf.append(g, ignore_index=True)
        else:
            gdf = None
        self.print(f'\nSummaring magn {gdf.shape}')
        return gdf

    def read_var(self):
        wr = FileRWriter()
        if len(self.var_files) > 0:
            s, m, df = wr.read_var_file(self.var_files[0])
            self.print(f'\nReading the first var {self.var_files[0]} {df.shape}')
            if len(self.var_files[1:]) > 0:
                for f in self.var_files[1:]:
                    s, m, g = wr.read_var_file(f)
                    self.print(f'\nReading others var {f} {g.shape}')
                    df = df.append(g, ignore_index=True)
        else:
            df = None
        self.print(f'\nSummaring var {df.shape}')
        return df

    def read_data(self):
        if self.output_path not in ('', None):
            self.output_metadata()  # save file metadata
        gdf = self.read_magn()
        df = self.read_var()
        return gdf, df

    def process_data(self, data):
        self.print(f'\nКонстанта магнитки: {self.const_magn}')
        gdf = data[0]
        df = data[1]

        if float(max(df['FIELD'])) > 100000:
            df["FIELD"] = pd.to_numeric(df['FIELD']) / 1000
            self.print(f'\n var FIELD \n{df["FIELD"]}')

        # df["time_milli"] = [datetime.strptime(t, self.var_format).timestamp() for t in (df.DATE + 'T' + df.TIME)]
        # gdf["time_milli"] = [datetime.strptime(t, self.magn_format).timestamp() for t in gdf.TIME]

        gdf["time_milli"] = [parser.parse(timeStr) for timeStr in gdf.TIME]
        mdays = [item.day for item in gdf["time_milli"]]
        mmonths = [item.month for item in gdf["time_milli"]]
        self.print(f'\nmagn days {set(mdays)}')
        self.print(f'magn months {set(mmonths)}')

        df["time_milli"] = [parser.parse(timeStr) for timeStr in (df.DATE + 'T' + df.TIME)]
        vdays = [item.day for item in df["time_milli"]]
        vmonths = [item.month for item in df["time_milli"]]
        self.print(f'\nvar days {set(vdays)}')
        self.print(f'var months {set(vmonths)}')

        df["time_milli"] = [dt.timestamp() for dt in df["time_milli"]]
        gdf["time_milli"] = [dt.timestamp() for dt in gdf["time_milli"]]
        self.print(f'\nvar time_milli \n{df["time_milli"]}')
        self.print(f'\nmagn time_milli \n{gdf["time_milli"]}')

        # calc variations
        var_func = SplinesArray()
        xy_var = [(row['time_milli'], row['FIELD']) for index, row in df[['time_milli', 'FIELD']].iterrows()]

        # create function with all variation points
        var_func.add_spline(xy_var)

        # calc variation points
        gdf['VARIATED'] = [row["FIELD"] + (self.const_magn - var_func.get_value(row["time_milli"]))
                           for index, row in gdf[['FIELD', 'time_milli']].iterrows()]

        self.print(f"\nmagn FIELD VARIATED \n{gdf['VARIATED']}")

        return gdf.drop("time_milli", axis=1)

    def run(self):
        """Variation Task. Main function"""
        (gdf, df) = ExceptionHandle(self.read_data, self.out,
                                    err_text='\nОшибка при чтении исходных данных. Неправильный формат данных')()

        if gdf is not None and df is not None:
            data = ExceptionHandle(lambda: self.process_data((gdf, df)), self.out,
                                   err_text='\nОшибка при расчете вариаций.')()

            if data is not None:
                self.print(f'\nВариации успешно рассчитаны!', 1)
                if self.output_path not in ('', None):
                    ExceptionHandle(lambda: self.write_result(data), self.out,
                                    err_text='\nОшибка при записи результата в файл.')()
                else:
                    self.print(f'\nРезультат не сохранен!', -1)

        self.stop()
        self.print('\nВыполнение операции завершено.')


if __name__ == '__main__':
    const_magn = 61038
    dir_path = '/Users/ronya/Docs/GIS/TESTDATA/input/Aunakit'
    var_files = [
        os.path.join(dir_path, 'Var/07210132.txt'),
        os.path.join(dir_path, 'Var/07240137.txt'),
        os.path.join(dir_path, 'Var/07250253.txt'),
        os.path.join(dir_path, 'Var/07260326.txt'),
    ]
    magn_files = [
        os.path.join(dir_path, 'Magn/20210721_Magn_Aunakit_All.txt'),
        os.path.join(dir_path, 'Magn/20210724_Magn_Aunakit_All.txt'),
        os.path.join(dir_path, 'Magn/20210725_Magn_Aunakit_All.txt'),
        os.path.join(dir_path, 'Magn/20210725_Magn_Aunakit_Control.txt'),
        os.path.join(dir_path, 'Magn/20210726_Magn_Aunakit_All.txt'),
    ]
    output_path = os.path.join(dir_path, 'Aunakit_variated.txt')

    params = {'INPUT': magn_files,
              'VAR': var_files,
              'CONST': const_magn,
              }

    v = VariationsTask(params, None)

    gdf, df = v.read_data()

    gdf = v.process_data((gdf, df))
