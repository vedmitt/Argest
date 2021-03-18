import math
from datetime import datetime

from PyQt5.QtCore import QVariant
from osgeo import ogr
from qgis._core import QgsVectorDataProvider, QgsFeatureRequest, QgsField

from .AzimutMathUtil import AzimutMathUtil


class FeatCalcTool:
    # outDS = None
    # templayer = None
    # guiUtil = None

    def __init__(self, outDS, templayer, guiUtil):
        self.outDS = outDS
        self.templayer = templayer
        self.guiUtil = guiUtil

    def removeZeroPointsFromMemory(self, boolChecked):
        # далее работаем с временным слоем
        # -------- удаляем нулевые точки ---------------
        if boolChecked:
            self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем удаление нулевых точек...')
            for i in range(self.templayer.GetFeatureCount()):
                feat = self.templayer.GetNextFeature()
                if feat is not None:
                    geom = feat.geometry()
                    if geom.GetX() == 0.0 and geom.GetY() == 0.0:
                        self.delFeatByID(feat.GetFID())
            self.templayer.ResetReading()

            self.guiUtil.setOutputStyle('green', 'bold', 'Нулевые точки успешно удалены!')
            self.guiUtil.setOutputStyle('black', 'normal', 'Количество точек после удаления нулевых: ' +
                                        str(self.templayer.GetFeatureCount()))
        self.outDS.SyncToDisk()

    def delFeatByID(self, ID):
        self.templayer.DeleteFeature(ID)
        self.outDS.ExecuteSQL('REPACK ' + self.templayer.GetName())

    ##------------------------------------------------------------------

    def tempLayerToListFeat(self, templayer):
        feat_list = []
        for i in range(templayer.GetFeatureCount()):
            feat = templayer.GetNextFeature()
            feat_list.append(feat)
        templayer.ResetReading()
        return feat_list

    def sortListByLambda(self, mylist, fieldName):
        mylist = sorted(mylist, key=lambda feature: feature.GetField(fieldName), reverse=False)
        return mylist

    def createNewField(self, fieldName, fieldType):
        fieldDefn = ogr.FieldDefn(fieldName, fieldType)
        self.templayer.CreateField(fieldDefn)

    def setFieldValue(self, feature, fieldName, value):
        if feature.GetField(fieldName) is None:
            feature.SetField(fieldName, value)
            self.templayer.SetFeature(feature)

    def mainAzimutCalc(self):
        global azimut_2
        self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем классификацию точек...')

        # создаем новый столбец
        fieldNum = "feat_num"
        self.createNewField(fieldNum, ogr.OFTInteger)
        fieldAz = "AZIMUTH"
        self.createNewField(fieldAz, ogr.OFTReal)

        # переместим фичи из временного слоя в список
        feat_list = self.tempLayerToListFeat(self.templayer)

        # отсортируем список по времени
        feat_list = self.sortListByLambda(feat_list, 'TIME')

        accuracy = 5
        flightList = []
        parts_list = []
        min_dist = 6.966525707833812e-08
        bad_paths = []
        i = 0
        az_temp = []
        avg_az_list = []

        self.setFieldValue(feat_list[0], fieldAz, 0)

        while i + 2 < len(feat_list):
            azimut_1 = AzimutMathUtil().azimutCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
                                                   [feat_list[i + 1].geometry().GetX(),
                                                    feat_list[i + 1].geometry().GetY()])
            azimut_2 = AzimutMathUtil().azimutCalc(
                [feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()],
                [feat_list[i + 2].geometry().GetX(), feat_list[i + 2].geometry().GetY()])

            # Запишем значение азимута и номера фактора в отдельный столбец
            self.setFieldValue(feat_list[i], fieldNum, i)
            self.setFieldValue(feat_list[i+1], fieldAz, azimut_1)
            self.setFieldValue(feat_list[i+2], fieldAz, azimut_1)

            dist = AzimutMathUtil().distanceCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
                                                 [feat_list[i + 1].geometry().GetX(),
                                                  feat_list[i + 1].geometry().GetY()])

            if math.fabs(azimut_1 - azimut_2) < accuracy:
                if dist < min_dist:
                    bad_paths.append(feat_list[i].GetFID())
                else:
                    parts_list.append(feat_list[i])
                    az_temp.append(azimut_1)
            else:
                if parts_list is not None:
                    flightList.append(parts_list)
                    az_sum = 0
                    for item in az_temp:
                        az_sum = az_sum + item
                    if len(az_temp) != 0:
                        avg_az_list.append(az_sum / len(az_temp))
                parts_list = [feat_list[i]]
                az_temp = [azimut_1]
            i += 1

        if parts_list is not None:
            parts_list.append(feat_list[i])
            parts_list.append(feat_list[i + 1])
            avg_az_list.append(azimut_2)
            flightList.append(parts_list)

        # удаляем аномальные пути в начале полетов (неудачный метод)
        for item in bad_paths:
            self.delFeatByID(item)

        self.guiUtil.setOutputStyle('black', 'normal',
                                            'Количество частей полетов: ' + str(len(flightList)))
        longest_path = max(len(elem) for elem in flightList)
        self.guiUtil.setOutputStyle('black', 'normal', 'Самый длинный полет: ' + str(longest_path))

        i_longest = 0
        for path in flightList:
            if len(path) == longest_path:
                i_longest = flightList.index(path)
                break

        target_az = avg_az_list[i_longest]
        self.guiUtil.setOutputStyle('black', 'normal', 'Целевой азимут: ' + str(target_az))
        for i in range(len(avg_az_list)):
            if math.fabs(avg_az_list[i] - target_az) < accuracy or math.fabs(
                    (avg_az_list[i] + 180) - target_az) < accuracy:
                if len(flightList[i]) < 20:
                    for feat in flightList[i]:
                        self.delFeatByID(feat.GetFID())
            else:
                for feat in flightList[i]:
                    self.delFeatByID(feat.GetFID())

        self.guiUtil.setOutputStyle('green', 'bold', 'Точки успешно классифицированы!')
        self.guiUtil.setOutputStyle('black', 'normal', '\nКоличество точек в полученном слое: ' +
                                    str(self.templayer.GetFeatureCount()))
        self.outDS.SyncToDisk()
