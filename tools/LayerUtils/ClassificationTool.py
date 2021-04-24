import math
import dateutil.parser
import os
from osgeo import ogr, osr

from .AzimutMathUtil import AzimutMathUtil
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
        while i < len(feat_list):
            a = self.getAzimuth(feat_list[prev_ind], feat_list[i])
            z = int((a + step / 2) % 360 // step) * 10
            res.append(z)

            prev_ind = i
            i += 1

        targetAzimuth = max(set(res), key=res.count)
        if targetAzimuth > 180:
            targetAzimuth -= 180
        return targetAzimuth

    def getAzimuth(self, prev_i, curr_i):
        azimuth = AzimutMathUtil().azimutCalc([prev_i.geometry().GetX(), prev_i.geometry().GetY()],
                                              [curr_i.geometry().GetX(), curr_i.geometry().GetY()])
        return azimuth

    def getDistance(self, prev_i, curr_i):
        dist = AzimutMathUtil().distanceCalc([prev_i.geometry().GetX(), prev_i.geometry().GetY()],
                                             [curr_i.geometry().GetX(), curr_i.geometry().GetY()])
        return dist

    def getDate(self, elem):
        date = dateutil.parser.parse(elem.GetField('TIME'))
        return date

    def getSpeed(self, prev_i, curr_i):
        dist = self.getDistance(prev_i, curr_i)
        period = self.getDate(curr_i) - self.getDate(prev_i)

        if period.total_seconds() != 0:
            speed = dist / period.total_seconds()
            return speed
        else:
            return 99999

    def classify(self, azimuth, speed):
        if math.fabs(self.targetAzimuth - azimuth) <= self.accuracy:
            return 4
        elif math.fabs(self.targetAzimuth + 180 - azimuth) <= self.accuracy:
            return 3
        elif speed < 0.000001:
            return 0
        else:
            return 2

    def azimuthLoop(self, feat_list, numPass):
        control_flights = []

        # первая точка:
        feat_list[0].SetField(self.fieldClass, 1)  # первая точка - точка взлета
        feat_list[0].SetField(self.fieldGlobalNum, self.global_num)
        self.global_num += 1

        # создадим окно сглаживания
        window = BufferAzimuth(self.bufSize, self.targetAzimuth, self.accuracy)

        prev_date = self.getDate(feat_list[0])

        j = 0
        prev_ind = 0
        i = 1

        while i < len(feat_list):
            dist = self.getDistance(feat_list[prev_ind], feat_list[i])
            cur_date = self.getDate(feat_list[i])
            period = cur_date - prev_date
            if period.total_seconds() != 0:
                cur_speed = dist / period.total_seconds()
            else:
                cur_speed = 156634

            # feat_list[i].SetField(self.fieldSpeed, cur_speed)

            if dist > 10 and period.total_seconds() < 60:
                control_flights.append(feat_list[i])
            else:
                azimuth = self.getAzimuth(feat_list[prev_ind], feat_list[i])

                # Запишем значение азимута и номера фактора в отдельный столбец
                feat_list[i].SetField(self.fieldGlobalNum, self.global_num)

                # маркировка без окна сглаживания
                # feat_list[i].SetField(self.fieldAz, azimuth)
                # feat_list[i].SetField(self.fieldClass, self.classify(azimuth, cur_speed))

                window.addElem(azimuth)
                j = i - self.bufSize
                if j >= 0:
                    # feat_list[j].SetField(self.fieldAzAvg, window.getAverage())
                    feat_list[j].SetField(self.fieldClass, self.classify(window.getAverage(), cur_speed))

                prev_ind = i
                prev_date = cur_date
                # prev_speed = cur_speed

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
            # self.fm.createNewField(self.fieldCurSpeed, ogr.OFTReal)
            # self.fm.createNewField(self.fieldAvgSpeed, ogr.OFTReal)

            if checkBox_numProfiles.isChecked():
                self.fm.createNewField(self.fieldNum, ogr.OFTInteger)

            # переместим фичи из временного слоя в список
            feat_list = self.fm.tempLayerToListFeat(self.templayer)

            # отсортируем список по времени
            feat_list = self.fm.sortListByLambda(feat_list, 'TIME')

            # вычислим целевой азимут
            try:
                self.targetAzimuth = self.getMostFreqAzimuth(feat_list)
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
                    if num_pass > 100:
                        self.guiUtil.setOutputStyle('red', 'bold', '\nЗациклился!')
                        break
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


