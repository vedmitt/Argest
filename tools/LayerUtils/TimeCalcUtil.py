import math
import os
from datetime import datetime

import ogr

from .AzCalcTool import AzCalcTool
from .AzimutMathUtil import AzimutMathUtil


class TimeCalcUtil:
    guiUtil = None

    def __init__(self, guiUtil):
        TimeCalcUtil.guiUtil = guiUtil

    def setFlightNumber(self, dataSource, layer):
        TimeCalcUtil.guiUtil.setTextEditStyle('black', 'normal', 'Начинаем нумерацию профилей...')

        # # Collect all Geometry
        # geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
        # for feature in layer:
        #     geomcol.AddGeometry(feature.GetGeometryRef())
        #
        # # Calculate convex hull (polygon)
        # convexhull = geomcol.ConvexHull()


        # # находим крайние точки слоя
        extent = layer.GetExtent()
        # # Create a Polygon from the extent tuple
        # ring = ogr.Geometry(ogr.wkbLinearRing)
        # ring.AddPoint(extent[0], extent[2])
        # ring.AddPoint(extent[1], extent[2])
        # ring.AddPoint(extent[1], extent[3])
        # ring.AddPoint(extent[0], extent[3])
        # ring.AddPoint(extent[0], extent[2])
        # poly = ogr.Geometry(ogr.wkbPolygon)
        # poly.AddGeometry(ring)

        # layer.SetSpatialFilterRect(143.46374420000938699, 63.73680240000010144, 143.46371380001073703, 63.73723679999989145)  # x1 y1 x2 y2
        # layer.SetSpatialFilter(143.46202220000850502, 63.7376846499992098, 143.46197729999403236, 63.73768420000124024)  # x1 y1 x2 y2

        # layer.SetSpatialFilterRect(extent[0], extent[2], extent[1], extent[3])  # x1 y1 x2 y2
        # TimeCalcUtil.guiUtil.textEdit.append(str(extent[0]))
        # TimeCalcUtil.guiUtil.textEdit.append(str(extent[1]))
        # TimeCalcUtil.guiUtil.textEdit.append(str(extent[2]))
        # TimeCalcUtil.guiUtil.textEdit.append(str(extent[3]))
        # for feature in layer:
        #     AzCalcTool(dataSource, layer, None).delFeatByID(feature.GetFID())

        # # # Save extent to a new Shapefile
        # outShapefile = r"M:/Sourcetree/output/states_convexhull.shp"
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

        # создаем новый столбец
        newField = 'FLIGHT_NUM'
        fieldDefn = ogr.FieldDefn(newField, ogr.OFTInteger)
        layer.CreateField(fieldDefn)

        # Переводим все фичи в список, сортируем по времени
        az = AzCalcTool(dataSource, layer, None)
        feat_list = az.tempLayerToListFeat(layer)
        feat_list = az.sortListByLambda(feat_list, 'TIME')

        # Находим самую верхнююю левую точку и начинаем с нее
        flight_num = 1

        # ищем первый путь и помечаем его
        first_path = self.findThePath(layer, newField, feat_list, flight_num, extent, 0.0003)
        prev_path = first_path

        # Ищем второй и последующие пути
        flight_num = 2
        while flight_num < 15:
            the_path = self.findThePath(layer, newField, feat_list, flight_num, prev_path, 0.0006)
            prev_path.extend(the_path)
            flight_num += 1


        # # Добавляем номера профилей
        # while i+1 < len(feat_list):
        #     boolYesNo = self.timeSort(feat_list[i], feat_list[i+1])
        #     dist = AzimutMathUtil().distanceCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
        #                                          [feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()])
        #
        #     # if (boolYesNo is False) and (feat_list[i+1] is not None):
        #     if dist > 0.0003 and boolYesNo is False:
        #         # добавить номер профиля (новый)
        #         flight_num += 1
        #         feat_list[i + 1].SetField(newField, flight_num)
        #         layer.SetFeature(feat_list[i + 1])
        #     else:
        #         # добавить номер профиля
        #         feat_list[i].SetField(newField, flight_num)
        #         feat_list[i + 1].SetField(newField, flight_num)
        #         layer.SetFeature(feat_list[i])
        #         layer.SetFeature(feat_list[i + 1])
        #     i += 1
        #
        dataSource.SyncToDisk()
        TimeCalcUtil.guiUtil.setTextEditStyle('black', 'normal', 'Профилей выделено: ' + str(flight_num))
        TimeCalcUtil.guiUtil.setTextEditStyle('green', 'bold', 'Нумерация профилей завершена!')

    def findThePath(self, layer, newField, feat_list, flight_num, prev_path, radius):
        the_path = []
        if len(prev_path) < 5:
            # this is the first path
            valueY = prev_path[3]
        else:
            valueY = prev_path[0].geometry().GetY()

        for i in range(len(feat_list)):
            cur_geom = feat_list[i].geometry()
            if math.fabs(cur_geom.GetY() - valueY) < radius \
                    and feat_list[i] not in prev_path:
                the_path.append(feat_list[i])
                feat_list[i].SetField(newField, flight_num)
                layer.SetFeature(feat_list[i])
            # else:
            #     AzCalcTool(dataSource, layer, None).delFeatByID(feat_list[i].GetFID())
        return the_path

    def timeSort(self, prevFeat, nextFeat):
        data_format = '%m-%d-%YT%H:%M:%S,%f'

        prevDataTime = datetime.strptime(prevFeat['TIME'], data_format)
        nextDataTime = datetime.strptime(nextFeat['TIME'], data_format)

        if nextDataTime.date() != prevDataTime.date():
            return True
        elif (nextDataTime.time().hour - prevDataTime.time().hour) > 0 or \
                (nextDataTime.time().minute - prevDataTime.time().minute) > 3 or \
                (nextDataTime.time().second - prevDataTime.time().second) > 10:
            return True
        else:
            return False
