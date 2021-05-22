import os

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor, QFont
from qgis._core import *
from qgis.utils import iface

from .Feature import Feature

global actVecLyrDict, layer


class LayerManager:
    actVecLyrDict = {}

    def __init__(self):
        self.layer = None
        self.layername = None
        self.layerpath = None
        self.driverName = None
        self.csvFileAttrs = {}


    def getActiveLayers(self):
        LayerManager.actVecLyrDict = {}
        layers = iface.mapCanvas().layers()  # по умолчанию только видимые слои
        for item in layers:
            if ((type(item) == QgsVectorLayer) and (item.geometryType() == 0)):
                # setdefault добавляет элементы с проверкой на повторяющиеся
                # если у пользователя два слоя с одиноковыми именами, в комбобокс попадет только один из них
                LayerManager.actVecLyrDict.setdefault(item.name(), item)
        return LayerManager.actVecLyrDict


    def getLayer(self, layerstr):
        layer = self.getActiveLayers().get(layerstr)

        if layer is not None:
            layername = layer.name()
            driverName = layer.dataProvider().storageType()
            uri = layer.dataProvider().dataSourceUri()

            if driverName == 'ESRI Shapefile':
                char_arr = uri.split('|')
                layerpath = char_arr[0]
                return QgsVectorLayer(layerpath, layername, "ogr")

            elif driverName == 'Delimited text file':
                # uri = "file:///Users/ronya/My_Documents/input_data/20210517_Magn_Data_All/Group_1/20210503_Magn_Group_1_coord.txt?type=csv&delimiter=%5Ct&xField=LON&yField=LAT&zField=ALT".format(os.getcwd(), "x", "y")
                # fn = uri.split('?')
                # fn1 = fn[0].split('///')
                # self.layerpath = fn1[1]
                # attr = fn[1].split('&')
                # for i in range(len(attr)):
                #     elem = attr[i].split('=')
                #     self.csvFileAttrs.setdefault(elem[0], elem[1])
                return QgsVectorLayer(uri, layername, 'delimitedtext')


    def uploadLayer(self, filepath, filename, typeOfFile):
        # show our new layer in qgis
        layer = iface.addVectorLayer(filepath, filename, typeOfFile)
        if not layer:
            return -1, 'Не удалось загрузить слой в оболочку!'
        else:
            return 1, '\nСлой успешно сохранен и загружен в QGIS!'


    def saveToFile(self, driverName, fileEncoding, file_attr, features):
        newfields = QgsFields()
        fields = features.getFieldDict()
        for field in fields:
            newfields.append(QgsField(field, fields[field]))

        crs = QgsProject.instance().crs()
        transform_context = QgsProject.instance().transformContext()
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = driverName
        save_options.fileEncoding = fileEncoding

        writer = QgsVectorFileWriter.create(
            file_attr[0],
            newfields,
            QgsWkbTypes.Point,
            crs,
            transform_context,
            save_options
        )

        # add features
        feat_list = features.getFeaturesList()
        for i in range(len(feat_list)):
            f = QgsFeature()
            coordinates = feat_list[i].getGeometry()
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(QgsPointXY(coordinates))))
            f.setAttributes(features.getOrderedValList(i))

            writer.addFeature(f)
            i += 1

        # delete the writer to flush features to disk
        del writer

        mess = self.uploadLayer(file_attr[0], file_attr[1], 'ogr')
        return mess

