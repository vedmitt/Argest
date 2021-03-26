import math
from datetime import datetime
from statistics import mode
import numpy as np

from PyQt5.QtCore import QVariant
from osgeo import ogr
from osgeo.ogr import Geometry
from qgis._core import QgsVectorDataProvider, QgsFeatureRequest, QgsField

from .AzimutMathUtil import AzimutMathUtil
from .FeatureManagement import FeatureManagement
from .LogFileTool import LogFileTool


class ClassificationTool_2:

    def __init__(self, outDS, templayer, guiUtil):
        self.log_lines = []
        self.accuracy = 5
        self.fieldDist = "DIST"
        self.fieldDy = "DY"
        self.fieldDx = "DX"
        self.fieldAz = "AZIMUTH"
        self.fieldAz1 = "AZIMUTH_2"
        self.fieldNum = "feat_num"
        self.fieldClass = "CLASS"
        self.fieldPass = "NUM_PASS"
        self.targetAzimuth = 0
        self.outDS = outDS
        self.templayer = templayer
        self.guiUtil = guiUtil
        self.fm = FeatureManagement(self.outDS, self.templayer, self.guiUtil)

    def getMostFreqAzimuth(self, feat_list):
        step = 10
        res = []
        i = 1
        prev_ind = 0
        az = AzimutMathUtil()
        while i < len(feat_list):
            azimuth = az.azimutCalc([feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                                    [feat_list[i].geometry().GetX(),
                                     feat_list[i].geometry().GetY()])
            z = int((azimuth + step / 2) % 360 // step) * 10
            res.append(z)
            dist = az.distanceCalc([feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                                   [feat_list[i].geometry().GetX(),
                                    feat_list[i].geometry().GetY()])

            # запишем значение азимута и расстояние мужду точками в столбцы
            self.fm.setFieldValue(feat_list[i], self.fieldAz, azimuth)
            self.fm.setFieldValue(feat_list[i], self.fieldDist, dist)

            prev_ind = i
            i += 1

        self.outDS.SyncToDisk()
        targetAzimuth = max(set(res), key=res.count)
        if targetAzimuth > 180:
            targetAzimuth -= 180
        return targetAzimuth

    def getNewAzimuth(self, feat_list):
        step = 10
        res = []
        i = 1
        prev_ind = 0
        az = AzimutMathUtil()
        while i < len(feat_list):
            azimuth = az.azimutCalc([feat_list[prev_ind].GetField('DX'), feat_list[prev_ind].GetField('DY')],
                                    [feat_list[i].GetField('DX'),
                                     feat_list[i].GetField('DY')])
            z = int((azimuth + step / 2) % 360 // step) * 10
            res.append(z)

            # запишем значение азимута и расстояние мужду точками в столбцы
            self.fm.setFieldValue(feat_list[i], self.fieldAz1, azimuth)
            # self.fm.setFieldValue(feat_list[i], self.fieldDist, dist)

            prev_ind = i
            i += 1

        self.outDS.SyncToDisk()
        targetAzimuth = max(set(res), key=res.count)
        if targetAzimuth > 180:
            targetAzimuth -= 180
        return targetAzimuth

    def affineCoordinate(self, feat_list, targetAzimuth):
        az = AzimutMathUtil()
        angle = 90 - targetAzimuth
        Ox = feat_list[0].geometry().GetX()
        Oy = feat_list[0].geometry().GetY()
        for feat in feat_list:
            fg = feat.geometry()
            dx = fg.GetX() - Ox
            dy = fg.GetY() - Oy
            new_x, new_y = az.rotateTransform(dx, dy, angle)
            # feat.SetGeometry(Geometry(new_x, new_y))
            self.fm.setFieldValue(feat, self.fieldDx, new_x)
            self.fm.setFieldValue(feat, self.fieldDy, new_y)

    def mainAzimutCalc(self):
        self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем классификацию точек...')

        # создаем новый столбец
        # self.fm.createNewField(self.fieldNum, ogr.OFTInteger)
        self.fm.createNewField(self.fieldAz, ogr.OFTReal)
        self.fm.createNewField(self.fieldDist, ogr.OFTReal)
        self.fm.createNewField(self.fieldDx, ogr.OFTReal)
        self.fm.createNewField(self.fieldDy, ogr.OFTReal)
        self.fm.createNewField(self.fieldAz1, ogr.OFTReal)
        # self.fm.createNewField(self.fieldPass, ogr.OFTInteger)
        # self.fm.createNewField(self.fieldClass, ogr.OFTString)

        # переместим фичи из временного слоя в список
        feat_list = self.fm.tempLayerToListFeat(self.templayer)

        # отсортируем список по времени
        feat_list = self.fm.sortListByLambda(feat_list, 'TIME')

        # вычислим целевой азимут
        # self.targetAzimuth = 30
        self.targetAzimuth = self.getMostFreqAzimuth(feat_list)
        self.guiUtil.setOutputStyle('black', 'normal', 'Целевой азимут: ' + str(self.targetAzimuth))

        # выполним аффинные преобразования относительно первой точки
        self.affineCoordinate(feat_list, self.targetAzimuth)
        self.guiUtil.setOutputStyle('black', 'normal', 'Аффиное преобразование выполнено!')
        new_azimuth = self.getNewAzimuth(feat_list)
        self.guiUtil.setOutputStyle('black', 'normal', 'Новый азимут: ' + str(new_azimuth))
