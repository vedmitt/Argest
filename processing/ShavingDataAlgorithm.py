# -*- coding: utf-8 -*-

#
# Алгоритм поворота точек до горизонтального положения профилей профилей
#
import math
from collections import deque

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingException,
                       QgsFeatureSink,
                       QgsProcessingParameterDefinition,
                       QgsFeature,
                       QgsPoint,
                       QgsLineString,
                       QgsGeometry,
                       QgsField,
                       QgsFields,
                       QgsWkbTypes)

from ..utils.spatial import rotate, dist, BBox, angle180, azimuth180
from ..utils.statistics import AzimuthHistogram
from ..core.classify import Matrix, PointCache

import numpy as np


class shavingDataAlgorithm(QgsProcessingAlgorithm):
    """
        Входные данные - данные магнитной съемки
        Выходные данные - слой с обрезанными долетами
    """
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Входные данные'),
                                                              [QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Результат'),
                                                            type=QgsProcessing.TypeVectorPoint))

    def getAsPoint(self, f):
        """преобразует очередной считанный объект в точку. Из мультиточек берётся первая точка,
        для неточечных объектов - центроид"""
        ft = f.geometry().wkbType()
        if (ft == QgsWkbTypes.MultiPoint) or (ft == QgsWkbTypes.MultiPointM) or (ft == QgsWkbTypes.MultiPointZ) or (
                ft == QgsWkbTypes.MultiPointZM):
            g = f.geometry()
            g.convertToSingleType()
            return g.asPoint()
        else:
            return f.geometry().asPoint()

    latFieldIdx = -1
    lonFieldIdx = -1
    xFieldIdx = -1
    yFieldIdx = -1

    def detectFields(self, fields):
        self.latFieldIdx = fields.indexOf('LAT')
        self.lonFieldIdx = fields.indexOf('LON')
        self.xFieldIdx = fields.indexOf('X')
        self.yFieldIdx = fields.indexOf('Y')

    def isFalsePoint(self, f) -> bool:
        if self.latFieldIdx >= 0 and f[self.latFieldIdx] == 0:
            return True
        if self.xFieldIdx >= 0 and f[self.xFieldIdx] == 0:
            return True
        return False

    def processAlgorithm(self, parameters, context, feedback):
        # def progress(stage, current, total):
        #     stages = 7
        #     feedback.setProgress(int(100/stages*(stage-1) + current/float(total)*100/stages))

        input = self.parameterAsSource(parameters, self.INPUT, context)
        if input is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # total = input.featureCount()
        # fields = input.fields()
        # self.detectFields(fields)
        #
        # points = PointCache(total)  # кэш точек для ускорения вычислений
        #
        # az_threshold = 4  # эмпирика!
        #
        # # Этап 1 - загрузка данных в кэш
        # feedback.setProgressText('Loading data points...')
        # false_count = 0
        # zero_count = 0
        # prev = None
        # azimuths = [0]
        # for current, f in enumerate(input.getFeatures()):
        #     if feedback.isCanceled():
        #         break
        #     if not f.hasGeometry():
        #         continue
        #     g = self.getAsPoint(f)
        #     if prev:
        #         azimuth = azimuth180(prev.x(), prev.y(), g.x(), g.y())
        #         azimuths.append(azimuth)
        #         points.append(g.x(), g.y())
        #     # if not self.isFalsePoint(f):  # в вычислениях участвуют только точки с ненулевыми координатами
        #     #     if prev:
        #     #         if dist(prev.x(), prev.y(), g.x(), g.y()) > 0:
        #     #             points.append(g.x(), g.y())
        #     #         else:
        #     #             zero_count += 1
        #     # else:
        #     #     false_count += 1
        #     prev = g
        #     progress(1, current, total)
        # feedback.setProgressText(f'Points rejected by attributes: {false_count}')
        # feedback.setProgressText(f'Points rejected by distance: {zero_count}')
        # feedback.setProgressText(f'Points loaded: {points.count}')
        #
        # points.compact()
        #
        # # Этап 2 - вычисление статистики по исходным точкам
        # feedback.setProgressText('Calculating statistics...')
        # # переменные для расчёта статистики
        # az_counter = AzimuthHistogram(2)  # гистограмма для вычисления наиболее частого азимута. Точность - 2 градуса
        #
        # for i in range(points.count):
        #     if i > 0 and points.dist[i] > 0:
        #         az_counter.add(points.az[i])
        #     progress(2, i, points.count)
        #
        # feedback.setProgressText(f'Most frequent azimuth = {az_counter.getMostFrequent()}')
        #
        # # Этап 3 - уточнение азимута профилей.
        # # Имеется преобладающий азимут с точностью +/-1 градус, нужно вычислить точнее
        # # Находятся цепочки точек, азимуты между которыми не отклоняются от преобладающего больше, чем на некоторое значение (эмпирически взято 4 градуса)
        # # Для каждой цепочки вычиляется азимут между первой и последней точкой
        # # За финальный азимут берётся среднее значение азимутов 10% наиболее длинных цепочек - так производится ограничение влияния почти параллельных профилям долётов
        #
        # az0 = az_counter.getMostFrequent()  # преобладающий азимут
        #
        # feedback.setProgressText('Refining azimuth and distance...')
        # prev = None
        # az_value = az0
        # first_point = -1 # первая точка цепочки
        # second_point = -1 # последняя точка цепочки
        # run_size = 0 # количество точек в текущей цепочке
        # run_dist = 0 # расстояние между минимальной и максимальной точкой текущей цепочки
        # sum_dst = 0
        # used = 0
        # chains = []
        # chain_len = []
        #
        # for i in range(points.count):
        #     if points.dist[i] > 0: # у первой точки расстояние всегда = 0 и её пропускаем
        #         if math.fabs(points.az[i] - az0) < az_threshold:  # если азимут попадает в предел значений вокруг преобладающего азимута
        #             if first_point >= 0:  # первая точка в цепочке уже есть - наращиваем цепочку
        #                 second_point = i
        #                 run_size += 1
        #                 run_dist = dist(points.x[i], points.y[i], points.x[first_point], points.y[first_point])
        #                 if used == 0 or (points.dist[i] < (sum_dst/used)*10):  # эмпирическая защита от перескоков между участками
        #                     sum_dst += points.dist[i]
        #                     used += 1
        #             else: # первой точки ещё нет - начинаем цепочку
        #                 first_point = i
        #                 second_point = -1
        #                 run_size = 0
        #                 run_dist = 0
        #         else: # отклонение азимута слишком большое - рвём цепочку, если она есть
        #             if first_point >= 0 and second_point >= 0: # если были первая и последняя точки - вычисляем характеристики цепочки и запоминаем их
        #                 if run_dist > 0:  # а может мы метались в стартовой точке и пришли в начало
        #                     az_value = angle180(points.x[first_point], points.y[first_point], points.x[second_point], points.y[second_point])
        #                     if run_size > 2: # совсем мелкие цепочки не берём
        #                         chain_len.append(run_dist)
        #                         chains.append({"l": run_dist, "a": az_value})
        #                 run_size = 0
        #                 run_dist = 0
        #             first_point = -1
        #             second_point = -1
        #     progress(3, i, points.count)
        #
        # if feedback.isCanceled():
        #     return {}
        #
        # az_value = np.mean([a_dict["a"] for a_dict in chains if a_dict["l"] > np.percentile(chain_len, 90)]) # выборка азимута как среднего значения по 10% самых длинных цепочек (TODO: использовать медиану?)
        # az_value_m = np.median([a_dict["a"] for a_dict in chains if a_dict["l"] > np.percentile(chain_len, 90)]) # выборка азимута как среднего значения по 10% самых длинных цепочек (TODO: использовать медиану?)
        #
        # feedback.setProgressText(f'Refined azimuth = {az_value}')
        # feedback.setProgressText(f'Refined azimuth (median) = {az_value_m}')
        #
        # if feedback.isCanceled():
        #     return {}
        #
        # # Этап 5 - определение точек, принадлежащих профилям
        # feedback.setProgressText('Detecting profiles...')

        # save result
        res_fields = input.fields()
        res_fields.append(QgsField('AZ', QVariant.Double))

        (output, output_id) = self.parameterAsSink(parameters, self.OUTPUT, context, res_fields,
                                                   input.wkbType(),
                                                   input.sourceCrs())
        if output is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # classify points
        # target = az_value_m

        # if len(azimuths) == total:
        for i, f in enumerate(input.getFeatures()):
            # if target - 5 < azimuths[i] < target + 5:
            nf = QgsFeature()
            nf.setFields(res_fields)
            nf.setGeometry(f.geometry())
            nf.setAttributes(f.attributes())
            nf['AZ'] = 1
            output.addFeature(nf, QgsFeatureSink.FastInsert)
        # else:
        #     feedback.reportError('\nError while evaluating azimuths', fatalError=True)

        # if feedback.isCanceled():
        #     return {}

        if context.willLoadLayerOnCompletion(output_id):
            l = context.layerToLoadOnCompletionDetails(output_id)
            if l:
                l.name = 'Обрезанные данные'
        return {self.OUTPUT: output_id}

    def name(self):
        return 'shaving_data'

    def displayName(self):
        txt_ru = 'Обрезка долетов магнитосъемки'
        return self.tr(txt_ru)

    def shortHelpString(self):
        txt_ru = '''Обрезка долетов магнитосъемки'''
        return self.tr(txt_ru)

    def shortDescription(self):
        txt_ru = 'Rotate points'
        return self.tr(txt_ru)

    def group(self):
        return self.tr('Support')

    def groupId(self):
        return 'support'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return shavingDataAlgorithm()
