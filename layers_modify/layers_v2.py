import csv
import math
from datetime import datetime

from click import edit
from qgis.core import (
    QgsVectorFileWriter,
    QgsProject, QgsFields, QgsField, QgsWkbTypes, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer,
    QgsFeatureRequest, QgsVectorDataProvider,
)
from qgis.PyQt.QtCore import QVariant
import osgeo.ogr as ogr
import osgeo.osr as osr
import os
import sys


# На вход могут подавться различные типы данных, а не только шейпфайлы
# Например, это могут быть временные слои, текстовые файлы и др.
# Плагин должен уметь распознавать эти типы данных и работать с ними
# Сохранение тоже должно выполняться в разные форматы.
# Нужно изменить интерфейс таким образом, чтобы сохранение выполнялось.

def azimutCalc(x1, x2):
    dX = x2[0] - x1[0]
    dY = x2[1] - x1[1]
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


def testAlgorithm():
    global templayer, inDS, outDS
    try:
        inDS = ogr.Open(r'M:\Sourcetree\bpla_plugin_flights\input_data', 0)
        in_lyr = inDS.GetLayer('20200905_(F9-17)wMagnCoord')
        memDriver = ogr.GetDriverByName('MEMORY')
        outDS = memDriver.CreateDataSource('memData')
        tmpDS = memDriver.Open('memData', 1)

        templayer = outDS.CopyLayer(in_lyr, 'temp_layer', ['OVERWRITE=YES'])

    except Exception as err:
        print('\nНе удалось создать временный слой! ' + str(err))

    # далее работаем с временным слоем
    if templayer is not None:
        # print('Временный слой успешно создан!')
        # print('Количество точек во временном слое: ' + str(templayer.GetFeatureCount()))
        # -------- удаляем нулевые точки ---------------
        # print('\nНачинаем удаление нулевых точек...')
        try:
            for i in range(templayer.GetFeatureCount()):
                feat = templayer.GetNextFeature()
                if feat is not None:
                    geom = feat.geometry()
                    if geom.GetX() == 0.0 and geom.GetY() == 0.0:
                        templayer.DeleteFeature(feat.GetFID())
                        # inDS.ExecuteSQL('REPACK ' + templayer.GetName())
                        # print(str(feat.GetField("TIME")))
            templayer.ResetReading()
            # print('Количество точек после удаления нулевых: ' + str(templayer.GetFeatureCount()))
        except Exception as err:
            print('\nНе удалось удалить нулевые точки! ' + str(err))

        outDS.SyncToDisk()

        # ------ основная часть плагина -------------------------
        print('\nНачинаем удаление избыточных точек...')
        try:
            feat_list = []
            for i in range(100):
                feat = templayer.GetNextFeature()
                feat_list.append(feat)
            templayer.ResetReading()

            # отсортируем список по fid
            # feat_list = sorted(feat_list, key=lambda feature: feature.GetFID(), reverse=False)
            feat_list = sorted(feat_list, key=lambda feature: feature.GetField("TIME"), reverse=False)

            accuracy = 10
            partsFlightList = []
            ids_list = []
            i = 0
            while i + 2 < len(feat_list):
                azimut_1 = azimutCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
                                      [feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()])
                azimut_2 = azimutCalc([feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()],
                                      [feat_list[i + 2].geometry().GetX(), feat_list[i + 2].geometry().GetY()])

                print('i= ', i)
                print(str(azimut_1) + ' ' + str(azimut_2))

                if math.fabs(azimut_1 - azimut_2) < accuracy:
                    print('\nYes!')
                    ids_list.append(feat_list[i].GetFID())
                    print(str(ids_list))

                else:
                    print('\nnope')
                    if ids_list is not None:
                        partsFlightList.append(ids_list)
                    ids_list = [feat_list[i].GetFID()]
                    print(str(ids_list))
                i += 1

            if ids_list is not None:
                ids_list.append(feat_list[i].GetFID())
                ids_list.append(feat_list[i + 1].GetFID())
                partsFlightList.append(ids_list)

            # print(str(partsFlightList))

            print('Количество частей полетов: ' + str(len(partsFlightList)))

            longest_list = max(len(elem) for elem in partsFlightList)
            print('Самый длинный полет: ' + str(longest_list))
            shortest_list = min(len(elem) for elem in partsFlightList)
            print('Самый короткий полет: ' + str(shortest_list))

            # анализируем длины полетов и удаляем точки
            for list in partsFlightList:
                if len(list) > longest_list / 10:
                    print(len(list))

            #     if len(list) < longest_list / 10:
            #         for fid in list:
            #             templayer.DeleteFeature(fid)
            #             # inDS.ExecuteSQL('REPACK ' + templayer.GetName())
            # templayer.ResetReading()
            # print('\nКоличество точек в полученном слое: ' + str(templayer.GetFeatureCount()))

        except Exception as err:
            print('\nНе удалось удалить избыточные точки! ' + str(err))

        outDS.SyncToDisk()

        # -------- сохраняем результат в шейпфайл (код рабочий) ----------------------
        # try:
        #     fileDriver = ogr.GetDriverByName('ESRI Shapefile')
        #     fileDS = fileDriver.CreateDataSource(filepath)
        #     tmpDS = fileDriver.Open(filepath, 1)
        #
        #     newlayer = fileDS.CopyLayer(templayer, filename, ['OVERWRITE=YES'])
        #     if newlayer is not None:
        #         uploadLayer(filepath, filename, 'ogr')
        #     del fileDS
        # except Exception as err:
        #     textEdit.setTextColor(QColor(255, 0, 0))
        #     textEdit.setFontWeight(QFont.Bold)
        #     print('\nНе удалось сохранить файл! ' + str(err))

        del inDS, tmpDS, outDS

