import math
from datetime import datetime

from click import edit
from qgis.core import (
    QgsVectorFileWriter,
    QgsProject, QgsFields, QgsField, QgsWkbTypes, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer,
    QgsFeatureRequest, QgsVectorDataProvider,
)
from qgis.PyQt.QtCore import QVariant
from osgeo import ogr
import os
import sys

# На вход могут подавться различные типы данных, а не только шейпфайлы
# Например, это могут быть временные слои, текстовые файлы и др.
# Плагин должен уметь распознавать эти типы данных и работать с ними
# Сохранение тоже должно выполняться в разные форматы.
# Нужно изменить интерфейс таким образом, чтобы сохранение выполнялось.



if __name__ == "__main__":
    # layer = QgsVectorLayer(r'M:\Sourcetree\bpla_plugin_flights\output\test_f1f8.shp', 'test_f1f8', 'ogr')
    # layer = QgsVectorLayer(r'M:\YandexDisk\QGIS\my_data_source\20200905_(F1-8)wMagnCoord.txt', '20200905_(F1-8)wMagnCoord', 'ogr')
    #
    # print(layer.dataProvider().storageType())
    # print(layer.metadataUri())
    # print(layer.dataProvider().dataSourceUri())
    # print(layer.dataUrl())

    str = 'file:///M:/YandexDisk/QGIS/my_data_source/20200905_(F25-27)wMagnCoord.txt?type=csv&delimiter=%5Ct&detectTypes=yes&xField=LON&yField=LAT&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no'
    fn = str.split('?')
    fn = fn[0].split('///')
    print(fn[1])