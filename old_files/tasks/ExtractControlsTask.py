import os
import geopandas as gpd

from .AbstractTask import AbstractTask
from old_files.tools import FileRWriter
from old_files.tools import ExceptionHandle


class ExtractControlsTask(AbstractTask):
    def __init__(self, params, out_tool):
        super().__init__(params, out_tool)
        self.input_name = params.get('INPUT')

        self.out_dir = params.get('OUTPUT')

        self.scheme_name = f'{self.input_name}_scheme'
        self.control_name = f'{self.input_name}_controls'
        self.ordinary_name = f'{self.input_name}_ordinary'

        self.scheme_path = os.path.join(self.out_dir, f'{self.scheme_name}.shp')
        self.control_path = os.path.join(self.out_dir, f'{self.control_name}.shp')
        self.ordinary_path = os.path.join(self.out_dir, f'{self.ordinary_name}.shp')

    def intersection(self, gdf):  # create the scheme of repeated profiles
        # make buffer
        scheme = gdf[[self.FLIGHT_NUM, 'geometry']]
        scheme = scheme.set_geometry(gdf.buffer(10))

        # make dissolve
        scheme = scheme.dissolve(by=self.FLIGHT_NUM, as_index=False, aggfunc="first")

        # build scheme with profile polygons
        flight1 = []
        flight2 = []
        geometry = []
        area = []

        i = 0
        while i < len(scheme):
            j = 0
            while j < len(scheme):
                if scheme.geometry[i] is None or scheme.geometry[j] is None:
                    pass
                else:
                    if scheme.geometry[i].intersects(scheme.geometry[j]) and i < j:
                        f1 = scheme.loc[i, self.FLIGHT_NUM]
                        f2 = scheme.loc[j, self.FLIGHT_NUM]
                        intersection = scheme.geometry[i].build_scheme(scheme.geometry[j])
                        flight1.append(f1)
                        flight2.append(f2)
                        geometry.append(intersection)
                        area.append(intersection.area)
                j += 1
            i += 1

        scheme = gpd.GeoDataFrame(
            {
                'flight1': flight1,
                'flight2': flight2,
                'area': area,
                'geometry': geometry,
            },
            crs=gdf.crs
        )
        scheme = scheme.query('area > 10000')
        if len(scheme) > 0:
            return scheme
        else:
            return None

    def classify(self, scheme, gdf):
        gdf[self.PAIR_NUM] = 0
        i = 0
        while i < len(gdf):
            f0 = gdf.loc[i, self.FLIGHT_NUM]
            for index, row in scheme.iterrows():
                f1 = row["flight1"]
                f2 = row["flight2"]
                if (f0 == f1 and gdf.geometry[i].intersects(row["geometry"])) \
                        or (f0 == f2 and gdf.geometry[i].intersects(row["geometry"])):
                    gdf.loc[i, self.PAIR_NUM] = f2
            i += 1
        controls = gdf.query(f'{self.PAIR_NUM} > 0 and {self.FLIGHT_NUM} == {self.PAIR_NUM}')
        ordinals = gdf.query(f'{self.PAIR_NUM} == 0 or {self.FLIGHT_NUM} != {self.PAIR_NUM}')
        return controls, ordinals

    def process_data(self, gdf):
        wr = FileRWriter()
        scheme = self.intersection(gdf)

        if scheme is not None and len(scheme) > 0:
            # wr.write_shapefile(scheme, self.scheme_path)
            # wr.upload_to_legend(self.scheme_path, self.scheme_name, 'ogr')

            controls, ordinals = self.classify(scheme, gdf)

            wr.write_shapefile(controls, self.control_path)
            wr.write_shapefile(ordinals, self.ordinary_path)

            wr.upload_to_legend(self.control_path, self.control_name, 'ogr')
            wr.upload_to_legend(self.ordinary_path, self.ordinary_name, 'ogr')

            self.print('\nКонтрольные профиля успешно найдены!', 1)
        else:
            self.print('\nКонтрольные профиля не найдены!', -1)

    def run(self):
        """Выделение контролей. Main function"""

        ExceptionHandle(self.extract_metadata, self.out,
                        err_text='\nОшибка при извлечении метаданных слоя. Введите корректные данные')()

        data = ExceptionHandle(self.read_data, self.out,
                               err_text='\nОшибка при чтении исходных данных. Неправильный формат данных')()

        if data is not None and self.FLIGHT_NUM in data.columns:
            ExceptionHandle(lambda: self.process_data(data), self.out,
                            err_text='\nОшибка при выделении контролей.')()
        else:
            self.print(f'\nВ данных обязательно должно присутсвовать поле {self.FLIGHT_NUM}!', -1)

        self.stop()
        self.print('\nВыполнение операции завершено.')


if __name__ == '__main__':
    pass