def txtFilesTest():
    # Parse a delimited text file of volcano data and create a shapefile
    # use a dictionary reader so we can access by field name
    reader = csv.DictReader(open(r'M:\Sourcetree\bpla_plugin_flights\input_data\20200905_(F1-8)wMagnCoord.txt', "rt",
                                 encoding="utf8"),
                            delimiter='\t',
                            quoting=csv.QUOTE_NONE)

    # set up the shapefile driver
    driver = ogr.GetDriverByName('MEMORY')

    # create the data source
    data_source = driver.CreateDataSource('memData')

    # create the spatial reference, WGS84
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # create the layer
    layer = data_source.CreateLayer("temp_layer", srs, ogr.wkbPoint)

    # Add the all fields
    for field in reader.fieldnames:
        layer.CreateField(ogr.FieldDefn(field, ogr.OFTString))
    #
    # Process the text file and add the attributes and features to the shapefile
    for row in reader:
        # create the feature
        feature = ogr.Feature(layer.GetLayerDefn())
        # Set the attributes using the values from the delimited text file
        for item in row.keys():
            feature.SetField(item, row[item])

        # create the WKT for the feature using Python string formatting
        wkt = "POINT(%f %f)" % (float(row['LON']), float(row['LAT']))

        # Create the point from the Well Known Txt
        point = ogr.CreateGeometryFromWkt(wkt)

        # Set the feature geometry using the point
        feature.SetGeometry(point)
        # Create the feature in the layer (shapefile)
        layer.CreateFeature(feature)
        # Dereference the feature
        feature = None

    # feat_list = []
    # for i in range(layer.GetFeatureCount()):
    #     feat = layer.GetNextFeature()
    #     feat_list.append(feat)
    # layer.ResetReading()
    #
    # # отсортируем список по fid
    # # feat_list = sorted(feat_list, key=lambda feature: feature.GetFID(), reverse=False)
    # feat_list = sorted(feat_list, key=lambda feature: feature.GetField("TIME"), reverse=False)
    #
    # for i in feat_list:
    #     print(i.GetField('TIME'))

    # Save and close the data source
    data_source = None

def spatialIndexTest():
    inShapefile = "M:/Sourcetree/bpla_plugin_flights/output/test.shp"
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()

    # # Collect all Geometry
    # geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
    # for feature in inLayer:
    #     geomcol.AddGeometry(feature.GetGeometryRef())
    #
    # # Calculate convex hull
    # convexhull = geomcol.ConvexHull()

    # # Save extent to a new Shapefile
    # outShapefile = "M:/Sourcetree/bpla_plugin_flights/output/states_convexhull.shp"
    # outDriver = ogr.GetDriverByName("ESRI Shapefile")
    #
    # # Remove output shapefile if it already exists
    # if os.path.exists(outShapefile):
    #     outDriver.DeleteDataSource(outShapefile)
    #
    # # Create the output shapefile
    # outDataSource = outDriver.CreateDataSource(outShapefile)
    # outLayer = outDataSource.CreateLayer("states_convexhull", geom_type=ogr.wkbPolygon)
    #
    # # Add an ID field
    # idField = ogr.FieldDefn("id", ogr.OFTInteger)
    # outLayer.CreateField(idField)
    #
    # # Create the feature and set values
    # featureDefn = outLayer.GetLayerDefn()
    # feature = ogr.Feature(featureDefn)
    # feature.SetGeometry(convexhull)
    # feature.SetField("id", 1)
    # outLayer.CreateFeature(feature)
    # feature = None
    #
    # # Save and close DataSource
    # inDataSource = None
    # outDataSource = None

    # wkt = "POLYGON ((143.513377 63.7332))"

    delta = 0.0003732999903149903
    for i in range(20):
        feature = inLayer.GetNextFeature()
        geom = feature.geometry()
        inLayer.SetSpatialFilterRect(geom.GetX(), geom.GetY(),
                                     geom.GetX() + delta, geom.GetY() + delta)
        print(inLayer.GetFeatureCount())
    inLayer.ResetReading()

if __name__ == "__main__":
    # txtFilesTest()

    # cur_lyr_path = 'file:///M:/YandexDisk/QGIS/my_data_source/20200905_(F1-8)wMagnCoord.txt?type=csv&delimiter=%5Ct&detectTypes=yes&xField=LON&yField=LAT&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no'
    # fn = cur_lyr_path.split('?')
    # fn1 = fn[0].split('///')
    # layerpath = fn1[1]
    # # print(fn)
    # attr = fn[1].split('&')
    # # print(attr)
    # attr_dict = {}
    # for i in range(len(attr)):
    #     elem = attr[i].split('=')
    #     attr_dict.setdefault(elem[0], elem[1])
    # print(attr_dict)
    # espg = attr_dict.get('crs').split(':')
    # print(int(espg[1]))

    # spatialIndexTest()

    # x1 = [143.51339611917475736, 63.73329049174756733]
    # x2 = [143.51339625752427764, 63.73329047524271829]
    # dX = x2[0] - x1[0]
    # dY = x2[1] - x1[1]
    # dist = math.sqrt((dX * dX) + (dY * dY))
    # print(dist)

    # a1 = [0, 1, 2]
    # a2 = [3, 4, 5, 6]
    # a3 = [7, 8, 9, 10, 11, 12]
    # A = [a1, a2, a3]
    # print(A)
    # for i in range(len(A)):
    #     if i+1 < len(A):
    #         if len(A[i]) < len(A[i + 1]):
    #             A[i].extend(A[i+1])
    #             A.remove(A[i+1])
    # print(A)

    a = 5
    b = 10
    if a in range(0, 10):
        print(a)
