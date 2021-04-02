import math
from datetime import datetime
import os
from osgeo import ogr, osr

from .AzimutMathUtil import AzimutMathUtil
from .LayerManagement import LayerManagement
from .LogFileTool import LogFileTool
from .FeatureManagement import FeatureManagement
from .BufferAzimuth import BufferAzimuth


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

    def saveFeatListToFile(self, feat_list, templayer, filename, filepath, checkBox_delete):
        # -------- сохраняем результат в шейпфайл (код рабочий) ----------------------
        self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем сохранение файла...')

        fileDriver = ogr.GetDriverByName('ESRI Shapefile')

        # если слой уже существует и загружен, то удаляем его из проекта
        # for layer in QgsProject.instance().mapLayers().values():
        #     if layer.name() == filename:
        #         QgsProject.instance().removeMapLayers([layer.id()])
        #         # break

        if os.path.exists(filepath):
            fileDriver.DeleteDataSource(filepath)

        fileDS = fileDriver.CreateDataSource(filepath)
        newDS = fileDriver.Open(filepath, 1)

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(28420)
        newlayer = fileDS.CreateLayer(filename, srs, ogr.wkbPoint)

        # newlayer = fileDS.CopyLayer(templayer, filename, ['OVERWRITE=YES'])

        inLayerDefn = templayer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()
            newlayer.CreateField(fieldDefn)

        for feature in feat_list:
            if checkBox_delete.isChecked():
                if feature.GetField(self.fieldClass) == 'азимут<180' \
                        or feature.GetField(self.fieldClass) == 'азимут>180':
                    newlayer.CreateFeature(feature)

        self.guiUtil.setOutputStyle('black', 'normal', 'Файл успешно сохранен!')

        if newlayer is not None:
            self.guiUtil.uploadLayer(filepath, filename, 'ogr')
            self.guiUtil.setOutputStyle('green', 'bold', 'Слой успешно загружен в QGIS!')

        # del outDS, newDS, fileDS

    def numerateProfiles(self, feat_list):
        self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем нумерацию профилей... ')
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

        self.guiUtil.setOutputStyle('green', 'bold', 'Профиля успешно пронумерованы!')
        return feat_list

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

    def classify(self, azimuth, speed):
        if math.fabs(self.targetAzimuth - azimuth) <= self.accuracy:
            return 'азимут<180'
        elif math.fabs(self.targetAzimuth + 180 - azimuth) <= self.accuracy:
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

        # создадим окно сглаживания
        window = BufferAzimuth(self.bufSize, self.targetAzimuth, self.accuracy)

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

                window.addElem(azimuth)
                j = i - self.bufSize
                if j >= 0:
                    feat_list[j].SetField(self.fieldAzAvg, window.getAverage())
                    feat_list[j].SetField(self.fieldClass, self.classify(window.getAverage(), cur_speed))

                prev_ind = i
                prev_date = cur_date
                prev_speed = cur_speed

            i += 1
            self.global_num += 1

        return control_flights

    def mainAzimutCalc(self, checkBox_delete, checkBox_numProfiles):
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
        self.fm.createNewField(self.fieldClass, ogr.OFTString)

        if checkBox_numProfiles.isChecked():
            self.fm.createNewField(self.fieldNum, ogr.OFTInteger)

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
        # self.outDS.SyncToDisk()

        # сортируем по глобальному номеру и нумеруем профиля
        if checkBox_numProfiles.isChecked():
            feat_list = self.numerateProfiles(feat_list)

        # сохраним основной файл
        try:
            self.saveFeatListToFile(feat_list, self.templayer, self.filename, self.filepath, checkBox_delete)
        except Exception as err:
            self.guiUtil.setOutputStyle('red', 'bold', '\nНе удалось сохранить/загрузить файл! ' + str(err))


