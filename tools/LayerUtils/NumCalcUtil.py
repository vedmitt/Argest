import math
import os
from datetime import datetime

import ogr

from .FeatCalcTool import FeatCalcTool
from .AzimutMathUtil import AzimutMathUtil


class NumCalcUtil:
    guiUtil = None
    layer = None
    feat_list = None
    newField = 'FLIGHT_NUM'
    extent = None
    dataSource = None

    def __init__(self, guiUtil):
        NumCalcUtil.guiUtil = guiUtil

    def setFlightNumber(self, dataSource, layer):
        NumCalcUtil.guiUtil.setTextEditStyle('black', 'normal', 'Начинаем нумерацию профилей...')
        NumCalcUtil.layer = layer
        NumCalcUtil.dataSource = dataSource

        # создаем новый столбец
        fieldDefn = ogr.FieldDefn(NumCalcUtil.newField, ogr.OFTInteger)
        NumCalcUtil.layer.CreateField(fieldDefn)

        # Переводим все фичи в список, сортируем по времени
        az = FeatCalcTool(NumCalcUtil.dataSource, NumCalcUtil.layer, None)
        NumCalcUtil.feat_list = az.tempLayerToListFeat(NumCalcUtil.layer)
        NumCalcUtil.feat_list = az.sortListByLambda(NumCalcUtil.feat_list, 'TIME')

        # найдем средний азимут первых 10 точек
        av_az = AzimutMathUtil().averageAzimut(NumCalcUtil.feat_list[:10])
        NumCalcUtil.guiUtil.textEdit.append(str(av_az))

        # повернем фигуру так чтобы профиля стали вертикальными
        NumCalcUtil.feat_list = self.rotationToList(av_az, NumCalcUtil.feat_list)

        av_az = AzimutMathUtil().averageAzimut(NumCalcUtil.feat_list[:10])
        NumCalcUtil.guiUtil.textEdit.append(str(av_az))

        # Переносим начало координат в левый верхний угол

        extent = layer.GetExtent()

        # # Находим самую верхнююю левую точку и начинаем с нее
        # flight_num = 1
        # first_path = self.findThePath(flight_num, extent, 0.0003)
        # prev_path = first_path
        #
        # flight_num = 2
        #
        # dist = 0.0006
        # while len(prev_path) < len(NumCalcUtil.feat_list):
        #     the_path = self.findThePath(flight_num, prev_path, dist)
        #     # TimeCalcUtil.guiUtil.textEdit.append(str(len(the_path)))
        #     if len(the_path) != 0:
        #         prev_path.extend(the_path)
        #         flight_num += 1
        #     dist += 0.00035

        NumCalcUtil.dataSource.SyncToDisk()
        # NumCalcUtil.guiUtil.setTextEditStyle('black', 'normal', 'Профилей выделено: ' + str(flight_num))
        NumCalcUtil.guiUtil.setTextEditStyle('green', 'bold', 'Нумерация профилей завершена!')

    def findThePath(self, flight_num, prev_path, radius):
        the_path = []
        if len(prev_path) < 5:
            # this is the first path
            valueY = prev_path[3]
        else:
            valueY = prev_path[0].geometry().GetY()

        for i in range(len(NumCalcUtil.feat_list)):
            cur_geom = NumCalcUtil.feat_list[i].geometry()
            if math.fabs(cur_geom.GetY() - valueY) < radius \
                    and NumCalcUtil.feat_list[i].GetField(NumCalcUtil.newField) is None:
                the_path.append(NumCalcUtil.feat_list[i])
                FeatCalcTool(NumCalcUtil.dataSource, NumCalcUtil.layer, NumCalcUtil.guiUtil).setFieldValue(NumCalcUtil.feat_list[i], NumCalcUtil.newField, flight_num)
            # else:
            #     AzCalcTool(dataSource, layer, None).delFeatByID(feat_list[i].GetFID())
        return the_path


    def setNewAxis(self):
        pass

    def rotationToList(self, av_az, feat_list):
        target_deg = 90  # 270
        fix_deg = -90
        if math.fabs(av_az - target_deg) > 5 or math.fabs(av_az - (target_deg + 180)) > 5:
            for item in feat_list:
                new_geom = AzimutMathUtil().rotateTransform(item.geometry().GetX(), item.geometry().GetY(), fix_deg)
                # присваиваем новую геометрию точкам
                NumCalcUtil.guiUtil.textEdit.append(str(new_geom[0]) + ' ' + str(new_geom[1]))
                # create the WKT for the feature using Python string formatting
                wkt = "POINT(%f %f)" % (float(new_geom[0]),
                                        float(new_geom[1]))
                # Create the point from the Well Known Txt
                point = ogr.CreateGeometryFromWkt(wkt)
                # Set the feature geometry using the point
                item.SetGeometry(point)
                # NumCalcUtil.layer.SetFeature(item)
        return feat_list

    def timeSort(self, prevFeat, nextFeat):
        data_format = '%m-%d-%YT%H:%M:%S,%f'

        prevDataTime = datetime.strptime(prevFeat['TIME'], data_format)
        nextDataTime = datetime.strptime(nextFeat['TIME'], data_format)

        prevTime = str(prevDataTime.time().hour) + str(prevDataTime.time().minute)  # + str(prevDataTime.time().second)
        nextTime = str(nextDataTime.time().hour) + str(nextDataTime.time().minute)  # + str(nextDataTime.time().second)
        if nextDataTime.date() != prevDataTime.date():
            return True
        # elif (nextDataTime.time().hour - prevDataTime.time().hour) > 0 or \
        #         (nextDataTime.time().minute - prevDataTime.time().minute) > 3 or \
        #         (nextDataTime.time().second - prevDataTime.time().second) > 10:
        elif math.fabs(int(nextTime) - int(prevTime)) > 1:
            NumCalcUtil.guiUtil.textEdit.append(str(nextTime))
            NumCalcUtil.guiUtil.textEdit.append(str(prevTime))
            return True
        else:
            return False

    def saveExtend(self, dataSource, layer):
        extent = layer.GetExtent()
        # Create a Polygon from the extent tuple
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(extent[0], extent[2])
        ring.AddPoint(extent[1], extent[2])
        ring.AddPoint(extent[1], extent[3])
        ring.AddPoint(extent[0], extent[3])
        ring.AddPoint(extent[0], extent[2])
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        # layer.SetSpatialFilterRect(143.46374420000938699, 63.73680240000010144, 143.46371380001073703, 63.73723679999989145)  # x1 y1 x2 y2
        # layer.SetSpatialFilter(143.46202220000850502, 63.7376846499992098, 143.46197729999403236, 63.73768420000124024)  # x1 y1 x2 y2

        # layer.SetSpatialFilterRect(extent[0], extent[2], extent[1], extent[3])  # x1 y1 x2 y2
        # TimeCalcUtil.guiUtil.textEdit.append(str(extent[0]))
        # TimeCalcUtil.guiUtil.textEdit.append(str(extent[1]))
        # TimeCalcUtil.guiUtil.textEdit.append(str(extent[2]))
        # TimeCalcUtil.guiUtil.textEdit.append(str(extent[3]))
        for feature in layer:
            FeatCalcTool(dataSource, layer, None).delFeatByID(feature.GetFID())

        self.saveToFile('states_extent', "M:/Sourcetree/output/states_extent.shp", poly)

    def saveConvexhull(self, dataSource, layer):
        # Collect all Geometry
        geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
        for feature in layer:
            geomcol.AddGeometry(feature.GetGeometryRef())

        # Calculate convex hull (polygon)
        convexhull = geomcol.ConvexHull()
        self.saveToFile('states_convexhull', "M:/Sourcetree/output/states_convexhull.shp", convexhull)

    def saveToFile(self, fname, fpath, fgeometry):
        # # Save extent to a new Shapefile
        outShapefile = fpath
        outDriver = ogr.GetDriverByName("ESRI Shapefile")

        # Remove output shapefile if it already exists
        if os.path.exists(outShapefile):
            outDriver.DeleteDataSource(outShapefile)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(outShapefile)
        outLayer = outDataSource.CreateLayer(fname, geom_type=ogr.wkbPolygon)

        # Add an ID field
        idField = ogr.FieldDefn("id", ogr.OFTInteger)
        outLayer.CreateField(idField)

        # Create the feature and set values
        featureDefn = outLayer.GetLayerDefn()
        feature = ogr.Feature(featureDefn)
        feature.SetGeometry(fgeometry)
        feature.SetField("id", 1)
        outLayer.CreateFeature(feature)
        feature = None

        # Save and close DataSource
        inDataSource = None
        outDataSource = None
