import os
from datetime import datetime

import ogr
from PyQt5.QtCore import QVariant
from qgis._core import QgsFeatureRequest, QgsVectorDataProvider, QgsField

from .AzCalcTool import AzCalcTool


class TimeCalcUtil:
    guiUtil = None

    def __init__(self, guiUtil):
        TimeCalcUtil.guiUtil = guiUtil

    def setFlightNumber(self, dataSource, layer):
        TimeCalcUtil.guiUtil.setTextEditStyle('black', 'normal', 'Начинаем нумерацию профилей...')

        # driver = ogr.GetDriverByName(drivername)
        # # if os.path.exists(layerpath):
        # #     driver.DeleteDataSource(layerpath)
        #
        # dataSource = driver.CreateDataSource(layerpath)
        # layerDS = driver.Open(layerpath, 1)  # 0 means read-only. 1 means writeable.
        #
        # layer = dataSource.GetLayer()
        # featureCount = layer.GetFeatureCount()

        # создаем новый столбец
        newField = 'FLIGHT_NUM'
        layer.addField(ogr.FieldDefn(newField, ogr.OFTInteger))

        # Переводим все фичи в список, сортируем по времени

        # Добавляем номера профилей
        i = 1
        boolYesNo = False
        prevFeat = None
        nextFeat = None

        for feat in layer:
            if feat.id() == 0:
                prevFeat = feat
            elif feat.id() == 1:
                nextFeat = feat
                boolYesNo = self.timeSort(prevFeat, nextFeat)
            else:
                prevFeat = nextFeat
                nextFeat = feat
                boolYesNo = self.timeSort(prevFeat, nextFeat)

            if (boolYesNo is False) and (nextFeat is not None):
                # add new flight number
                prevFeat.SetField(newField, i)
                nextFeat.SetField(newField, i)

                # attrs = {fieldNum: i}
                # self.changeFeatValues(layer, prevFeat.id(), attrs)
                # self.changeFeatValues(layer, nextFeat.id(), attrs)
            elif nextFeat is not None:
                i += 1
                # add new flight number
                nextFeat.SetField(newField, i)

                # attrs = {fieldNum: i}
                # self.changeFeatValues(layer, nextFeat.id(), attrs)

        dataSource.SyncToDisk()
        TimeCalcUtil.guiUtil.setTextEditStyle('black', 'normal', 'Профилей выделено: ' + str(i))
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
