# -*- coding: utf-8 -*-

#
# Алгоритм учета вариаций
#
import statistics
from datetime import datetime
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

from ..common.SplinesArray import SplinesArray, ValueNotFoundException


class CalcVariationsAlgorithm(QgsProcessingAlgorithm):
    """
        Входные данные - распарсенные файлы вариаций и магнитки
        Выходные данные - слой магнитки с учтенными вариациями
        """
    INPUT_VAR = 'INPUT_VAR'
    INPUT_MAGN = 'INPUT_MAGN'
    MAGN_CONST = 'MAGN_CONST'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_VAR, self.tr('Данные вариаций'),
                                                              [QgsProcessing.TypeFile]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_MAGN, self.tr('Данные магнитной съемки'),
                                                              [QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterNumber(self.MAGN_CONST, self.tr('Магнитная константа'),
                                                       defaultValue=60000))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Результат'),
                                                            type=QgsProcessing.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):
        input_var = self.parameterAsSource(parameters, self.INPUT_VAR, context)
        input_magn = self.parameterAsSource(parameters, self.INPUT_MAGN, context)
        magn_const = self.parameterAsInt(parameters, self.MAGN_CONST, context)

        if input_var is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_VAR))
        if input_magn is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_MAGN))
        if magn_const is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.MAGN_CONST))

        # ----- main algorithm ------
        feedback.setProgressText(f'Evaluating variations...')

        value_points = []
        variations_function = SplinesArray()

        for f in input_var.getFeatures():
            try:
                unix_dt = datetime(f['YEAR'], f['MONTH'], f['DAY'], f['HOUR'], f['MINUTE'], f['SECOND']).timestamp()
            except ValueError:
                feedback.reportError('\nVariations datetime parse error', fatalError=True)
                continue

            value_points.append((unix_dt, f['FIELD']))

        variations_function.add_spline(value_points)

        res_fields = QgsFields()
        res_fields.append(QgsField('FIELD', QVariant.Double))
        res_fields.append(QgsField('TIME', QVariant.DateTime))
        res_fields.append(QgsField('LAT', QVariant.Double))
        res_fields.append(QgsField('LON', QVariant.Double))
        res_fields.append(QgsField('ALT', QVariant.Double))

        (output, output_id) = self.parameterAsSink(parameters, self.OUTPUT, context, res_fields,
                                                   QgsWkbTypes.PointZ,
                                                   input_magn.sourceCrs())

        magnetic_field = []
        for f in input_magn.getFeatures():
            magnetic_field.append(f['FIELD'])
        magn_const = statistics.median(magnetic_field)

        feedback.setProgressText(f'Магнитная константа равна {magn_const}\n')

        # variated_magnetic_points = []
        for f in input_magn.getFeatures():
            date_time = datetime(f['YEAR'], f['MONTH'], f['DAY'], f['HOUR'], f['MINUTE'], f['SECOND'], f['MSECOND'])
            unix_dt = date_time.timestamp()
            try:
                variated_value = f['FIELD'] + (magn_const - variations_function.get_value(unix_dt))
            except ValueNotFoundException:
                feedback.reportError("\nVariations not found for magnetic record: {}".format(date_time), fatalError=True)
                variated_value = 0
            # variated_magnetic_points.append((variated_value, lon, lat, alt))

            nf = QgsFeature()
            nf.setFields(res_fields)
            nf.setGeometry(f.geometry())
            nf['FIELD'] = variated_value
            nf['TIME'] = format(date_time)
            nf['LAT'] = f['LAT']
            nf['LON'] = f['LON']
            nf['ALT'] = f['ALT']
            output.addFeature(nf, QgsFeatureSink.FastInsert)

        # ----- end of algorithm -------

        if feedback.isCanceled():
            return {}

        if context.willLoadLayerOnCompletion(output_id):
            l = context.layerToLoadOnCompletionDetails(output_id)
            if l:
                l.name = 'Учтенные вариации'
        return {self.OUTPUT: output_id}
        # return {}

    def name(self):
        return 'calc_variations'

    def displayName(self):
        txt_ru = 'Учет вариаций'
        return self.tr(txt_ru)

    def shortHelpString(self):
        txt_ru = '''Учет вариаций магнитной съемки'''
        return self.tr(txt_ru)

    def shortDescription(self):
        txt_ru = 'Учет вариаций магнитной съемки'
        return self.tr(txt_ru)

    def group(self):
        return self.tr('Support')

    def groupId(self):
        return 'support'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CalcVariationsAlgorithm()