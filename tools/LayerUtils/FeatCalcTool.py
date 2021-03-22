import math
from datetime import datetime
from statistics import mode
import numpy as np

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
        global azimuth_2
        self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем классификацию точек...')

        # создаем новый столбец
        fieldNum = "feat_num"
        self.createNewField(fieldNum, ogr.OFTInteger)
        fieldAz = "AZIMUTH"
        self.createNewField(fieldAz, ogr.OFTReal)
        fieldClass = "NUM_FLIGHT"
        self.createNewField(fieldClass, ogr.OFTInteger)

        # переместим фичи из временного слоя в список
        feat_list = self.tempLayerToListFeat(self.templayer)

        # отсортируем список по времени
        feat_list = self.sortListByLambda(feat_list, 'TIME')

        accuracy = 5
        i = 0
        numFlight = 1
        az_all_set = []
        flightList = []
        parts_list = []
        az_temp = []
        avg_az_list = []

        self.setFieldValue(feat_list[0], fieldAz, 0)  # the first elem of azimuth field

        while i + 9 < len(feat_list):
            # azimuth_1 = AzimutMathUtil().azimutCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
            #                                         [feat_list[i + 1].geometry().GetX(),
            #                                          feat_list[i + 1].geometry().GetY()])
            # azimuth_2 = AzimutMathUtil().azimutCalc(
            #     [feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()],
            #     [feat_list[i + 2].geometry().GetX(), feat_list[i + 2].geometry().GetY()])

            res = AzimutMathUtil().getAzimuth(feat_list, 10, i)

            # Запишем значение азимута и номера фактора в отдельный столбец
            self.setFieldValue(feat_list[i], fieldNum, i)
            # self.setFieldValue(feat_list[i + 1], fieldAz, azimuth_1)
            # self.setFieldValue(feat_list[i + 2], fieldAz, azimuth_2)

            # dist = AzimutMathUtil().distanceCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
            #                                      [feat_list[i + 1].geometry().GetX(),
            #                                       feat_list[i + 1].geometry().GetY()])

            # az_all_set.append(azimuth_1)
            # az_all_set.append(azimuth_2)

            i += 9

            # self.outDS.SyncToDisk()

            # вычислим целевой азимут
            # targetAzimuth = np.std(az_all_set)
            # azimuth_avg = np.average(az_all_set)
            # self.guiUtil.setOutputStyle('black', 'normal', '\nЦелевой азимут: ' + str(targetAzimuth))
            # self.guiUtil.setOutputStyle('black', 'normal', 'Средний азимут: ' + str(azimut_avg))

        #     if math.fabs(azimuth_1 - azimuth_2) < accuracy:
        #         parts_list.append(feat_list[i])
        #         az_temp.append(azimuth_1)
        #         # self.setFieldValue(feat_list[i], fieldClass, numFlight)
        #     else:
        #         if parts_list is not None:
        #             # numFlight += 1
        #             flightList.append(parts_list)
        #             avg_az_list.append(np.average(az_temp))
        #         parts_list = [feat_list[i]]
        #         # self.setFieldValue(feat_list[i], fieldClass, numFlight)
        #         az_temp = [azimuth_1]
        #     i += 1
        #
        # if parts_list is not None:
        #     parts_list.append(feat_list[i])
        #     parts_list.append(feat_list[i + 1])
        #     avg_az_list.append(azimuth_2)
        #     flightList.append(parts_list)
        #
        # self.guiUtil.setOutputStyle('black', 'normal',
        #                             'Количество частей полетов: ' + str(len(flightList)))
        # longest_path = max(len(elem) for elem in flightList)
        # self.guiUtil.setOutputStyle('black', 'normal', 'Самый длинный полет: ' + str(longest_path))
        #
        # i_longest = 0
        # for path in flightList:
        #     if len(path) == longest_path:
        #         i_longest = flightList.index(path)
        #         break
        #
        # target_az = avg_az_list[i_longest]
        # self.guiUtil.setOutputStyle('black', 'normal', 'Целевой азимут: ' + str(target_az))
        #
        # numFlight = 1
        # for i in range(len(avg_az_list)):
        #     if math.fabs(avg_az_list[i] - target_az) < accuracy or \
        #             math.fabs((avg_az_list[i] + 180) - target_az) < accuracy:
        #         self.setFieldValue(feat_list[i], fieldClass, numFlight)
        #         numFlight += 1
        #         # if len(flightList[i]) < 20:
        #         # for feat in flightList[i]:
        #         #     self.delFeatByID(feat.GetFID())
        #     else:
        #         pass
        #         # numFlight += 1
        #         # self.setFieldValue(feat_list[i], fieldClass, numFlight)
        #         # for feat in flightList[i]:
        #         #     self.delFeatByID(feat.GetFID())

        self.guiUtil.setOutputStyle('green', 'bold', 'Точки успешно классифицированы!')
        # self.guiUtil.setOutputStyle('black', 'normal', '\nКоличество точек в полученном слое: ' +
        #                             str(self.templayer.GetFeatureCount()))
        self.outDS.SyncToDisk()
