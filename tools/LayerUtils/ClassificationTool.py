import math
from datetime import datetime
from random import randint
from statistics import mode

import numpy
import numpy as np

from PyQt5.QtCore import QVariant
from osgeo import ogr
from qgis._core import QgsVectorDataProvider, QgsFeatureRequest, QgsField

from .AzimutMathUtil import AzimutMathUtil
from .LayerManagement import LayerManagement
from .LogFileTool import LogFileTool
from .FeatureManagement import FeatureManagement
from .BufferAzimuth import BufferAzimuth


# from .MainIFace import MainIFace


class ClassificationTool:

    def __init__(self, outDS, templayer, guiUtil, filename, filepath):
        self.bufSize = 10
        self.global_num = 0
        self.data_format = '%Y/%m/%d %H:%M:%S.%f'
        self.log_lines = []
        self.accuracy = 5
        self.fieldDist = "DIST"
        self.fieldDy = "DY"
        self.fieldDx = "DX"
        self.fieldAz = "AZIMUTH"
        self.fieldAzAvg = "AZIMUTH_AVG"
        self.fieldGlobalNum = "GLOBAL_NUM"
        self.fieldNum = "FLIGHT_NUM"
        self.fieldClass = "CLASS"
        self.fieldPass = "NUM_PASS"
        self.fieldSpeed = 'SPEED'
        self.targetAzimuth = 0
        self.outDS = outDS
        self.templayer = templayer
        self.filename = filename
        self.filepath = filepath
        self.guiUtil = guiUtil
        self.fm = FeatureManagement(self.outDS, self.templayer, self.guiUtil)

    def numerateProfiles(self, feat_list):
        i = 1
        feat_list = self.fm.sortListByLambda(feat_list, self.fieldGlobalNum)
        isProfile = False
        profileNum = 1

        while i < len(feat_list):
            if feat_list[i].GetField(self.fieldClass) == 'азимут<180' or feat_list[i].GetField(self.fieldClass) == 'азимут>180':
                isProfile = True
                feat_list[i].SetField(self.fieldNum, profileNum)
            else:
                if isProfile:
                    profileNum += 1
                isProfile = False
            i += 1

    def getMostFreqAzimuth(self, feat_list):
        step = 10
        res = []
        # resSpeed = []
        i = 1
        prev_ind = 0
        # prev_date = datetime.strptime(feat_list[0].GetField('TIME'), self.data_format)
        az = AzimutMathUtil()
        while i < len(feat_list):
            a = az.azimutCalc([feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                              [feat_list[i].geometry().GetX(),
                               feat_list[i].geometry().GetY()])
            z = int((a + step / 2) % 360 // step) * 10
            res.append(z)

            # dist = az.distanceCalc([feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
            #                        [feat_list[i].geometry().GetX(),
            #                         feat_list[i].geometry().GetY()])
            # cur_date = datetime.strptime(feat_list[i].GetField('TIME'), self.data_format)
            # period = cur_date - prev_date
            # if period.total_seconds() != 0:
            #     cur_speed = dist / period.total_seconds()
            # else:
            #     cur_speed = 156634

            prev_ind = i
            # prev_date = cur_date
            i += 1

        targetAzimuth = max(set(res), key=res.count)
        if targetAzimuth > 180:
            targetAzimuth -= 180
        return targetAzimuth

    def classify(self, azimuth_1, speed):
        if math.fabs(self.targetAzimuth - azimuth_1) <= self.accuracy:
            return 'азимут<180'
        elif math.fabs(self.targetAzimuth + 180 - azimuth_1) <= self.accuracy:
            return 'азимут>180'
        elif speed == 0.0:
            return 'нулевая скорость'
        else:
            return 'несовпадение азимута'

    def azimuthLoop(self, feat_list, numPass):
        prev_ind = 0
        i = 1
        az = AzimutMathUtil()
        control_flights = []
        prev_speed = 20000
        prev_date = datetime.strptime(feat_list[0].GetField('TIME'), self.data_format)

        feat_list[0].SetField(self.fieldClass, 'первая точка')  # первая точка - точка взлета
        feat_list[0].SetField(self.fieldGlobalNum, self.global_num)
        self.global_num += 1

        # создадим несколько размеров окон для сглаживания
        window = BufferAzimuth(self.bufSize, self.targetAzimuth, self.accuracy)
        # windows = []
        # for bufSize in self.bufSizeList:
        #     window = BufferAzimuth(bufSize)
        #     windows.append(window)

        while i < len(feat_list):
            # self.log_lines.append('\n\nИтерация № ' + str(i))
            dist = az.distanceCalc([feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                                   [feat_list[i].geometry().GetX(),
                                    feat_list[i].geometry().GetY()])
            cur_date = datetime.strptime(feat_list[i].GetField('TIME'), self.data_format)
            period = cur_date - prev_date
            if period.total_seconds() != 0:
                cur_speed = dist / period.total_seconds()
            else:
                cur_speed = 156634

            # delta_speed = math.fabs(prev_speed - cur_speed)
            feat_list[i].SetField(self.fieldSpeed, cur_speed)

            # if cur_speed > prev_speed * 3:
            if dist > 10 and period.total_seconds() < 60:
                # self.log_lines.append('\nВыполнилось условие dist > 10 и разница во времени < 60 сек для i = '+str(i))
                control_flights.append(feat_list[i])
            else:
                # self.log_lines.append('\nВыполнилось условие else для i = ' + str(i))
                azimuth = az.azimutCalc(
                    [feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                    [feat_list[i].geometry().GetX(),
                     feat_list[i].geometry().GetY()])

                # Запишем значение азимута и номера фактора в отдельный столбец
                feat_list[i].SetField(self.fieldGlobalNum, self.global_num)

                # маркировка без окна сглаживания
                feat_list[i].SetField(self.fieldAz, azimuth)
                # feat_list[i].SetField(self.fieldClass, self.classify(azimuth, cur_speed))

                # маркировка с разными окнами сглаживания
                # k = 0
                # for bufSize in self.bufSizeList:
                window.addElem(azimuth)
                j = i - self.bufSize
                if j >= 0:
                    feat_list[j].SetField(self.fieldAzAvg, window.getAverage())
                    feat_list[j].SetField(self.fieldClass, self.classify(window.getAverage(), cur_speed))
                    # k += 1

                prev_ind = i
                prev_date = cur_date
                prev_speed = cur_speed

            i += 1
            self.global_num += 1

        return control_flights

    def mainAzimutCalc(self):
        self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем классификацию точек...')

        # создаем новый столбец
        self.fm.createNewField(self.fieldGlobalNum, ogr.OFTInteger)
        self.fm.createNewField(self.fieldAz, ogr.OFTReal)
        self.fm.createNewField(self.fieldAzAvg, ogr.OFTReal)
        self.fm.createNewField(self.fieldSpeed, ogr.OFTReal)
        # # self.createNewField(self.fieldDx, ogr.OFTReal)
        # # self.createNewField(self.fieldDy, ogr.OFTReal)
        # self.fm.createNewField(self.fieldDist, ogr.OFTReal)
        # self.fm.createNewField(self.fieldPass, ogr.OFTInteger)
        self.fm.createNewField(self.fieldNum, ogr.OFTInteger)
        self.fm.createNewField(self.fieldClass, ogr.OFTString)

        # создаем дополнительные столбцы для разных окон сглаживания
        # k = 0
        # for k in range(len(self.bufSizeList)):
        #     self.fm.createNewField(self.fieldClass + '_' + str(self.bufSizeList[k]), ogr.OFTString)
        #     k += 1

        # переместим фичи из временного слоя в список
        feat_list = self.fm.tempLayerToListFeat(self.templayer)

        # отсортируем список по времени
        feat_list = self.fm.sortListByLambda(feat_list, 'TIME')

        # вычислим целевой азимут
        self.targetAzimuth = 30
        # self.targetAzimuth = self.getMostFreqAzimuth(feat_list)
        self.guiUtil.setOutputStyle('black', 'normal', 'Целевой азимут: ' + str(self.targetAzimuth))

        # # проходим по всем азимутам и сравниваем с целевым
        num_pass = 1
        control_flights = self.azimuthLoop(feat_list, num_pass)

        # self.guiUtil.setOutputStyle('black', 'normal', str(len(control_flights)))

        # повторяем процедуру для полетов, совершенных одновременно
        while len(control_flights) > 0:
            num_pass += 1
            control_flights = self.azimuthLoop(control_flights, num_pass)
            # self.guiUtil.setOutputStyle('black', 'normal', str(len(control_flights)))

        self.guiUtil.setOutputStyle('green', 'bold', 'Точки успешно классифицированы!')
        self.outDS.SyncToDisk()

        # сортируем по глобальному номеру и нумеруем профиля
        self.numerateProfiles(feat_list)

        # сохраним основной файл
        lyr2 = LayerManagement(self.guiUtil)
        try:
            lyr2.saveFeatListToFile(feat_list, self.templayer, self.filename, self.filepath)
        except Exception as err:
            self.guiUtil.setOutputStyle('red', 'bold', '\nНе удалось сохранить/загрузить файл! ' + str(err))
