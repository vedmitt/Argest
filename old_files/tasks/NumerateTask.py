import math
import os

# from tools.Math import Math
# from tools.decorators import ExceptionHandle
# from AbstractTask import AbstractTask

from old_files.tools import Math
from old_files.tools import ExceptionHandle
from .AbstractTask import AbstractTask


class NumerateTask(AbstractTask):

    def __init__(self, params, out_tool):
        super(NumerateTask, self).__init__(params, out_tool)

    def process_data(self, gdf):
        a = Math()
        buffer = gdf.buffer(10)
        geometry = gdf.geometry

        # gdf['ID'] = gdf.index
        gdf[self.AZIMUTH] = 0
        gdf[self.AZ_DIFF] = 0
        gdf[self.FLIGHT_NUM] = 1

        profile = 1
        i = 2

        while i < len(gdf):
            if geometry[i-2] is None or geometry[i-1] is None or geometry[i] is None:
                pass
            else:
                x0 = (geometry[i-2].x, geometry[i-2].y)
                x1 = (geometry[i-1].x, geometry[i-1].y)
                x = (geometry[i].x, geometry[i].y)

                a1 = a.azimuth_calc(x0, x1)
                a2 = a.azimuth_calc(x1, x)
                diff = math.fabs(a1 - a2)

                gdf.at[i-1, self.AZIMUTH] = a1
                gdf.at[i, self.AZIMUTH] = a2
                gdf.at[i, self.AZ_DIFF] = diff

                if not buffer[i-1].intersects(buffer[i]) and diff > 5:
                    profile += 1
                gdf.at[i, self.FLIGHT_NUM] = profile

            i += 1

        return gdf

    def run(self):
        """Numerate Task. Main function"""
        if self.input_name == "" or self.output_path == "":
            self.print('Введите данные в форму!', -1)
        else:
            ExceptionHandle(self.extract_metadata, self.out,
                            err_text='\nОшибка при извлечении метаданных слоя. Введите корректные данные')()

            data = ExceptionHandle(self.read_data, self.out,
                                   err_text='\nОшибка при чтении исходных данных. Неправильный формат данных')()

            # self.print(f'{data}')

            if data is not None:
                data = ExceptionHandle(lambda: self.process_data(data), self.out,
                                       err_text='\nОшибка при нумерации профилей.')()
                # self.print(f'{data}')
                # data.plot(column=self.FLIGHT_NUM)
                # plt.show()
                if data is not None:
                    self.print(f'\nПрофиля успешно пронумерованы!', 1)
                    ExceptionHandle(lambda: self.write_result(data), self.out,
                                    err_text='\nОшибка при записи результата в файл.')()

        self.stop()
        self.print('\nВыполнение операции завершено.')


if __name__ == "__main__":
    dir_path = '/Users/ronya/Docs/GIS/TESTDATA'
    # input_fname = 'input/Tyukan_rad_All.csv'
    # input_fname = 'input/TyukanGK19_rad_all.shp'
    # output_fname = 'output/Tyukan_rad_new-Cut_GK19__output.shp'

    # input_fname = 'input/Tyukan_spectr_All_cut_GK19.shp'
    # output_fname = 'output/Tyukan_spectr_All_cut_GK19__output.shp'

    input_fname = 'input/NorilskGK30_variated_shp.shp'
    output_fname = 'output/NorilskGK30_variated_num.shp'

    params = {
        'INPUT': os.path.join(dir_path, input_fname),
        'OUTPUT': os.path.join(dir_path, output_fname),
    }
    task = NumerateTask(params, None)
    task.isConsole = True
    task.run()
