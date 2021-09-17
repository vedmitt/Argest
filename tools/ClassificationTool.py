import math
import dateutil.parser

from .mathUtil.AzimutMathUtil import AzimutMathUtil
from .mathUtil.BufferAzimuth import BufferAzimuth
from .dataStorage.FeaturesList import FeaturesList
from .mathUtil.DataTimeUtil import DataTimeUtil


class ClassificationTool:

    def __init__(self, accuracy, bufSize, timeField, shouldBeNumerated, isAbsolutData, guiUtil):
        self.global_num = 0
        self.accuracy = accuracy
        self.bufSize = bufSize
        self.timeField = timeField
        self.shouldBeNumerated = shouldBeNumerated
        self.isAbsolutData = isAbsolutData
        self.fieldGlobalNum = "GLOBAL_NUM"
        self.fieldNum = "FLIGHT_NUM"
        self.fieldClass = "CLASS"
        self.targetAzimuth = 0
        self.guiUtil = guiUtil

    def numerateProfiles(self, features):
        self.guiUtil.setOutputStyle([0, '\nНачинаем нумерацию профилей... '])
        i = 1
        features.sortByField(self.fieldGlobalNum)
        isProfile = False
        profileNum = 1

        while i < features.featureCount():
            if features.getFeatureValue(i, self.fieldClass) == 4 or features.getFeatureValue(i, self.fieldClass) == 3:
                isProfile = True
                features.setFeature(i, self.fieldNum, profileNum)
            else:
                if isProfile:
                    profileNum += 1
                isProfile = False
            i += 1

        self.guiUtil.setOutputStyle([1, 'Профиля успешно пронумерованы!'])
        return features

        # self.guiUtil.setOutputStyle([0, '\nНачинаем нумерацию профилей... '])
        # # features.addNewField('AZ_DIFF', 'Real')
        # prev = 0
        # i = 1
        # # features.sortByField('DEV')
        # profileNum = 1
        # features.setFeature(prev, self.fieldNum, profileNum)
        #
        # while i < features.featureCount()-1:
        #     az = AzimutMathUtil()
        #     prev_az = az.getAzimuth(features.getFeature(prev), features.getFeature(i))
        #     cur_az = az.getAzimuth(features.getFeature(i), features.getFeature(i+1))
        #     diff = math.fabs(cur_az - prev_az)
        #     # features.setFeature(i, 'AZ_DIFF', diff)
        #     # self.guiUtil.setOutputStyle([0, str(diff)])
        #     if diff < 90:
        #         features.setFeature(i, self.fieldNum, profileNum)
        #     else:
        #         profileNum += 1
        #         features.setFeature(i, self.fieldNum, profileNum)
        #     prev = i
        #     i += 1
        #
        # features.setFeature(i, self.fieldNum, profileNum)
        # self.guiUtil.setOutputStyle([1, 'Профиля успешно пронумерованы!'])
        # return features

    def classify(self, azimuth, speed):
        if math.fabs(self.targetAzimuth - azimuth) <= self.accuracy:
            return 4
        elif math.fabs(self.targetAzimuth + 180 - azimuth) <= self.accuracy:
            return 3
        elif speed < 0.000001:
            return 0
        else:
            return 2

    def classifyPoints(self, feat_list, numPass):
        az = AzimutMathUtil()
        control_flights = FeaturesList(feat_list.getFields(), feat_list.getFieldTypes(), None)

        # первая точка:
        feat_list.setFeature(0, self.fieldGlobalNum, self.global_num)
        feat_list.setFeature(0, self.fieldClass, 1)  # первая точка - точка взлета
        self.global_num += 1

        # создадим окно сглаживания
        window = BufferAzimuth(self.bufSize, self.targetAzimuth, self.accuracy)

        if self.isAbsolutData:
            prev_date = float(feat_list.getFeatureValue(0, self.timeField))
            diff_sec = 0.0002
        else:  # если дата обычная в одну строку в формате датаТвремя
            prev_date = DataTimeUtil().getDate(feat_list.getFeatureValue(0, self.timeField))
            diff_sec = 60

        j = 0
        prev_ind = 0
        i = 1
        # prev_speed = 20000

        while i < feat_list.featureCount():
            dist = az.getDistance(feat_list.getFeature(prev_ind), feat_list.getFeature(i))

            if self.isAbsolutData:
                cur_date = float(feat_list.getFeatureValue(i, self.timeField))
            else:
                cur_date = DataTimeUtil().getDate(feat_list.getFeatureValue(i, self.timeField))

            period = cur_date - prev_date

            if self.isAbsolutData:
                if period != 0:
                    cur_speed = dist / period
                else:
                    cur_speed = 156634
            else:
                if period.total_seconds() != 0:
                    cur_speed = dist / period.total_seconds()
                else:
                    cur_speed = 156634

            # if dist > 10 and period.total_seconds() < 60:
            if dist > 10 and period < diff_sec:
                control_flights.addFeature(feat_list.getFeature(i))
            else:
                azimuth = az.getAzimuth(feat_list.getFeature(prev_ind), feat_list.getFeature(i))

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

    def mainAzimutCalc(self, features):
        # создаем новые столбцы, если они еще не созданы
        if self.fieldGlobalNum and self.fieldClass not in features.getFields():
            features.addNewField(self.fieldGlobalNum, 'Integer64')
            features.addNewField(self.fieldClass, 'Integer64')

        # отсортируем список по времени
        features.sortByField(self.timeField)

        # вычислим целевой азимут
        # self.targetAzimuth = 110
        self.targetAzimuth = AzimutMathUtil().calcTargetAzimuth(features)
        self.guiUtil.setOutputStyle([0, 'Целевой азимут: ' + str(self.targetAzimuth)])

        # проходим по всем азимутам и сравниваем с целевым
        self.guiUtil.setOutputStyle([0, '\nНачинаем классификацию точек...'])
        num_pass = 1
        control_flights = self.classifyPoints(features, num_pass)

        # повторяем процедуру для полетов, совершенных одновременно
        while control_flights.featureCount() > 0:
            num_pass += 1
            control_flights = self.classifyPoints(control_flights, num_pass)
            if num_pass > 100:
                self.guiUtil.setOutputStyle([-1, '\nЗациклился!'])
                break
        self.guiUtil.setOutputStyle([1, 'Точки успешно классифицированы!'])

        # if self.shouldBeNumerated:
        # if self.fieldGlobalNum and self.fieldClass in features.getFields() \
        #         and self.fieldNum not in features.getFields():
        features.addNewField(self.fieldNum, 'Integer64')

        # # выясним сколько групп полетов имеет один слой
        # flights = features.getVectorOfValues('DEV')
        # flights = list(set(flights))
        # # guiUtil.setOutputStyle([0, '\n' + str(flights)])
        #
        # out_fields = features.getFields()
        # types = features.getFieldTypes()
        # g1_entries = features.selectValueByCondition(out_fields, ['DEV', flights[0]])
        # features = FeaturesList(out_fields, types, g1_entries)

        features = self.numerateProfiles(features)

        return features
