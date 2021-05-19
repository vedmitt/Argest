import math
import dateutil.parser

from .AzimutMathUtil import AzimutMathUtil
from .BufferAzimuth import BufferAzimuth
from .FeaturesList import FeaturesList


class ClassificationTool:

    def __init__(self, guiUtil):
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
        self.guiUtil = guiUtil

    def numerateProfiles(self, features):
        self.guiUtil.setOutputStyle([0, '\nНачинаем нумерацию профилей... '])
        i = 1
        features.sortListByLambda(self.fieldGlobalNum)
        isProfile = False
        profileNum = 1

        while i < features.getFeatureCount():
            if features.getFeature(i).getValue(self.fieldClass) == 4 or features.getFeature(i).getValue(self.fieldClass) == 3:
                isProfile = True
                features.setFeature(i, self.fieldNum, profileNum)
            else:
                if isProfile:
                    profileNum += 1
                isProfile = False
            i += 1

        self.guiUtil.setOutputStyle([1, 'Профиля успешно пронумерованы!'])
        return features

    def getMostFreqAzimuth(self, feat_list):
        step = 10
        res = []
        i = 1
        prev_ind = 0
        while i < feat_list.getFeatureCount():
            a = self.getAzimuth(feat_list.getFeature(prev_ind), feat_list.getFeature(i))
            z = int((a + step / 2) % 360 // step) * 10
            res.append(z)

            prev_ind = i
            i += 1

        targetAzimuth = max(set(res), key=res.count)
        if targetAzimuth > 180:
            targetAzimuth -= 180
        return targetAzimuth

    def getAzimuth(self, prev_i, curr_i):
        azimuth = AzimutMathUtil().azimutCalc([prev_i.getGeometry()[0], prev_i.getGeometry()[1]],
                                              [curr_i.getGeometry()[0], curr_i.getGeometry()[1]])
        return azimuth

    def getDistance(self, prev_i, curr_i):
        dist = AzimutMathUtil().distanceCalc([prev_i.getGeometry()[0], prev_i.getGeometry()[1]],
                                             [curr_i.getGeometry()[0], curr_i.getGeometry()[1]])
        return dist

    def getDate(self, elem):
        date = dateutil.parser.parse(elem.getValue('TIME'))
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
        control_flights = FeaturesList(None, None)
        control_flights.setFields(feat_list.getFieldDict())

        # первая точка:
        feat_list.setFeature(0, self.fieldGlobalNum, self.global_num)
        feat_list.setFeature(0, self.fieldClass, 1)  # первая точка - точка взлета
        self.global_num += 1

        # создадим окно сглаживания
        window = BufferAzimuth(self.bufSize, self.targetAzimuth, self.accuracy)

        prev_date = self.getDate(feat_list.getFeature(0))

        j = 0
        prev_ind = 0
        i = 1
        # prev_speed = 20000

        while i < feat_list.getFeatureCount():
            dist = self.getDistance(feat_list.getFeature(prev_ind), feat_list.getFeature(i))
            cur_date = self.getDate(feat_list.getFeature(i))
            period = cur_date - prev_date

            if period.total_seconds() != 0:
                cur_speed = dist / period.total_seconds()
            else:
                cur_speed = 156634

            if dist > 10 and period.total_seconds() < 60:
                control_flights.addFeature(feat_list.getFeature(i))
            else:
                azimuth = self.getAzimuth(feat_list.getFeature(prev_ind), feat_list.getFeature(i))

                # Запишем значение номера фактора в отдельный столбец
                feat_list.setFeature(i, self.fieldGlobalNum, self.global_num)
                self.global_num += 1

                # маркировка без окна сглаживания
                feat_list.setFeature(i, self.fieldClass, self.classify(azimuth, cur_speed))

                window.addElem(azimuth)
                j = i - self.bufSize
                if j >= 0:
                    feat_list.setFeature(j, self.fieldClass, self.classify(window.getAverage(), cur_speed))

                prev_ind = i
                prev_date = cur_date
                # prev_speed = cur_speed

            i += 1
            # self.global_num += 1

        return control_flights

    def mainAzimutCalc(self, features, cb_num):
        # создаем новые столбцы, если они еще не созданы
        if self.fieldGlobalNum and self.fieldClass not in features.getFieldList():
            features.addNewField(self.fieldGlobalNum, 'Integer64')
            features.addNewField(self.fieldClass, 'Integer64')

            # отсортируем список по времени
            features.sortListByLambda('TIME')

            # вычислим целевой азимут
            try:
                # self.targetAzimuth = 30
                self.targetAzimuth = self.getMostFreqAzimuth(features)
                self.guiUtil.setOutputStyle([0, 'Целевой азимут: ' + str(self.targetAzimuth)])
            except Exception as err:
                self.guiUtil.setOutputStyle([-1, '\nНе удалось вычислить целевой азимут! ' + str(err)])

            # проходим по всем азимутам и сравниваем с целевым
            try:
                self.guiUtil.setOutputStyle([0, '\nНачинаем классификацию точек...'])
                num_pass = 1
                control_flights = self.azimuthLoop(features, num_pass)

                # повторяем процедуру для полетов, совершенных одновременно
                while control_flights.getFeatureCount() > 0:
                    num_pass += 1
                    control_flights = self.azimuthLoop(control_flights, num_pass)
                    if num_pass > 100:
                        self.guiUtil.setOutputStyle([-1, '\nЗациклился!'])
                        break

                self.guiUtil.setOutputStyle([1, 'Точки успешно классифицированы!'])
            except Exception as err:
                self.guiUtil.setOutputStyle([-1, '\nНе удалось классифицировать точки! ' + str(err)])

        if cb_num:
            try:
                if self.fieldGlobalNum and self.fieldClass in features.getFieldList() and self.fieldNum not in features.getFieldList():
                    features.addNewField(self.fieldNum, 'Integer64')
                    features = self.numerateProfiles(features)
            except Exception as err:
                self.guiUtil.setOutputStyle([-1, '\nНе удалось пронумеровать профиля! ' + str(err)])

        return features
