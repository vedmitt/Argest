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
  QgsVectorLayerUtils
)
from qgis.core.additions.edit import edit
from qgis.utils import iface
from qgis.PyQt.QtGui import (
    QColor,
)
from qgis.PyQt.QtCore import QVariant
import os
os.environ['GDAL_DATA'] = 'C:\Program Files\QGIS 3.10\share\gdal'
os.environ['PROJ_LIB'] = 'C:\Program Files\QGIS 3.10\share\proj'

def addRemoveFields(layer):
    caps = layer.dataProvider().capabilities()

    # if caps & QgsVectorDataProvider.AddAttributes:
    #     res = layer.dataProvider().addAttributes(
    #         [QgsField("newField", QVariant.String), # adding NULL every time :(
    #          QgsField("myint", QVariant.Int)])

    if caps & QgsVectorDataProvider.DeleteAttributes:
        res = layer.dataProvider().deleteAttributes([2])

    # # Alternate methods for removing fields
    # # first create temporary fields to be removed (f1-3)
    # layer.dataProvider().addAttributes(
    #     [QgsField("f1", QVariant.Int), QgsField("f2", QVariant.Int), QgsField("f3", QVariant.Int)])
    # layer.updateFields()
    # count = layer.fields().count()  # count of layer fields
    # ind_list = list((count - 3, count - 2))  # create list
    #
    # # remove a single field with an index
    # layer.dataProvider().deleteAttributes([count - 1])
    #
    # # remove multiple fields with a list of indices
    # layer.dataProvider().deleteAttributes(ind_list)

    layer.updateFields() # compulsory!

def addFeatures(layer):
    caps = layer.dataProvider().capabilities()
    # # Check if a particular capability is supported:
    # if caps & QgsVectorDataProvider.DeleteFeatures:
    #     print('The layer supports DeleteFeatures')

    # caps_string = layer.dataProvider().capabilitiesString()
    # Print:
    # 'Add Features, Delete Features, Change Attribute Values, Add Attributes,
    # Delete Attributes, Rename Attributes, Fast Access to Features at ID,
    # Presimplify Geometries, Presimplify Geometries with Validity Check,
    # Transactions, Curved Geometries'

    # If caching is enabled, a simple canvas refresh might not be sufficient
    # to trigger a redraw and you must clear the cached image for the layer
    # if iface.mapCanvas().isCachingEnabled():
    #     layer.triggerRepaint()
    # else:
    #     iface.mapCanvas().refresh()
    ## add features
    if caps & QgsVectorDataProvider.AddFeatures:
        feat = QgsFeature(layer.fields())
        # feat.setAttributes([0, 'hello'])
        # # Or set a single attribute by key or by index:
        feat.setAttribute('name', 'hello')
        feat.setAttribute('value', random.uniform(0.1, 1.9))
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(123, 456)))
        (res, outFeats) = layer.dataProvider().addFeatures([feat])

def modifyFeatures(layer):
    caps = layer.dataProvider().capabilities()
    fid = 10  # ID of the feature we will modify
    # The following example first changes values of attributes with index 0 and 1, then it changes the feature’s geometry.
    if caps & QgsVectorDataProvider.ChangeAttributeValues:
        attrs = {0: "hello", 1: 123}
        layer.dataProvider().changeAttributeValues({fid: attrs})

    if caps & QgsVectorDataProvider.ChangeGeometries:
        geom = QgsGeometry.fromPointXY(QgsPointXY(111, 222))
        layer.dataProvider().changeGeometryValues({fid: geom})

