import math
from datetime import datetime
from statistics import mode
import numpy as np

from PyQt5.QtCore import QVariant
from osgeo import ogr
from qgis._core import QgsVectorDataProvider, QgsFeatureRequest, QgsField

from .AzimutMathUtil import AzimutMathUtil
from .LogFileTool import LogFileTool
from .FeatureManagement import FeatureManagement


class ClassificationTool_1:

    def __init__(self, outDS, templayer, guiUtil):
        self.log_lines = []
        self.accuracy = 5
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
        self.fm = FeatureManagement(self.outDS, self.templayer, self.guiUtil)

    def getMostFreqAzimuth(self, feat_list):
        step = 10
        res = []
        i = 1
        prev_ind = 0
        az = AzimutMathUtil()
        while i < len(feat_list):
            a = az.azimutCalc([feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                              [feat_list[i].geometry().GetX(),
                               feat_list[i].geometry().GetY()])
            z = int((a + step / 2) % 360 // step) * 10
            res.append(z)
            prev_ind = i
            i += 1

        targetAzimuth = max(set(res), key=res.count)
        if targetAzimuth > 180:
            targetAzimuth -= 180
        return targetAzimuth

    # def repeatAzimuthLoop(self, feat_list):
    #     # из таблицы берем азимут и значение класса точки
    #     # сравниваем несколько точек по азимуту
    #     # az_list = self.fm.getAllFieldValuesAsList(self.templayer, self.fieldAz)
    #     # class_list = self.fm.getAllFieldValuesAsList(self.templayer, self.fieldClass)
    #
    #     prev1 = 0
    #     prev2 = 1
    #     i = 2
    #     while i < len(feat_list) - 2:
    #
    #         pass
    #         prev1 = prev2
    #         prev2 = i
    #         i += 1

    def azimuthLoop(self, feat_list, numPass):
        i = 1
        prev_ind = 0
        az = AzimutMathUtil()
        control_flights = []
        data_format = '%Y/%m/%d %H:%M:%S.%f'

        self.fm.setFieldValue(feat_list[0], self.fieldClass, 'первая точка')  # первая точка - точка взлета
        prev_date = datetime.strptime(feat_list[0].GetField('TIME'), data_format)

        while i < len(feat_list):
            # self.log_lines.append('\n\nИтерация № ' + str(i))
            dist = az.distanceCalc([feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                                   [feat_list[i].geometry().GetX(),
                                    feat_list[i].geometry().GetY()])
            cur_date = datetime.strptime(feat_list[i].GetField('TIME'), data_format)

            # self.log_lines.append('\nРасстояние между точками = ' + str(dist))
            # self.log_lines.append('\nПредыдущая дата: ' + str(prev_date))
            # self.log_lines.append('\nТекущая дата: ' + str(cur_date))

            period = cur_date - prev_date
            if dist > 10 and period.total_seconds() < 60:
                # self.log_lines.append('\nВыполнилось условие dist > 10 и разница во времени < 60 сек для i = '+str(i))
                control_flights.append(feat_list[i])
            else:
                # self.log_lines.append('\nВыполнилось условие else для i = ' + str(i))
                azimuth_1 = az.azimutCalc(
                    [feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                    [feat_list[i].geometry().GetX(),
                     feat_list[i].geometry().GetY()])

                # self.log_lines.append('\nЗначение азимута: ' + str(azimuth_1))

                # dX = feat_list[i + step].geometry().GetX() - feat_list[i].geometry().GetX()
                # dY = feat_list[i + step].geometry().GetY() - feat_list[i].geometry().GetY()

                # dX = feat_list[i].geometry().GetX()
                # dY = feat_list[i].geometry().GetY()

                # Запишем значение азимута и номера фактора в отдельный столбец
                # self.fm.setFieldValue(feat_list[i], self.fieldNum, i)
                # self.fm.setFieldValue(feat_list[i], self.fieldAz, azimuth_1)
                # # self.setFieldValue(feat_list[i], self.fieldDx, dX)
                # # self.setFieldValue(feat_list[i], self.fieldDy, dY)
                # self.fm.setFieldValue(feat_list[i], self.fieldDist, dist)
                # self.fm.setFieldValue(feat_list[i], self.fieldPass, numPass)

                # self.log_lines.append('\nПроход цикла № ' + str(numPass))

                if math.fabs(self.targetAzimuth - azimuth_1) <= self.accuracy:
                    self.fm.setFieldValue(feat_list[i], self.fieldClass, 'азимут<180')
                    # self.log_lines.append('\nПрисвоено: азимут<180')
                elif math.fabs(self.targetAzimuth + 180 - azimuth_1) <= self.accuracy:
                    self.fm.setFieldValue(feat_list[i], self.fieldClass, 'азимут>180')
                    # self.log_lines.append('\nПрисвоено: азимут>180')
                else:
                    self.fm.setFieldValue(feat_list[i], self.fieldClass, 'несовпадение азимута')
                    # self.log_lines.append('\nПрисвоено: несовпадение азимута')
                    # self.delFeatByID(feat_list[i].GetFID())

                prev_ind = i
                prev_date = cur_date

            i += 1

        return control_flights

    def mainAzimutCalc(self):
        self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем классификацию точек...')

        # создаем новый столбец
        # self.fm.createNewField(self.fieldNum, ogr.OFTInteger)
        self.fm.createNewField(self.fieldAz, ogr.OFTReal)
        self.fm.createNewField(self.fieldClass, ogr.OFTString)
        # # self.createNewField(self.fieldDx, ogr.OFTReal)
        # # self.createNewField(self.fieldDy, ogr.OFTReal)
        # self.fm.createNewField(self.fieldDist, ogr.OFTReal)
        # self.fm.createNewField(self.fieldPass, ogr.OFTInteger)

        # переместим фичи из временного слоя в список
        feat_list = self.fm.tempLayerToListFeat(self.templayer)

        # отсортируем список по времени
        feat_list = self.fm.sortListByLambda(feat_list, 'TIME')

        # вычислим целевой азимут
        self.targetAzimuth = self.getMostFreqAzimuth(feat_list)
        self.guiUtil.setOutputStyle('black', 'normal', 'Целевой азимут: ' + str(self.targetAzimuth))

        # проходим по всем азимутам и сравниваем с целевым
        num_pass = 1
        control_flights = self.azimuthLoop(feat_list, num_pass)

        # self.guiUtil.setOutputStyle('black', 'normal', str(len(control_flights)))

        # повторяем процедуру для полетов, совершенных одновременно
        while len(control_flights) > 0:
            num_pass += 1
            control_flights = self.azimuthLoop(control_flights, num_pass)
            # self.guiUtil.setOutputStyle('black', 'normal', str(len(control_flights)))

        # LogFileTool().writeToLog(self.log_lines)

        # делаем обход "окном сглаживания" еще раз
        # для того чтобы очистить точки внутри профилей от ошибочно забракованных
        # self.repeatAzimuthLoop(feat_list)

        self.guiUtil.setOutputStyle('green', 'bold', 'Точки успешно классифицированы!')
        self.outDS.SyncToDisk()
