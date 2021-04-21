from PyQt5.QtGui import QColor, QFont
from qgis._core import QgsVectorLayer
from qgis.utils import iface

global actVecLyrDict, layer


class LayerGetter:

    # layer = None
    # layername = None
    # layerpath = None
    # driverName = None
    # csvFileAttrs = {}
    actVecLyrDict = {}

    def __init__(self):
        self.layer = None
        self.layername = None
        self.layerpath = None
        self.driverName = None
        self.csvFileAttrs = {}


    def getActiveLayers(self):
        LayerGetter.actVecLyrDict = {}
        layers = iface.mapCanvas().layers()  # по умолчанию только видимые слои
        for item in layers:
            if ((type(item) == QgsVectorLayer) and (item.geometryType() == 0)):
                # setdefault добавляет элементы с проверкой на повторяющиеся
                # если у пользователя два слоя с одиноковыми именами, в комбобокс попадет только один из них
                LayerGetter.actVecLyrDict.setdefault(item.name(), item)
        return LayerGetter.actVecLyrDict


    def getLayer(self, layerstr):
        self.layer = self.getActiveLayers().get(layerstr)

        if self.layer is not None:
            self.layername = self.layer.name()
            self.driverName = self.layer.dataProvider().storageType()
            cur_lyr_path = self.layer.dataProvider().dataSourceUri()

            if self.driverName == 'ESRI Shapefile':
                char_arr = cur_lyr_path.split('|')
                self.layerpath = char_arr[0]

            elif self.driverName == 'Delimited text file':
                fn = cur_lyr_path.split('?')
                fn1 = fn[0].split('///')
                self.layerpath = fn1[1]
                attr = fn[1].split('&')
                for i in range(len(attr)):
                    elem = attr[i].split('=')
                    self.csvFileAttrs.setdefault(elem[0], elem[1])