def modifyLayersEditingBuffer(layer): # not working?
    # layer.beginEditCommand("Feature triangulation")
    feat1 = feat2 = QgsFeature(layer.fields())
    fid = 9
    feat1.setId(fid)

    # add two features (QgsFeature instances)
    layer.addFeatures([feat1, feat2])
    # delete a feature with specified ID
    layer.deleteFeature(fid)

    # set new geometry (QgsGeometry instance) for a feature
    geometry = QgsGeometry.fromWkt("POINT(7 45)")
    layer.changeGeometry(fid, geometry)
    # update an attribute with given field index (int) to a given value
    fieldIndex = 2
    value = 'My new name'
    layer.changeAttributeValue(fid, fieldIndex, value)

    # add new field
    layer.addAttribute(QgsField("mytext", QVariant.String))
    # remove a field
    layer.deleteAttribute(fieldIndex)

    # if problem_occurred:
    #     layer.destroyEditCommand()
    #     # ... tell the user that there was a problem
    #     # and return

    # ... more editing ...
    # layer.endEditCommand()

    with edit(layer):
        feat = next(layer.getFeatures())
        feat[0] = 5
        layer.updateFeature(feat)

def deleteFeatures(layer):
    caps = layer.dataProvider().capabilities()
    if caps & QgsVectorDataProvider.DeleteFeatures:
        res = layer.dataProvider().deleteFeatures([10, 12])

def requestFeature(layer):
    # areaOfInterest = QgsRectangle(450290, 400520, 450750, 400780)
    # request = QgsFeatureRequest().setFilterRect(areaOfInterest)
    # for feature in layer.getFeatures(request):
    #     # do whatever you need with the feature
    #     print(feature['name'])
    #     pass

    # The expression will filter the features where the field "location_name"
    # contains the word "Lake" (case insensitive)
    exp = QgsExpression('name ILIKE \'%name%\'')
    request = QgsFeatureRequest(exp)
    # request = QgsFeatureRequest()
    request.setLimit(2)
    for feature in layer.getFeatures(request):
        print(feature, feature['name'])

def selectFeatures(layer):
    # Get the active layer (must be a vector layer)
    # layer = iface.activeLayer()
    layer.selectAll()
    # layer.selectByExpression('"Class"=\'B52\' and "Heading" > 10 and "Heading" <70', QgsVectorLayer.SetSelection)

    selected_fid = []
    # Get the first feature id from the layer
    for feature in layer.getFeatures():
        selected_fid.append(feature.id())
        break
    # Add these features to the selected list
    print(selected_fid)
    layer.select(selected_fid)

    ## iterating over selected features
    selection = layer.selectedFeatures()
    for feature in selection:
        # do whatever you need with the feature
        print(feature['name'], feature['id'])
        pass

def iterFeatures(layer):
    # "layer" is a QgsVectorLayer instance
    # layer = iface.activeLayer()
    features = layer.getFeatures()
    # num_features = layer.GetFeatureCount()
    # print('\n All features amount: {0}'.format(num_features))

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
        # break

def vectorLayerUtilsMethods(layer):
    # The QgsVectorLayerUtils class contains some very useful methods that you can use with vector layers.
    # For example the createFeature() method prepares a QgsFeature to be added to a vector layer keeping
    # all the eventual constraints and default values of each field:

    feat = QgsVectorLayerUtils.createFeature(layer)
    # select only the first feature to make the output shorter
    vlayer.selectByIds([1])
    val = QgsVectorLayerUtils.getValues(vlayer, "NAME", selectedOnly=True)
    print('\n', val)

if __name__ == "__main__":
    # vlayer = QgsVectorLayer(r'M:\YandexDisk\QGIS\osgeopy\osgeopy-data\global\ne_50m_populated_places.shp', 'capital_cities', 'ogr')
    vlayer = QgsVectorLayer(r'M:\YandexDisk\QGIS\temp\newpoints.shp', 'degree_days', 'ogr')
    # for field in vlayer.fields():
    #     print(field.name(), field.typeName())
        ## or
    # print(vlayer.displayField())

    # requestFeature(vlayer)
    # addFeatures(vlayer)
    # modifyFeatures(vlayer)
    # modifyLayersEditingBuffer(vlayer)
    # deleteFeatures(vlayer)
    # addRemoveFields(vlayer)
    # iterFeatures(vlayer)
    # vectorLayerUtilsMethods(vlayer)
    # selectFeatures(vlayer)
    pass

