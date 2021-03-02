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

        # создаем новый столбец
        newField = 'FLIGHT_NUM'
        fieldDefn = ogr.FieldDefn(newField, ogr.OFTInteger)
        layer.CreateField(fieldDefn)

        # Переводим все фичи в список, сортируем по времени
        az = AzCalcTool(dataSource, layer, None)
        feat_list = az.tempLayerToListFeat(layer)
        feat_list = az.sortListByLambda(feat_list, 'TIME')

        # Добавляем номера профилей
        i = 0
        flight_num = 1

        while i+1 < len(feat_list):
            # boolYesNo = self.timeSort(feat_list[i], feat_list[i+1])
            dist = AzimutMathUtil().distanceCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
                                                 [feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()])

            # if (boolYesNo is False) and (feat_list[i+1] is not None):
            if dist > 0.0003:
                # добавить номер профиля (новый)
                flight_num += 1
                feat_list[i + 1].SetField(newField, flight_num)
                layer.SetFeature(feat_list[i + 1])
            else:
                # добавить номер профиля
                feat_list[i].SetField(newField, flight_num)
                feat_list[i + 1].SetField(newField, flight_num)
                layer.SetFeature(feat_list[i])
                layer.SetFeature(feat_list[i + 1])
            i += 1

        dataSource.SyncToDisk()
        TimeCalcUtil.guiUtil.setTextEditStyle('black', 'normal', 'Профилей выделено: ' + str(flight_num))
        TimeCalcUtil.guiUtil.setTextEditStyle('green', 'bold', 'Нумерация профилей завершена!')

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
