# -*- coding: utf-8 -*-
# TODO: add zero points removing (from geometry)
#
# Алгоритм обрезки точек долета по азимуту
#

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis._core import QgsProcessingParameterBoolean
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
import geopandas as gpd
from ..tools.azimuth_math import *
from ..tools.write_read_methods import *


class ShavingDataAlgorithm(QgsProcessingAlgorithm):
    """
        Входные данные - данные магнитной съемки
        Выходные данные - слой с обрезанными долетами
    """
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    DEL = 'DEL'
    RADIUS = 'RADIUS'
    AZIMUTH = 'AZIMUTH'
    CLASS = 'CLASS'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Входные данные'),
                                                              [QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterBoolean(self.DEL, self.tr('Удалить точки долетов'),
                                                        defaultValue=True))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS, self.tr('Радиус целевого азимута:'),
                                                       defaultValue=20))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Результат'),
                                                            type=QgsProcessing.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):
        radius = self.parameterAsInt(parameters, self.RADIUS, context)
        will_del = self.parameterAsBool(parameters, self.DEL, context)
        input = self.parameterAsSource(parameters, self.INPUT, context)
        if input is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        feedback.setProgressText(f'Loading {input.featureCount()} points...')
        if feedback.isCanceled():
            return {}

        # добавляет лишние кавычки, пока не знаю почему
        uri = self.parameterDefinition(self.INPUT).valueAsPythonString(parameters[self.INPUT], context).strip("'")

        # переводим исходный файл в geopandas
        file = read_file_to_gdf_from_uri(uri)
        if file[0] == 1: feedback.setProgressText(file[1])
        else: feedback.reportError(file[1])

        gdf = file[2]
        gdf = calc_all_azimuths(gdf, self.AZIMUTH)  # подсчитываем значения всех азимутов
        targets = get_targets(gdf)  # найдем профильные азимуты
        bounds = specify_bounds(radius, targets)  # вычислим интервал допустимых азимутов
        gdf = self.classify(gdf, bounds)  # классификация 1 - полезная точка, 0 - нет

        # gdf = gdf[gdf.geometry.z != 0]  # исключим все точки с нулевыми координатами
        gdf = gdf[gdf.LON != 0]

        if will_del:
            gdf = self.delete_points(gdf)

        #  save result
        res_fields = input.fields()
        res_fields.append(QgsField(self.AZIMUTH, QVariant.Double))
        res_fields.append(QgsField(self.CLASS, QVariant.Int))

        (output, output_id) = self.parameterAsSink(parameters, self.OUTPUT, context, res_fields,
                                                   input.wkbType(),
                                                   input.sourceCrs())
        save_gdf_to_output(gdf, res_fields, output)

        if context.willLoadLayerOnCompletion(output_id):
            l = context.layerToLoadOnCompletionDetails(output_id)
            if l:
                l.name = input.sourceName() + '_cut'
        return {self.OUTPUT: output_id}
        # return {}

    def classify(self, gdf, bounds):
        gdf[self.CLASS] = 0
        i = 0
        while i < len(gdf):
            a = gdf.loc[i, self.AZIMUTH]
            for b in bounds:
                if b[0] <= a <= b[1]:
                    gdf.at[i, self.CLASS] = 1
            i += 1

        # print(f'\n{gdf.query("CLASS == 1")}')
        return gdf

    def delete_points(self, gdf):
        gdf = gdf.query(f"{self.CLASS} == 1")
        return gdf

    def name(self):
        return 'shaving_data'

    def displayName(self):
        txt_ru = 'Обрезка долетов'
        return self.tr(txt_ru)

    def shortHelpString(self):
        txt_ru = '''Обрезка долетов'''
        return self.tr(txt_ru)

    def shortDescription(self):
        txt_ru = 'Shaving points'
        return self.tr(txt_ru)

    def group(self):
        return self.tr('Support')

    def groupId(self):
        return 'support'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ShavingDataAlgorithm()
