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

import features_editing as broker

def createFileDirectlyFromFeatures(): ## QgsVectorFileWriter has no attribute create
    # define fields for feature attributes. A QgsFields object is needed
    fields = QgsFields()
    fields.append(QgsField("first", QVariant.Int))
    fields.append(QgsField("second", QVariant.String))

    """ create an instance of vector file writer, which will create the vector file.
    Arguments:
    1. path to new file (will fail if exists already)
    2. field map
    3. geometry type - from WKBTYPE enum
    4. layer's spatial reference (instance of
       QgsCoordinateReferenceSystem)
    5. coordinate transform context
    6. save options (driver name for the output file, encoding etc.)
    """

    crs = QgsProject.instance().crs()
    transform_context = QgsProject.instance().transformContext()
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "ESRI Shapefile"
    save_options.fileEncoding = "UTF-8"

    writer = QgsVectorFileWriter.create(
        "testdata/my_new_shapefile.shp",
        fields,
        QgsWkbTypes.Point,
        crs,
        transform_context,
        save_options
    )

    if writer.hasError() != QgsVectorFileWriter.NoError:
        print("Error when creating shapefile: ", writer.errorMessage())

    # add a feature
    fet = QgsFeature()

    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 10)))
    fet.setAttributes([1, "text"])
    writer.addFeature(fet)

    # delete the writer to flush features to disk
    del writer

def saveLayerToFile(layer, filepath): ## QgsVectorFileWriter  has no attriburte writeAsVectorFormatV2
    # Write to an ESRI Shapefile format dataset using UTF-8 text encoding
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "ESRI Shapefile"
    save_options.fileEncoding = "UTF-8"
    transform_context = QgsProject.instance().transformContext()
    # error = QgsVectorFileWriter.writeAsVectorFormatV2(layer,
    #                                                   "testdata/my_new_shapefile",
    #                                                   transform_context,
    #                                                   save_options)
    i = 0
    for f in layer:
        print(f['NAME'])
        i += 1
    print('Features to save', i)

    # error = QgsVectorFileWriter.writeAsVectorFormat(layer, filepath,
    #                                                 "CP1250", 'EPSG:27700',  ##layer.crs(),
    #                                                 "ESRI Shapefile")
    # # writer = QgsVectorFileWriter(fn, 'UTF-8', layerFields, QgsWkbTypes.Point, \
    # #                              QgsCoordinateReferenceSystem('EPSG:26912'), 'ESRI Shapefile')
    # if error[0] == QgsVectorFileWriter.NoError:
    #     print("Successfully saved!")
    # else:
    #     print(error)

    def listToShapefile(self):
        # # Write to an ESRI Shapefile format dataset using UTF-8 text encoding
        # save_options = QgsVectorFileWriter.SaveVectorOptions()
        # save_options.driverName = "ESRI Shapefile"
        # save_options.fileEncoding = "UTF-8"
        # transform_context = QgsProject.instance().transformContext()
        #
        # error = QgsVectorFileWriter.writeAsVectorFormat(self.layer, self.filename,
        #                                                 "CP1250", self.layer.crs(),
        #                                                 "ESRI Shapefile")
        #
        # if error[0] == QgsVectorFileWriter.NoError:
        #     iface.messageBar().pushMessage("Successfully saved!", level=0)
        #     # # uploading new file to the map
        #     # layer = iface.addVectorLayer(r"M:\Sourcetree\bpla_plugin_flights\output\test1.shp", "new_layer", "ogr")
        #     filepath = self.filename + '.shp'
        #     # iface.messageBar().pushMessage(filepath, level=0)
        #     layer = iface.addVectorLayer(filepath, "new_layer", "ogr")
        #     if not layer:
        #         iface.messageBar().pushMessage("Layer failed to load!", level=0)
        # else:
        #     iface.messageBar().pushMessage("Something went wrong... ", error,  level=0)
        pass

