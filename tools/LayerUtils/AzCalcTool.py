import math
from datetime import datetime

from PyQt5.QtCore import QVariant
from qgis._core import QgsVectorDataProvider, QgsFeatureRequest, QgsField

from .AzimutMathUtil import AzimutMathUtil


class AzCalcTool:
    outDS = None
    templayer = None
    guiUtil = None

    def __init__(self, outDS, templayer, guiUtil):
        AzCalcTool.outDS = outDS
        AzCalcTool.templayer = templayer
        AzCalcTool.guiUtil = guiUtil

    def removeZeroPointsFromMemory(self, boolChecked):
        # далее работаем с временным слоем
        # -------- удаляем нулевые точки ---------------
        if boolChecked:
            AzCalcTool.guiUtil.setTextEditStyle('black', 'normal', '\nНачинаем удаление нулевых точек...')
            for i in range(AzCalcTool.templayer.GetFeatureCount()):
                feat = AzCalcTool.templayer.GetNextFeature()
                if feat is not None:
                    geom = feat.geometry()
                    if geom.GetX() == 0.0 and geom.GetY() == 0.0:
                        AzCalcTool.templayer.DeleteFeature(feat.GetFID())
                        AzCalcTool.outDS.ExecuteSQL('REPACK ' + AzCalcTool.templayer.GetName())
                        # textEdit.append(str(feat.GetField("TIME")))
            AzCalcTool.templayer.ResetReading()

            AzCalcTool.guiUtil.setTextEditStyle('green', 'bold', 'Нулевые точки успешно удалены!')
            AzCalcTool.guiUtil.setTextEditStyle('black', 'normal', 'Количество точек после удаления нулевых: ' +
                                                str(AzCalcTool.templayer.GetFeatureCount()))
        AzCalcTool.outDS.SyncToDisk()

##------------------------------------------------------------------

    def mainAzimutCalc(self):
        global azimut_2
        AzCalcTool.guiUtil.setTextEditStyle('black', 'normal', '\nНачинаем удаление избыточных точек...')

        feat_list = []
        for i in range(AzCalcTool.templayer.GetFeatureCount()):
            feat = AzCalcTool.templayer.GetNextFeature()
            feat_list.append(feat)
        AzCalcTool.templayer.ResetReading()

        # отсортируем список по времени
        feat_list = sorted(feat_list, key=lambda feature: feature.GetField("TIME"), reverse=False)

        accuracy = 10
        flightList = []
        parts_list = []
        min_dist = 6.966525707833812e-08
        bad_paths = []
        i = 0
        az_temp = []
        avg_az_list = []
        while i + 2 < len(feat_list):
            azimut_1 = AzimutMathUtil().azimutCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
                                                   [feat_list[i + 1].geometry().GetX(),
                                                    feat_list[i + 1].geometry().GetY()])
            azimut_2 = AzimutMathUtil().azimutCalc([feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()],
                                                   [feat_list[i + 2].geometry().GetX(), feat_list[i + 2].geometry().GetY()])

            dist = AzimutMathUtil().distanceCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
                                                 [feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()])

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
                    avg_az_list.append(az_sum / len(az_temp))
                parts_list = [feat_list[i]]
                az_temp = [azimut_1]
            i += 1

        if parts_list is not None:
            parts_list.append(feat_list[i])
            parts_list.append(feat_list[i + 1])
            avg_az_list.append(azimut_2)
            flightList.append(parts_list)

        # удаляем аномальные пути в начале полетов
        for item in bad_paths:
            AzCalcTool.templayer.DeleteFeature(item)
            AzCalcTool.outDS.ExecuteSQL('REPACK ' + AzCalcTool.templayer.GetName())

        AzCalcTool.guiUtil.setTextEditStyle('black', 'normal',
                                              'Количество частей полетов: ' + str(len(flightList)))
        # textEdit.append('Количество усредненных азимутов: ' + str(len(avg_az_list)))
        longest_path = max(len(elem) for elem in flightList)
        AzCalcTool.guiUtil.setTextEditStyle('black', 'normal', 'Самый длинный полет: ' + str(longest_path))
        # shortest_path = min(len(elem) for elem in flightList)
        # textEdit.append('Самый короткий полет: ' + str(shortest_path))

        i_longest = 0
        for path in flightList:
            if len(path) == longest_path:
                i_longest = flightList.index(path)
                break

        target_az = avg_az_list[i_longest]
        AzCalcTool.guiUtil.setTextEditStyle('black', 'normal', 'Целевой азимут: ' + str(target_az))
        for i in range(len(avg_az_list)):
            if math.fabs(avg_az_list[i] - target_az) < accuracy or math.fabs(
                    (avg_az_list[i] + 180) - target_az) < accuracy:
                if len(flightList[i]) < 20:
                    for feat in flightList[i]:
                        AzCalcTool.templayer.DeleteFeature(feat.GetFID())
                        AzCalcTool.outDS.ExecuteSQL('REPACK ' + AzCalcTool.templayer.GetName())
            else:
                for feat in flightList[i]:
                    AzCalcTool.templayer.DeleteFeature(feat.GetFID())
                    AzCalcTool.outDS.ExecuteSQL('REPACK ' + AzCalcTool.templayer.GetName())

        # for i in range(len(avg_az_list)):
        #     textEdit.append(str(avg_az_list[i]))

        # while i + 2 < len(avg_az_list):
        #     if math.fabs(avg_az_list[i] - avg_az_list[i+1]) < 90 \
        #             or math.fabs(avg_az_list[i+1] - avg_az_list[i+2]) < 90:
        #         if len(flightList[i]) > len(flightList[i+1]) and len(flightList[i+2]) > len(flightList[i+1]):
        #             for feat in flightList[i+1]:
        #                 templayer.DeleteFeature(feat.GetFID())
        #                 outDS.ExecuteSQL('REPACK ' + templayer.GetName())
        #     else:
        #         for feat in flightList[i]:
        #             templayer.DeleteFeature(feat.GetFID())
        #             outDS.ExecuteSQL('REPACK ' + templayer.GetName())

        # for path in flightList:
        #     if len(path) < longest_path / 2:
        #         for feat in path:
        #             templayer.DeleteFeature(feat.GetFID())
        #             outDS.ExecuteSQL('REPACK ' + templayer.GetName())

        AzCalcTool.guiUtil.setTextEditStyle('green', 'bold', 'Избыточные точки успешно удалены!')
        AzCalcTool.guiUtil.setTextEditStyle('black', 'normal', '\nКоличество точек в полученном слое: ' +
                                            str(AzCalcTool.templayer.GetFeatureCount()))
        AzCalcTool.outDS.SyncToDisk()
