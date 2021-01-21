from numpy import random
from qgis.core import (
  QgsApplication,
  QgsDataSourceUri,
  QgsCategorizedSymbolRenderer,
  QgsClassificationRange,
  QgsPointXY,
  QgsProject,
  QgsExpression,
  QgsField,
  QgsFields,
  QgsFeature,
  QgsFeatureRequest,
  QgsFeatureRenderer,
  QgsGeometry,
  QgsGraduatedSymbolRenderer,
  QgsMarkerSymbol,
  QgsMessageLog,
  QgsRectangle,
  QgsRendererCategory,
  QgsRendererRange,
  QgsSymbol,
  QgsVectorDataProvider,
  QgsVectorLayer,
  QgsVectorFileWriter,
  QgsWkbTypes,
  QgsSpatialIndex,
  QgsVectorLayerUtils,
  QgsCoordinateReferenceSystem
)

from qgis.core.additions.edit import edit

from qgis.PyQt.QtGui import (
    QColor,
)

from qgis.utils import iface
from PyQt5.QtCore import *

fn = r'M:\YandexDisk\QGIS\temp\newpoints.shp'
# fn = r'D:\\veron\\YandexDisk\\QGIS\\temp\\newpoints.shp'

import os
os.environ['GDAL_DATA'] = 'C:\Program Files\QGIS 3.10\share\gdal'
os.environ['PROJ_LIB'] = 'C:\Program Files\QGIS 3.10\share\proj'

def createNewLayer():
    layerFields = QgsFields()
    layerFields.append(QgsField('id', QVariant.Int))
    layerFields.append(QgsField('value', QVariant.Double))
    layerFields.append(QgsField('name', QVariant.String))

    writer = QgsVectorFileWriter(fn, 'UTF-8', layerFields, QgsWkbTypes.Point,\
        QgsCoordinateReferenceSystem('EPSG:26912'), 'ESRI Shapefile')

    for i in range(10):
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(455618, 4632221)))
        feat.setAttributes([i, random.uniform(0.1, 1.9), 'name'+str(i)])
        writer.addFeature(feat)


    # import layer
    layer = QgsVectorLayer(fn, 'degree_days', 'ogr')
    # # test
    if not layer.isValid():
        print("Layer failed to load!")
    else:
        print("Layer was loaded successfully!")
        iface.addVectorLayer(layer)

    del(writer)

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
# qgs.exitQgis()
