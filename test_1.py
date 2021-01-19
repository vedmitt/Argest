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
  QgsVectorLayerUtils
)

from qgis.core.additions.edit import edit

from qgis.PyQt.QtGui import (
    QColor,
)

from qgis.utils import iface
from PyQt5.QtCore import *

# Supply the path to the qgis install location
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.10", True)
# Create a reference to the QgsApplication.
# Setting the second argument to True enables the GUI. We need
# this since this is a custom application.
qgs = QgsApplication([], True)
# load providers
qgs.initQgis()
# Write your code here to load some layers, use processing
# algorithms, etc.

# If you are not inside a QGIS console you first need to import
# qgis and PyQt classes you will use in this script as shown below:
from qgis.core import QgsProject
# Get the project instance
project = QgsProject.instance()
# Print the current project file name (might be empty in case no projects have been loaded)
print(project.fileName())
# Load another project
project.read(r'M:\YandexDisk\QGIS\Home_projects\all_flights_project.qgz')
print(project.fileName())

# get the path to the shapefile e.g. /home/project/data/ports.shp
# path_to_osgeo_layer = r'M:\YandexDisk\QGIS\osgeopy\osgeopy-data\global\ne_50m_populated_places.shp'

# # The format is:
# # vlayer = QgsVectorLayer(data_source, layer_name, provider_name)

# vlayer = QgsVectorLayer(path_to_osgeo_layer, "new_layer", "ogr")
# if not vlayer.isValid():
#     print("Layer failed to load!")
# else:
#     QgsProject.instance().addMapLayer(vlayer)

# print(vlayer.displayField())

# for field in vlayer.fields():
#     print(field.name(), field.typeName())

# "layer" is a QgsVectorLayer instance
layer = iface.activeLayer()
features = layer.getFeatures()

for feature in features:
    # retrieve every feature with its geometry and attributes
    print("Feature ID: ", feature.id())
    # fetch geometry
    # show some information about the feature geometry
    geom = feature.geometry()
    geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
    if geom.type() == QgsWkbTypes.PointGeometry:
        # the geometry type can be of single or multi type
        if geomSingleType:
            x = geom.asPoint()
            print("Point: ", x)
        else:
            x = geom.asMultiPoint()
            print("MultiPoint: ", x)
    elif geom.type() == QgsWkbTypes.LineGeometry:
        if geomSingleType:
            x = geom.asPolyline()
            print("Line: ", x, "length: ", geom.length())
        else:
            x = geom.asMultiPolyline()
            print("MultiLine: ", x, "length: ", geom.length())
    elif geom.type() == QgsWkbTypes.PolygonGeometry:
        if geomSingleType:
            x = geom.asPolygon()
            print("Polygon: ", x, "Area: ", geom.area())
        else:
            x = geom.asMultiPolygon()
            print("MultiPolygon: ", x, "Area: ", geom.area())
    else:
        print("Unknown or invalid geometry")
    # fetch attributes
    attrs = feature.attributes()
    # attrs is a list. It contains all the attribute values of this feature
    print(attrs)
    # for this test only print the first feature
    break

# Save the project to the same
project.write()
# ... or to a new file
# project.write(r'M:\YandexDisk\QGIS\Home_projects\test_project_1.qgs')


# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
qgs.exitQgis()




