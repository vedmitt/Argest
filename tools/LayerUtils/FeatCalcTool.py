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
        self.fieldDist = "DIST"
        self.fieldDy = "DY"
        self.fieldDx = "DX"
        self.fieldAz = "AZIMUTH"
        self.fieldNum = "feat_num"
        self.fieldClass = "CLASS"
        self.fieldPass = "NUM_PASS"
        self.targetAzimuth = 0
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
        if fieldType == ogr.OFTString:
            fieldDefn.SetWidth(30)
        self.templayer.CreateField(fieldDefn)

    def setFieldValue(self, feature, fieldName, value):
        if feature.GetField(fieldName) is None:
            feature.SetField(fieldName, value)
            self.templayer.SetFeature(feature)

    def getTargetAzimuth(self, feat_list):
        pass

    def azimuthLoop(self, feat_list, numPass):
        accuracy = 5
        i = 1
        prev_ind = 0
        az = AzimutMathUtil()
        control_flights = []

        self.setFieldValue(feat_list[0], self.fieldClass, 'первая точка')  # первая точка - точка взлета

        while i < len(feat_list):
            dist = AzimutMathUtil().distanceCalc([feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                                                 [feat_list[i].geometry().GetX(),
                                                  feat_list[i].geometry().GetY()])
            if dist > 10:
                control_flights.append(feat_list[i])
            else:
                azimuth_1 = az.azimutCalc([feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                                          [feat_list[i].geometry().GetX(),
                                           feat_list[i].geometry().GetY()])

                # dX = feat_list[i + step].geometry().GetX() - feat_list[i].geometry().GetX()
                # dY = feat_list[i + step].geometry().GetY() - feat_list[i].geometry().GetY()

                # dX = feat_list[i].geometry().GetX()
                # dY = feat_list[i].geometry().GetY()

                # Запишем значение азимута и номера фактора в отдельный столбец
                self.setFieldValue(feat_list[i], self.fieldNum, i)
                self.setFieldValue(feat_list[i], self.fieldAz, azimuth_1)
                # self.setFieldValue(feat_list[i], self.fieldDx, dX)
                # self.setFieldValue(feat_list[i], self.fieldDy, dY)
                self.setFieldValue(feat_list[i], self.fieldDist, dist)
                self.setFieldValue(feat_list[i], self.fieldPass, numPass)

                if math.fabs(self.targetAzimuth - azimuth_1) <= accuracy:
                    self.setFieldValue(feat_list[i], self.fieldClass, 'азимут<180')
                elif math.fabs(self.targetAzimuth + 180 - azimuth_1) <= accuracy:
                    self.setFieldValue(feat_list[i], self.fieldClass, 'азимут>180')
                else:
                    self.setFieldValue(feat_list[i], self.fieldClass, 'несовпадение азимута')
                    # self.delFeatByID(feat_list[i].GetFID())

                prev_ind = i

            i += 1

        return control_flights


    def mainAzimutCalc(self):
        self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем классификацию точек...')

        # создаем новый столбец
        self.createNewField(self.fieldNum, ogr.OFTInteger)
        self.createNewField(self.fieldAz, ogr.OFTReal)
        self.createNewField(self.fieldClass, ogr.OFTString)
        # self.createNewField(self.fieldDx, ogr.OFTReal)
        # self.createNewField(self.fieldDy, ogr.OFTReal)
        self.createNewField(self.fieldDist, ogr.OFTReal)
        self.createNewField(self.fieldPass, ogr.OFTInteger)

        # переместим фичи из временного слоя в список
        feat_list = self.tempLayerToListFeat(self.templayer)

        # отсортируем список по времени
        feat_list = self.sortListByLambda(feat_list, 'TIME')

        # вычислим целевой азимут
        self.targetAzimuth = 30

        num_pass = 1

        control_flights = self.azimuthLoop(feat_list, num_pass)

        self.guiUtil.setOutputStyle('black', 'normal', str(len(control_flights)))
        # for item in control_flights:
        #     self.guiUtil.setOutputStyle('black', 'normal', str(item.geometry().GetX()) + str(item.geometry().GetY()))

        while len(control_flights) > 0:
            num_pass += 1
            control_flights = self.azimuthLoop(control_flights, num_pass)
            self.guiUtil.setOutputStyle('black', 'normal', str(len(control_flights)))

        self.guiUtil.setOutputStyle('green', 'bold', 'Точки успешно классифицированы!')
        self.outDS.SyncToDisk()
