from qgis._core import QgsVectorLayer

global actVecLyrDict, layer


class LayerGetter:
    actVecLyrDict = {}
    layer = None
    layername = None
    layerpath = None
    drivername = None
    csvFileAttrs = {}

    def __init__(self):
        # self.actVecLyrDict = {}
        pass


def getActiveLayers(canvas):
    layers = canvas.layers()  # по умолчанию только видимые слои
    for item in layers:
        if ((type(item) == QgsVectorLayer) and (item.geometryType() == 0)):
            # setdefault добавляет элементы с проверкой на повторяющиеся
            # если у пользователя два слоя с одиноковыми именами, в комбобокс попадет только один из них
            LayerGetter.actVecLyrDict.setdefault(item.name(), item)
    return LayerGetter.actVecLyrDict


def getLayer(layerstr):
    LayerGetter.layer = actVecLyrDict.get(layerstr)

    if layer is not None:
        LayerGetter.layername = layer.name()
        LayerGetter.driverName = layer.dataProvider().storageType()
        cur_lyr_path = layer.dataProvider().dataSourceUri()

        if LayerGetter.driverName == 'ESRI Shapefile':
            char_arr = cur_lyr_path.split('|')
            LayerGetter.layerpath = char_arr[0]

        elif LayerGetter.driverName == 'Delimited text file':
            fn = cur_lyr_path.split('?')
            fn1 = fn[0].split('///')
            LayerGetter.layerpath = fn1[1]
            attr = fn[1].split('&')
            csvFileAttrs = {}
            for i in range(len(attr)):
                elem = attr[i].split('=')
                csvFileAttrs.setdefault(elem[0], elem[1])
    return [LayerGetter.driverName, LayerGetter.layername, LayerGetter.layerpath, LayerGetter.csvFileAttrs]
