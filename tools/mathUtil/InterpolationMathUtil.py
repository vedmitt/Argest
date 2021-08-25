import math
from statistics import *
import copy
import numpy as np
from sklearn.metrics import mean_squared_error


class InterpolationMathUtil:

    def __init__(self, guiUtil=None):
        self.guiUtil = guiUtil

    def rotateTransform(self, x, y, deg_ccw):
        angle = math.radians(-deg_ccw)

        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)

        new_w = cos_theta * x - sin_theta * y
        new_h = sin_theta * x + cos_theta * y

        return new_w, new_h

    def affineCoordinate(self, feat_list, targetAzimuth):
        new_coordinates = []
        angle = 90 - targetAzimuth
        # сортируем по X
        feat_list.sortByField('LON')
        Ox = feat_list.getFeature(0).getGeometry()[0]
        Oy = feat_list.getFeature(0).getGeometry()[1]
        for feat in feat_list.getFeatures():
            fg = feat.getGeometry()
            dx = fg[0] - Ox
            dy = fg[1] - Oy
            new_x, new_y = self.rotateTransform(dx, dy, angle)
            new_coordinates.append([new_x, new_y])
            # new_coordinates.append([fg.asPoint()[0], fg.asPoint()[1]])
        return new_coordinates

    def findClosestNeighbours(self, vector, x):
        d = [math.fabs(x - i) for i in vector]
        dmin1 = min(d)
        dind1 = d.index(dmin1)
        f = copy.deepcopy(d)
        f.remove(dmin1)
        dmin2 = min(f)
        dind2 = d.index(dmin2)
        return [dmin1, dind1], [dmin2, dind2]

    def getAverageByList(self, list):  # среднее арифметическое значений массива
        return mean(list)

    def calcPSD(self, list):  # population standard deviation (the square root of the population variance)
        if len(list) > 0:
            # return pstdev(list)
            # return stdev(list)
            return np.std(list)
        else:
            return None

    def calcMeanDeviation(self, N, y_actual, y_predicted):  # среднее отклонение
        if len(y_actual) > 0 and len(y_predicted) > 0:
            summa = 0
            i = 0
            while i < N:
                summa = summa + math.fabs(y_predicted[i] - y_actual[i])
                i += 1
            res = summa / N
            return res
        else:
            return None

    def calcRMSE(self, y_actual, y_predicted):  # среднеквадртичное отклонение
        # rms = math.sqrt(mean_squared_error(y_actual, y_predicted))
        rms = mean_squared_error(y_actual, y_predicted)
        return rms

    def calcInterpolation(self, x, points, values):  # return y_predicted
        if (len(points) > 0 and len(values) > 0) and (len(points) == len(values)):
            return np.interp(x, points, values)
        else:
            return []

    def interpolatePoint(self, x, x1, y1, x2, y2):
        return y1 + (x - x1) * ((y2 - y1) / (x2 - x1))

    def interpolation_func(self, x, X1, X2, Y1, Y2):  # линейная интерполяция
        if Y1 == None or Y2 == None:
            return None
        elif (X2 - X1) == 0:
            return 0
        else:
            Tx = self.interpolatePoint(x, X1, X2, Y1, Y2)
            return Tx

    def interpolate_loop(self, features, Y, num_profile, xfield, out_fields):
        n = features.featureCount()
        Tx1_X_values = []
        i = 0  # бегунок для всех точек массива features
        k = 1  # бегунок для массива Y
        while i < n:
            # проходим по всем точкам нужного нам профиля и считаем Тх
            if features.getFeature(i).getValue('FLIGHT_NUM') == num_profile:
                # self.guiUtil.setOutputStyle([0, '\ni = ' + str(i)])
                # self.guiUtil.setOutputStyle([0, 'k = ' + str(k)])

                T1 = Y[k - 1][0]
                x1 = Y[k - 1][1]
                # self.guiUtil.setOutputStyle([0, 'y_actual = ' + str(y_actual)])

                T2 = Y[k][0]
                x2 = Y[k][1]
                # self.guiUtil.setOutputStyle([0, 'y_predicted = ' + str(y_predicted)])

                x = features.getFeature(i).getValue(xfield)
                Tx = self.interpolation_func(x, x1, x2, T1, T2)
                Tx1_X_values.append([Tx, x])
                features.setFeature(i, out_fields, Tx)

                k += 1
                if k > len(Y) - 1:
                    k = len(Y) - 1
            i += 1
        return Tx1_X_values

    def interpolate_mainFunc(self, features, numbers, tfield, xfield, out_fields):
        # общее количество точек
        # n = features.featureCount()
        # self.guiUtil.setOutputStyle([0, 'n = ' + str(n)])

        # массив значений Т и Х необходимые для расчетов
        Y = features.selectValueByCondition([tfield, xfield], ['FLIGHT_NUM', numbers[1]])  # [X, Y]

        Yr1 = self.interpolate_loop(features, Y, numbers[0], xfield, out_fields[0])  # 116 Tr
        Yk2 = self.interpolate_loop(features, Yr1, numbers[1], xfield, out_fields[1])  # 114 Tk

        Yr2 = self.interpolate_loop(features, Yk2, numbers[1], xfield, out_fields[0])  # 114 Tr
        Yk1 = self.interpolate_loop(features, Yr2, numbers[0], xfield, out_fields[1])  # 116 Tk

        return features