def createFromMemoryProvider():
    # create layer
    vl = QgsVectorLayer("Point", "temporary_points", "memory")
    pr = vl.dataProvider()

    # add fields
    pr.addAttributes([QgsField("name", QVariant.String),
                      QgsField("age", QVariant.Int),
                      QgsField("size", QVariant.Double)])
    vl.updateFields()  # tell the vector layer to fetch changes from the provider

    # add a feature
    fet = QgsFeature()
    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 10)))
    fet.setAttributes(["Johny", 2, 0.3])
    pr.addFeatures([fet])

    # update layer's extent when new features have been added
    # because change of extent in provider is not propagated to the layer
    vl.updateExtents()

    # show some stats
    print("fields:", len(pr.fields()))
    print("features:", pr.featureCount())
    e = vl.extent()
    print("extent:", e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum())

    # iterate over features
    features = vl.getFeatures()
    for fet in features:
        print("F:", fet.id(), fet.attributes(), fet.geometry().asPoint())

def createTempLayer(inShapefile, layername):
    # open an input datasource
    indriver = ogr.GetDriverByName('ESRI shapefile')
    srcdb = indriver.Open(inShapefile, 0)

    # create an output datasource in memory
    outdriver = ogr.GetDriverByName('MEMORY')
    source = outdriver.CreateDataSource('memData')

    # open the memory datasource with write access
    tmp = outdriver.Open('memData', 1)

    # copy a layer to memory
    pipes_mem = source.CopyLayer(srcdb.GetLayer(layername), 'temp_layer', ['OVERWRITE=YES'])

    # the new layer can be directly accessed via the handle pipes_mem or as source.GetLayer('temp_layer'):
    layer = source.GetLayer('temp_layer')

    # for feature in layer:
    #     print(feature['NAME'])
    #     # feature.SetField('SOMETHING', 1)
    # layer.ResetReading()
    del indriver, srcdb, outdriver, source


def getListFeatures(inShapefile, layername):
    srcdb = ogr.Open(inShapefile, 1)
    layer = srcdb.GetLayer()

    # create a list with features
    listFeat = []
    for f in layer:
        listFeat.append(f)

    listFeat.sort(key=lambda val: val['LON'] == 0.0, reverse=True)
    for i in listFeat:
        # print(i['TIME'], i['LON'], i['LAT'])
        if i['LON'] == 0.0 and i['LAT'] == 0.0:
            # self.textEdit.append('first zero point!')
            listFeat.remove(i)

    for i in listFeat:
        print(i['TIME'], i['LON'], i['LAT'])
    print('List items count: ', len(listFeat))
    return listFeat


def createNewLayerFromOldDefinitions(inShapefile, outShapefile):
    # inds = ogr.Open(inShapefile)
    # inlyr = inds.GetLayer()
    # # inlyr.SetAttributeFilter('name = "hello"')
    # drv = ogr.GetDriverByName('ESRI Shapefile')
    # outds = drv.CreateDataSource(outShapefile)
    # outlyr = outds.CopyLayer(inlyr, 'test2')
    # del inlyr, inds, outlyr, outds

    # Open the folder data source for writing
    inds = ogr.Open(inShapefile, 1)
    if inds is None:
        sys.exit('Could not open folder.')

    # Get the input shapefile
    in_lyr = inds.GetLayer()

    # # create a list with features
    # listFeat = []
    # for f in in_lyr:
    #     listFeat.append(f)
    # # for i in listFeat:
    # #     print(i['name'])
    # print('List items count: ', len(listFeat))

    # inlyr.SetAttributeFilter('name = "hello"')
    # Create a point layer
    drv = ogr.GetDriverByName('ESRI Shapefile')
    outds = drv.CreateDataSource(outShapefile)

    # if outds.GetLayer('capital_cities'):
    #     outds.DeleteLayer('capital_cities')
    out_lyr = outds.CreateLayer('capital_cities',
                             in_lyr.GetSpatialRef(),
                             ogr.wkbPoint)
    # out_lyr = QgsVectorLayer(r'M:\YandexDisk\QGIS\temp\newpoints5.shp', 'capital_cities', 'ogr')
    out_lyr.CreateFields(in_lyr.schema)  # get old fields schema

    # Create a blank feature
    out_defn = out_lyr.GetLayerDefn()
    out_feat = ogr.Feature(out_defn)

    for in_feat in listFeat:
        # if feat.GetField('FEATURECLA') == 'Admin-0 capital':

        # Copy geometry and attributes
        geom = in_feat.geometry()
        out_feat.SetGeometry(geom)
        # out_feat.
        for i in range(in_feat.GetFieldCount()):
            value = in_feat.GetField(i)
            out_feat.SetField(i, value)

        # Insert the feature
        out_lyr.CreateFeature(out_feat)

    i = 0
    for f in out_lyr:
        # print(f['NAME'])
        i += 1
    print('Features in layer', i)
    out_lyr.ResetReading()

    # out_lyr = outds.CopyLayer(in_lyr, 'test2')
    del in_lyr, inds, out_lyr, outds


