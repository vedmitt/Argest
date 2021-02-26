from PyQt5.QtGui import QColor, QFont
from qgis._core import QgsVectorLayer
from qgis.utils import iface

global actVecLyrDict, layer


class LayerGetter:

    layer = None
    layername = None
    layerpath = None
    drivername = None
    csvFileAttrs = {}
    actVecLyrDict = {}

    def __init__(self):
        pass


    def getActiveLayers(self, canvas):
        layers = canvas.layers()  # по умолчанию только видимые слои
        for item in layers:
            if ((type(item) == QgsVectorLayer) and (item.geometryType() == 0)):
                # setdefault добавляет элементы с проверкой на повторяющиеся
                # если у пользователя два слоя с одиноковыми именами, в комбобокс попадет только один из них
                LayerGetter.actVecLyrDict.setdefault(item.name(), item)
        return LayerGetter.actVecLyrDict


    def getLayer(self, layerstr):
        LayerGetter.layer = LayerGetter.actVecLyrDict.get(layerstr)

        if LayerGetter.layer is not None:
            LayerGetter.layername = LayerGetter.layer.name()
            LayerGetter.driverName = LayerGetter.layer.dataProvider().storageType()
            cur_lyr_path = LayerGetter.layer.dataProvider().dataSourceUri()

            if LayerGetter.driverName == 'ESRI Shapefile':
                char_arr = cur_lyr_path.split('|')
                LayerGetter.layerpath = char_arr[0]

            elif LayerGetter.driverName == 'Delimited text file':
                fn = cur_lyr_path.split('?')
                fn1 = fn[0].split('///')
                LayerGetter.layerpath = fn1[1]
                attr = fn[1].split('&')
                for i in range(len(attr)):
                    elem = attr[i].split('=')
                    LayerGetter.csvFileAttrs.setdefault(elem[0], elem[1])

