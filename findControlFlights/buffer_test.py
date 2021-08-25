from qgis.utils import iface
from qgis._core import QgsProject, QgsVectorFileWriter, QgsWkbTypes, QgsGeometry

#layerName = 'karelia_2'
#layerName = 'test4'
#outFn = '/Users/ronya/My_Documents/karelia/karelia_results/Buffered.shp'

layerName = 'Darhan_GK20_metric1'
outFn = '/Users/ronya/My_Documents/Darhan/controls/Buffered.shp'
bufferDist = 10

layers = QgsProject.instance().mapLayersByName(layerName)
layer = layers[0]
fields = layer.fields()
feats = layer.getFeatures()

writer = QgsVectorFileWriter(outFn, 'UTF-8', fields, QgsWkbTypes.Polygon, layer.sourceCrs(), 'ESRI Shapefile')

for feat in feats:
    geom = feat.geometry()
    buff = geom.buffer(bufferDist, 5, QgsGeometry.CapRound, QgsGeometry.JoinStyleRound, 2.0)
    feat.setGeometry(buff)
    writer.addFeature(feat)

iface.addVectorLayer(outFn, '', 'ogr')
del(writer)