def saveConvexhullOfAllGeometryToOutputLayer(inShapefile, outShapefile):
    # Get a Layer
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()

    # Collect all Geometry
    geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
    for feature in inLayer:
        geomcol.AddGeometry(feature.GetGeometryRef())

    # Calculate convex hull
    convexhull = geomcol.ConvexHull()

    # Save extent to a new Shapefile
    outDriver = ogr.GetDriverByName("ESRI Shapefile")

    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("states_convexhull", geom_type=ogr.wkbPolygon)

    # Add an ID field
    idField = ogr.FieldDefn("id", ogr.OFTInteger)
    outLayer.CreateField(idField)

    # Create the feature and set values
    featureDefn = outLayer.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(convexhull)
    feature.SetField("id", 1)
    outLayer.CreateFeature(feature)
    feature = None

    # Save and close DataSource
    inDataSource = None
    outDataSource = None

def timeLoop():
    vlayer = QgsVectorLayer(r'M:\Sourcetree\bpla_plugin_flights\output\test1.shp', 'test1', 'ogr')
    limit = 12
    # create new field with no content
    pr = vlayer.dataProvider()
    caps = pr.capabilities()

    if caps & QgsVectorDataProvider.AddAttributes:
        new_field = [QgsField("FLIGHT_NUM", QVariant.Int)]
        if (new_field not in vlayer.fields()) and vlayer.fields().count() == 7:
            pr.addAttributes(new_field)
            vlayer.updateFields()

    request = QgsFeatureRequest()
    request.setLimit(limit)

    i = 1
    boolYesNo = False
    prevFeat = None
    nextFeat = None

    for feat in vlayer.getFeatures(request):
        if feat.id() == 0:
            prevFeat = feat
        elif feat.id() == 1:
            nextFeat = feat
            boolYesNo = timeSort(prevFeat, nextFeat)
        else:
            prevFeat = nextFeat
            nextFeat = feat
            boolYesNo = timeSort(prevFeat, nextFeat)

        print(boolYesNo)
        if (boolYesNo is False) and (nextFeat is not None):
            print(i)
            # add new flight number
            if caps & QgsVectorDataProvider.ChangeAttributeValues:
                attrs = {7: i}
                pr.changeAttributeValues({prevFeat.id(): attrs})
                pr.changeAttributeValues({nextFeat.id(): attrs})
                vlayer.updateFields()
        elif nextFeat is not None:
            i += 1
            print(i)
            # add new flight number
            if caps & QgsVectorDataProvider.ChangeAttributeValues:
                attrs = {7: i}
                pr.changeAttributeValues({nextFeat.id(): attrs})
                vlayer.updateFields()

    broker.iterFeatures(vlayer, limit)


def timeSort(prevFeat, nextFeat):
    data_format = '%m-%d-%YT%H:%M:%S,%f'

    prevDataTime = datetime.strptime(prevFeat['TIME'], data_format)
    nextDataTime = datetime.strptime(nextFeat['TIME'], data_format)

    print('Date:', prevDataTime.date())
    print('Time:', prevDataTime.time())

    print('Date:', nextDataTime.date())
    print('Time:', nextDataTime.time())

    if nextDataTime.date() != prevDataTime.date():
        return True
    elif (nextDataTime.time().second - prevDataTime.time().second) > 1:
        return True
    else:
        return False


def azimutCalc(x1, x2):
    dX = x2[0]-x1[0]
    dY = x2[1]-x1[1]
    dist = math.sqrt((dX * dX) + (dY * dY))
    dXa = math.fabs(dX)
    if dist != 0:
        beta = math.degrees(math.acos(dXa / dist))
        if (dX > 0):
            if (dY < 0):
                angle = 270 + beta
            else:
                angle = 270 - beta
        else:
            if (dY < 0):
                angle = 90 - beta
            else:
                angle = 90 + beta
        return angle
    else:
        return 0


