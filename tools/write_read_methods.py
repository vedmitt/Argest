import os
from qgis._core import QgsFeature, QgsGeometry, QgsFeatureSink
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import Point


def save_gdf_to_output(gdf, res_fields, output):
    """
    Creates new qgsfeatures with gdf data and adds them to output object
    """
    for i, f in gdf.iterrows():
        nf = QgsFeature()
        nf.setFields(res_fields)
        nf.setGeometry(QgsGeometry.fromWkt(str(f.geometry)))
        for attr in res_fields.names():
            nf[attr] = f[attr]
        output.addFeature(nf, QgsFeatureSink.FastInsert)


def read_file_to_gdf_from_uri(uri):
    path = get_filepath_from_uri(uri)
    if path[1] == '.shp':
        return read_shapefile(path[0])
    elif path[1] in ('.csv', '.txt'):
        return read_csv_with_params(path[0], path[2])
    else:
        return -1, '\nДанный формат файла не поддерживается!', None


def get_filepath_from_uri(s):
    path = s.split('|')[0]
    _, ext = os.path.splitext(path)

    if ext == '.shp':
        return path, ext

    elif s.split(':')[0] == 'delimitedtext':
        return get_csv_metadata_from_uri(s)


def get_csv_metadata_from_uri(uri):
    fpath, params = uri.split('?')
    input_path = fpath[23:]
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


def read_shapefile(input_path):
    gdf = gpd.read_file(input_path, encoding='latin1')  # <class 'geopandas.geodataframe.GeoDataFrame'>
    if gdf is not None:
        return 1, f'\nВходной файл {input_path} успешно прочтен.', gdf
    else:
        return -1, f'\nОшибка при чтении файла.', None


def read_csv_with_params(input_path, csv_params):
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
