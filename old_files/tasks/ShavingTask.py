import os

# from tools.Math import Math
# from tools.decorators import ExceptionHandle
# from AbstractTask import AbstractTask

from old_files.tools import Math
from old_files.tools import ExceptionHandle
from .AbstractTask import AbstractTask


class ShavingTask(AbstractTask):

    def __init__(self, params, out_tool):
        super(ShavingTask, self).__init__(params, out_tool)
        self.params = params
        self.radius = 20

    def calc_all_azimuths(self, gdf):
        a = Math()
        geometry = gdf.geometry

        gdf[self.ID] = gdf.index
        gdf[self.AZIMUTH] = 0
        # gdf[self.AZ_DIFF] = 0

        # подсчет азимутов
        i = 2
        while i < len(gdf):
            if geometry[i - 2] is None or geometry[i - 1] is None or geometry[i] is None:
                pass
            else:
                x0 = (geometry[i - 2].x, geometry[i - 2].y)
                x1 = (geometry[i - 1].x, geometry[i - 1].y)
                x = (geometry[i].x, geometry[i].y)

                a1 = a.azimuth_calc(x0, x1)
                a2 = a.azimuth_calc(x1, x)
                # diff = math.fabs(a1 - a2)

                gdf.at[i - 1, self.AZIMUTH] = a1
                gdf.at[i, self.AZIMUTH] = a2
                # gdf.at[i, self.AZ_DIFF] = diff

            i += 1

        return gdf

    def opposite_azimuth(self, az):
        if 0 <= az < 180:
            return az + 180
        elif 180 <= az < 360:
            return az - 180

    def get_targets(self, gdf):
        azimuths = gdf[gdf.LON != 0].AZIMUTH  # избавимся от нулевых координат

        # # построим гистограмму по азимутам
        # plt.hist(azimuths, bins=20)
        # plt.show()

        # найдем самые популярные азимуты
        az_freq = azimuths.value_counts()
        self.print(f'\nЧастота азимутов: \n{az_freq}')
        a = az_freq.nlargest(1).index
        a = (*a, self.opposite_azimuth(*a))
        self.print(f'\n\nЦелевые азимуты: {a}')
        return a

    def specify_bounds(self, step, targets):
        m = Math()
        bounds = [m.build_bounds((t - step, t + step)) for t in targets]
        new_list = [v1 for sub_list in bounds for v1 in sub_list]
        bounds = []
        i = 0
        while i < len(new_list):
            bounds.append((new_list[i], new_list[i + 1]))
            i += 2
        self.print(f'\n Интервалы азимутов: {bounds}')
        return bounds

    def classify(self, gdf, bounds):
        gdf[self.CLASS] = 0
        i = 0
        while i < len(gdf):
            a = gdf.loc[i, self.AZIMUTH]
            for b in bounds:
                if b[0] <= a <= b[1]:
                    gdf.at[i, self.CLASS] = 1
            i += 1

        # print(f'\n{gdf.query("CLASS == 1")}')
        return gdf

    # def rewiew(self, gdf):
    #     i = 0
    #     while i < len(gdf):
    #         pass

    def delete_points(self, gdf):
        gdf = gdf.query(f"{self.CLASS} == 1")
        return gdf

    def process_data(self, gdf):
        gdf = self.calc_all_azimuths(gdf)  # подсчитываем значения всех азимутов
        targets = self.get_targets(gdf)  # найдем профильные азимуты
        bounds = self.specify_bounds(self.radius, targets)  # вычислим интервал допустимых азимутов
        gdf = self.classify(gdf, bounds)  # классификация 1 - полезная точка, 0 - нет

        # self.print(str(gdf.shape))
        gdf = gdf[gdf.LON != 0]
        # self.print(str(gdf.shape))

        if self.params.get('DEL'):
            gdf = self.delete_points(gdf)
        return gdf

    def run(self):
        """Shaving Task. Main function"""
        ExceptionHandle(self.extract_metadata, self.out,
                        err_text='\nОшибка при извлечении метаданных слоя. Введите корректные данные')()

        data = ExceptionHandle(self.read_data, self.out,
                               err_text='\nОшибка при чтении исходных данных. Неправильный формат данных')()

        # self.print(f'\n{data}')

        if data is not None:
            data = ExceptionHandle(lambda: self.process_data(data), self.out,
                                   err_text='\nОшибка при разбраковке точек.')()
            # self.print(f'{data}')
            if data is not None:
                self.print(f'\nПрофиля успешно разбракованы!', 1)
                ExceptionHandle(lambda: self.write_result(data), self.out,
                                err_text='\nОшибка при записи результата в файл.')()

        self.stop()
        self.print('\nВыполнение операции завершено.')


if __name__ == "__main__":
    dir_path = '/Users/ronya/Docs/GIS/TESTDATA'
    # input_fname = 'input/Tyukan_rad_All.csv'
    # input_fname = 'input/TyukanGK19_rad_all.shp'
    # output_fname = 'output/Tyukan_rad_new-Cut_GK19__output.shp'

    # input_fname = 'input/20200921_EgerlaghGK24_VariatedData(60000).shp'
    # output_fname = 'output/20200921_EgerlaghGK24_VariatedData(60000)__output.shp'

    # input_fname = 'input/20210921.shp'
    # output_fname = 'output/20210921__output.shp'

    input_fname = 'input/20210922.shp'
    output_fname = 'output/20210922__output.shp'

    params = {
        'INPUT': os.path.join(dir_path, input_fname),
        'OUTPUT': os.path.join(dir_path, output_fname),
    }
    task = ShavingTask(params, None)
    task.isConsole = True
    task.run()