def delFeatures(layer, delFeatIDs):
    caps = layer.dataProvider().capabilities()
    if caps & QgsVectorDataProvider.DeleteFeatures:
        res = layer.dataProvider().deleteFeatures(delFeatIDs)
        # layer.updateFields()
        # print(res)


def removePointsFromAzimut(layer, prevFeat, nextFeat, azimut, delFeatIDs):
    angle = azimutCalc([prevFeat['LON'], prevFeat['LAT']], [nextFeat['LON'], nextFeat['LAT']])
    accuracy = 5

    # print(angle)
    # print(azimut)

    # print(math.fabs(angle - azimut))
    # print(math.fabs(angle - (azimut + 180)))

    if (math.fabs(angle - azimut) < accuracy) or (math.fabs(angle - (azimut + 180)) < accuracy):
        # print(prevFeat.id(), prevFeat['FLIGHT_NUM'], prevFeat['LON'], prevFeat['LAT'])
        # print(math.fabs(angle - azimut))
        # print(math.fabs(angle - (azimut + 180)))
        # print('Nope!')
        pass
    else:
        # remove points
        # print(prevFeat.id(), prevFeat['FLIGHT_NUM'], prevFeat['LON'], prevFeat['LAT'])
        delFeatIDs.append(prevFeat.id())

    return delFeatIDs

def fromLayerGetAzimut(max_flnum, azimut):
    vlayer = QgsVectorLayer(r'M:\Sourcetree\bpla_plugin_flights\output\test2.shp', 'test2', 'ogr')

    request = QgsFeatureRequest()
    # request.setLimit(10)

    prevFeat = None
    nextFeat = None
    delFeatIDs = []
    for feat in vlayer.getFeatures(request):
        if feat.id() == 0:
            prevFeat = feat
        elif feat.id() == 1:
            nextFeat = feat
            delFeatIDs = removePointsFromAzimut(vlayer, prevFeat, nextFeat, azimut, delFeatIDs)
        else:
            prevFeat = nextFeat
            nextFeat = feat
            delFeatIDs = removePointsFromAzimut(vlayer, prevFeat, nextFeat, azimut, delFeatIDs)

    # print(delFeatIDs)
    delFeatures(vlayer, delFeatIDs)

    # for feat in vlayer.getFeatures(request):
    #     print(feat.id(), feat['FLIGHT_NUM'], feat['LON'], feat['LAT'])



if __name__ == "__main__":
    # vlayer = QgsVectorLayer(r'M:\YandexDisk\QGIS\osgeopy\osgeopy-data\global\ne_50m_populated_places.shp', 'capital_cities', 'ogr')
    # vlayer = QgsVectorLayer(r'M:\YandexDisk\QGIS\temp\newpoints.shp', 'degree_days', 'ogr')
    # for field in vlayer.fields():
    #     print(field.name(), field.typeName())

    # createFileDirectlyFromFeatures()
    # saveLayerToFile(vlayer)
    # createFromMemoryProvider()

    # inShapefile = r'M:\YandexDisk\QGIS\osgeopy\osgeopy-data\global\ne_50m_populated_places.shp'
    # inShapefile = r'M:\YandexDisk\QGIS\temp\newpoints.shp'
    inShapefile = r'M:\Sourcetree\bpla_plugin_flights\input_data\20200905_(F9-17)wMagnCoord.shp'
    # layername = '20200905_(F18-24)wMagnCoord'
    # outShapefile = r'M:\YandexDisk\QGIS\temp\states_convexhull.shp'
    outShapefile = r'M:\YandexDisk\QGIS\temp\test1.shp'

    # saveConvexhullOfAllGeometryToOutputLayer(inShapefile, outShapefile)
    # newTest()
    # createTempLayer(inShapefile, '20200905_(F9-17)wMagnCoord')
    # createNewLayerFromOldDefinitions(inShapefile, outShapefile)

    # list = getListFeatures(inShapefile, '20200905_(F9-17)wMagnCoord.shp')

    # timeLoop()
    fromLayerGetAzimut(4, 90)

    pass


