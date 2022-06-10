import os
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import Point

# import processing
# from qgis.core import edit
from PyQt5.QtCore import QVariant
from qgis._core import QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsPoint
from qgis.utils import iface


class FileRWriter:

    def __init__(self):
        pass

    def vlayer_metadata(self, vlayer, input_path, input_ext, csv_params):
        info = [0]

        provider = vlayer.dataProvider()
        storage_type = provider.storageType()
        uri = provider.dataSourceUri()
        info.append(f'{storage_type}')
        info.append(f'uri = {uri}')

        # если слой представлен в виде шейпфайла
        if storage_type == 'ESRI Shapefile':
            input_path, input_ext = self.shape_lyr_metadata(uri)
            info.append(f'\n{input_path} --- {input_ext}')

        # если слой представлен в виде текстового файла
        elif storage_type == 'Delimited text file':
            input_path, input_ext, csv_params = self.csv_lyr_metadata(uri)
            info.append(f'{input_path}, {input_ext}')
            info.append(str(csv_params))

        else:
            info = [-1, f'Не удалось прочесть метаданные слоя {vlayer.name()}! '
                        f'Поддерживаются только данные формата csv/txt или shp.']
        return info, input_path, input_ext, csv_params

    def shape_lyr_metadata(self, uri):
        if uri.find('|') != -1:
            input_path = uri[:uri.rfind('|')]
        else:
            input_path = uri

        _, input_ext = os.path.splitext(input_path)
        return input_path, input_ext

    def csv_lyr_metadata(self, uri):
        fpath, params = uri.split('?')
        input_path = fpath[8:]
        in_fn, input_ext = os.path.splitext(input_path)
        comp = params.split('&')
        csv_params = {}

        for item in comp:
            name, val = item.split('=')
            csv_params.setdefault(name, val)

        if 'delimiter' not in csv_params.keys():
            csv_params.setdefault('delimiter', ',')

        if csv_params.get('delimiter') == '%5Ct':
            csv_params['delimiter'] = '\t'

        return input_path, input_ext, csv_params

    def read_shapefile(self, input_path):
        gdf = gpd.read_file(input_path, encoding='latin1')  # <class 'geopandas.geodataframe.GeoDataFrame'>
        if gdf is not None:
            return 1, f'\nВходной файл {input_path} успешно прочтен.', gdf
        else:
            return -1, f'\nОшибка при чтении файла.', None

    def read_csv_with_params(self, input_path, csv_params):
        df = pd.read_csv(input_path, delimiter=csv_params.get('delimiter'), encoding='latin1')
        gdf = GeoDataFrame(
            df,
            crs=csv_params.get('crs'),
            geometry=[
                Point(xy) for xy in zip(
                    df[csv_params.get('xField')],
                    df[csv_params.get('yField')]
                )]
        )
        if gdf is not None:
            return 1, f'\nВходной файл {input_path} успешно прочтен.', gdf
        else:
            return -1, f'\nОшибка при чтении файла.', None

    def read_var_file(self, file_path):
        with open(file_path) as f:
            lines = f.readlines()
            # print(len(lines))

        if len(lines) > 0:
            col_count = len(lines[int(len(lines) / 2)].replace('\n', '').split(' '))
            # print(col_count)

            head = []
            data = []
            try:
                for i, line in enumerate(lines):
                    tuple = line.replace('\n', '').split(' ')
                    # print(tuple)
                    if len(tuple) == col_count and tuple[0] != ';':
                        data.append(tuple)

                        if len(head) == 0:
                            if i > 0:
                                first_line = lines[i-1:i][0].replace('\n', '').split(' ')
                                head = [i for i in first_line if i != '' and i != ';']
                            else:
                                return -1, 'Имена столбцов не найдены.', None
                # print(len(data))
                # print(head)

                if len(head) == len(data[0]):
                    df = pd.DataFrame.from_records(data, columns=head)
                    return 1, f'\nВходной файл {file_path} успешно прочтен.', df

            except Exception as err:
                return -1, f'\nОшибка при чтении файла. {err}', None
        else:
            return -1, f'\nФайл пуст.', None

    def check_geometry(self, gdf, type, input_path):
        if gdf.geom_type[0] != type:
            return -1, \
                   f'\nГеометрия входного файла {input_path} должна быть типа {type}, а не {gdf.geom_type[0]}!', \
                   None
        else:
            return 0, \
                   f'\nГеометрия входного слоя соответсвует типу {type}.', \
                   gdf

    def _check_metric(self, point_x):
        if point_x > 1000:  # metric
            return 1
        else:
            return 0  # lat lon or other

    def check_metric(self, input_name, gdf):
        point = gdf.geometry.x[0]
        if self._check_metric(point) == 1:
            return 0, \
                   f'\ncrs - {gdf.crs}\ngeometry type - {gdf.geom_type[0]} ({point})', \
                   gdf
        else:
            return -1, \
                   f'\nГеометрия слоя {input_name} должна быть выражена в метрах! Используйте проекцию Гаусса-Крюгера. ({point})', \
                   None

    def write_to_file(self, mode, fpath, text):
        """ Запись файла из списка строк. """
        try:
            with open(fpath, mode) as f:
                f.write(text)
            return 1, f'\nФайл успешно сохранен в {fpath}.'
        except FileNotFoundError:
            return -1, f'\nФайл не найден. Ошибка при сохранении файла.'

    def layers_from_canvas(self, areVisible=True):
        """ Возвращает словарь видимых слоев из канваса. """
        if areVisible is True:  # по умолчанию только видимые слои
            layers = iface.mapCanvas().layers()
        else:
            layers = QgsProject.instance().mapLayers().values()  # все слои из легенды
        return {item.name(): item for item in layers}

    def upload_to_legend(self, path, name, type):
        vlayer = QgsVectorLayer(path, name, type)
        QgsProject.instance().addMapLayer(vlayer)

    def write_csv_file(self, gdf, output_path, csv_params, index=False, drop_geom=True):
        if drop_geom:
            gdf.drop('geometry', axis=1).to_csv(output_path, sep=csv_params['delimiter'], index=index)
        else:
            gdf.to_csv(output_path, sep=csv_params['delimiter'], index=index)

        if csv_params['delimiter'] == '\t':
            csv_params['delimiter'] = '%5Ct'
        uri = 'file://{}?type=csv&delimiter={}&maxFields=10000&detectTypes=yes&xField={}&yField={}&crs={}' \
              '&spatialIndex=no&subsetIndex=no&watchFile=no'.format(output_path,
                                                                    csv_params['delimiter'],
                                                                    csv_params['xField'],
                                                                    csv_params['yField'],
                                                                    csv_params['crs'])
        return 1, f'\nФайл успешно сохранен в {output_path}', uri

    def write_shapefile(self, gdf, output_path, index=False):
        gdf.to_file(output_path, index=index)
        return 1, f'\nФайл успешно сохранен в {output_path}'

    def create_memory_lyr(self):  # not used
        # create layer
        vl = QgsVectorLayer("Point", "temporary_points", "memory")
        pr = vl.dataProvider()

        # add fields
        pr.addAttributes([QgsField("name", QVariant.String),
                          QgsField("age", QVariant.Int),
                          QgsField("size", QVariant.Double)])
        vl.updateFields()  # tell the vector layer to fetch changes from the provider

        # add a feature
        fet = QgsFeature()
        fet.setGeometry(QgsPoint(10, 10))
        fet.setAttributes(["Johny", 2, 0.3])
        pr.addFeatures([fet])

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        vl.updateExtents()
        QgsProject.instance().addMapLayer(vl)


if __name__ == "__main__":
    # dir_path = '/Users/ronya/Docs/GIS/TESTDATA/variations_test'
    # input_name = 'var/05030748.txt'

    dir_path = '/Users/ronya/Docs/GIS/TESTDATA/input/Aunakit'
    input_name = 'Var/07210132.txt'

    input_path = os.path.join(dir_path, input_name)
    wr = FileRWriter()
    mess = wr.read_var_file(input_path)
    print(mess)
