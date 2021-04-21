import math
from datetime import datetime
import dateutil.parser
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
        self.accuracy = 5
        # self.log_lines = []
        self.fieldGlobalNum = "GLOBAL_NUM"
        self.fieldNum = "FLIGHT_NUM"
        self.fieldClass = "CLASS"
        self.fieldCurSpeed = "CUR_SPEED"
        self.fieldAvgSpeed = "AVG_SPEED"
        self.targetAzimuth = 0
        self.outDS = outDS
        self.templayer = templayer
        self.filename = filename
        self.filepath = filepath
        self.guiUtil = guiUtil
        self.fm = FeatureManagement(self.outDS, self.templayer, self.guiUtil)

    def saveFeatListToFile(self, feat_list, templayer, filename, filepath, checkBox_delete):
        # -------- сохраняем результат в шейпфайл (код рабочий) ----------------------
        # self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем сохранение файла...')

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
                if feature.GetField(self.fieldClass) == 4 \
                        or feature.GetField(self.fieldClass) == 3:
                    newlayer.CreateFeature(feature)
            else:
                newlayer.CreateFeature(feature)

        if checkBox_delete.isChecked():
            self.guiUtil.setOutputStyle('green', 'bold', '\nТочки долетов/отлетов успешно удалены!')
        self.guiUtil.setOutputStyle('black', 'normal', '\nФайл успешно сохранен!')

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
            if feat_list[i].GetField(self.fieldClass) == 4 or feat_list[i].GetField(self.fieldClass) == 3:
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
            return 4
        elif math.fabs(self.targetAzimuth + 180 - azimuth) <= self.accuracy:
            return 3
        elif speed == 0.0:
            return 0
        else:
            return 2

    def azimuthLoop(self, feat_list, numPass):
        prev_ind = 0
        i = 1
        az = AzimutMathUtil()
        control_flights = []
        prev_date = dateutil.parser.parse(feat_list[0].GetField('TIME'))

        feat_list[0].SetField(self.fieldClass, 1)  # первая точка - точка взлета
        feat_list[0].SetField(self.fieldGlobalNum, self.global_num)
        self.global_num += 1
        # extra fields:
        feat_list[0].SetField(self.fieldCurSpeed, 0)
        feat_list[0].SetField(self.fieldAvgSpeed, 0)

        # создадим окно сглаживания
        window = BufferAzimuth(self.bufSize, self.targetAzimuth, self.accuracy)

        j = 0
        avg_speed_sum = 0
        while i < len(feat_list):
            dist = az.distanceCalc([feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                                   [feat_list[i].geometry().GetX(),
                                    feat_list[i].geometry().GetY()])
            cur_date = dateutil.parser.parse(feat_list[i].GetField('TIME'))
            period = cur_date - prev_date
            if period.total_seconds() != 0:
                cur_speed = dist / period.total_seconds()
            # else:
            #     cur_speed = 156634

            avg_speed_sum += cur_speed
            avg_speed = avg_speed_sum / i

            # запишем значение скорости текущей и средней
            feat_list[i].SetField(self.fieldCurSpeed, cur_speed)
            feat_list[i].SetField(self.fieldAvgSpeed, avg_speed)

            if cur_speed > avg_speed * 2:
            # if dist > 10 and period.total_seconds() < 60:
                control_flights.append(feat_list[i])
            else:
                azimuth = az.azimutCalc(
                    [feat_list[prev_ind].geometry().GetX(), feat_list[prev_ind].geometry().GetY()],
                    [feat_list[i].geometry().GetX(),
                     feat_list[i].geometry().GetY()])

                # Запишем значение азимута и номера фактора в отдельный столбец
                feat_list[i].SetField(self.fieldGlobalNum, self.global_num)

                # маркировка без окна сглаживания
                # feat_list[i].SetField(self.fieldAz, azimuth)
                # feat_list[i].SetField(self.fieldClass, self.classify(azimuth, cur_speed))

                window.addElem(azimuth)
                j = i - self.bufSize
                if j >= 0:
                    feat_list[j].SetField(self.fieldClass, self.classify(window.getAverage(), cur_speed))

                prev_ind = i
                prev_date = cur_date
                prev_speed = cur_speed

            i += 1
            self.global_num += 1

            j += 1
            while 0 <= j < i:
                feat_list[j].SetField(self.fieldClass, self.classify(window.getAverage(), cur_speed))
                j += 1

        return control_flights

    def mainAzimutCalc(self, checkBox_delete, checkBox_numProfiles):
        self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем классификацию точек...')

        # создаем новые столбцы, если они еще не созданы
        layerDefinition = self.templayer.GetLayerDefn()
        fields_list = [layerDefinition.GetFieldDefn(n).name for n in range(layerDefinition.GetFieldCount())]
        feat_list = []

        if self.fieldGlobalNum and self.fieldClass not in fields_list:
            self.fm.createNewField(self.fieldGlobalNum, ogr.OFTInteger)
            self.fm.createNewField(self.fieldClass, ogr.OFTInteger)
            # extra fields:
            self.fm.createNewField(self.fieldCurSpeed, ogr.OFTReal)
            self.fm.createNewField(self.fieldAvgSpeed, ogr.OFTReal)

            if checkBox_numProfiles.isChecked():
                self.fm.createNewField(self.fieldNum, ogr.OFTInteger)

            # переместим фичи из временного слоя в список
            feat_list = self.fm.tempLayerToListFeat(self.templayer)

            # отсортируем список по времени
            feat_list = self.fm.sortListByLambda(feat_list, 'TIME')

            # вычислим целевой азимут
            try:
                self.targetAzimuth = 30
                # self.targetAzimuth = self.getMostFreqAzimuth(feat_list)
                self.guiUtil.setOutputStyle('black', 'normal', 'Целевой азимут: ' + str(self.targetAzimuth))
            except Exception as err:
                self.guiUtil.setOutputStyle('red', 'bold', '\nНе удалось вычислить целевой азимут! ' + str(err))

            # проходим по всем азимутам и сравниваем с целевым
            try:
                num_pass = 1
                control_flights = self.azimuthLoop(feat_list, num_pass)

                # self.guiUtil.setOutputStyle('black', 'normal', str(len(control_flights)))

                # повторяем процедуру для полетов, совершенных одновременно
                while len(control_flights) > 0:
                    num_pass += 1
                    control_flights = self.azimuthLoop(control_flights, num_pass)
                    # self.guiUtil.setOutputStyle('black', 'normal', str(len(control_flights)))

                self.guiUtil.setOutputStyle('green', 'bold', 'Точки успешно классифицированы!')
            except Exception as err:
                self.guiUtil.setOutputStyle('red', 'bold', '\nНе удалось классифицировать точки! ' + str(err))

        if checkBox_numProfiles.isChecked():
            if self.fieldGlobalNum and self.fieldClass in fields_list and self.fieldNum not in fields_list:
                self.fm.createNewField(self.fieldNum, ogr.OFTInteger)
                # переместим фичи из временного слоя в список
                feat_list = self.fm.tempLayerToListFeat(self.templayer)
            # сортируем по глобальному номеру и нумеруем профиля
            feat_list = self.numerateProfiles(feat_list)

        # если файл уже был обработан, все равно сохраним его
        if len(feat_list) == 0:
            feat_list = self.fm.tempLayerToListFeat(self.templayer)

        # сохраним основной файл (в любом случае)
        try:
            self.saveFeatListToFile(feat_list, self.templayer, self.filename, self.filepath, checkBox_delete)
        except Exception as err:
            self.guiUtil.setOutputStyle('red', 'bold', '\nНе удалось сохранить/загрузить файл! ' + str(err))


