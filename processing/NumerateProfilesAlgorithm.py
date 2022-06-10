# TODO: add shaving data and cutting points before numerating

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
from ..tools.azimuth_math import numerate_profiles
<<<<<<< HEAD
from ..tools.write_read_methods import *
=======
from ..tools.write_read_methods import save_gdf_to_output
>>>>>>> 3c6e438b4560569dda14705ee75d54ebe3e35c73


class NumerateProfileAlgorithm(QgsProcessingAlgorithm):
    """
        Входные данные - обрезанные данные магнитной съемки
        Выходные данные - слой с пронумерованными профилями
    """
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    FLIGHT_NUM = 'FLIGHT_NUM'
    AZIMUTH = 'AZIMUTH'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Входные данные'),
                                                              [QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Результат'),
                                                            type=QgsProcessing.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):
        input = self.parameterAsSource(parameters, self.INPUT, context)
        if input is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        feedback.setProgressText(f'Loading {input.featureCount()} points...')
        if feedback.isCanceled():
            return {}

        # добавляет лишние кавычки, пока не знаю почему
<<<<<<< HEAD
        uri = self.parameterDefinition(self.INPUT).valueAsPythonString(parameters[self.INPUT], context).strip("'")
        file = read_file_to_gdf_from_uri(uri)
        if file[0] == 1:
            feedback.setProgressText(file[1])
        else:
            feedback.reportError(file[1])

        gdf = file[2]
=======
        inf = self.parameterDefinition(self.INPUT).valueAsPythonString(parameters[self.INPUT], context).strip("'")
        gdf = gpd.read_file(inf, encoding='latin1')  # переводим исходный файл в geopandas
>>>>>>> 3c6e438b4560569dda14705ee75d54ebe3e35c73

        gdf = numerate_profiles(gdf, self.AZIMUTH, self.FLIGHT_NUM)

        #  save result
        res_fields = input.fields()
        res_fields.append(QgsField(self.FLIGHT_NUM, QVariant.Int))

        (output, output_id) = self.parameterAsSink(parameters, self.OUTPUT, context, res_fields,
                                                   input.wkbType(),
                                                   input.sourceCrs())
        save_gdf_to_output(gdf, res_fields, output)

        if context.willLoadLayerOnCompletion(output_id):
            l = context.layerToLoadOnCompletionDetails(output_id)
            if l:
                l.name = input.sourceName() + '_num'
        return {self.OUTPUT: output_id}
        # return {}

    def name(self):
        return 'numerate_profiles'

    def displayName(self):
        txt_ru = 'Нумерация профилей'
        return self.tr(txt_ru)

    def shortHelpString(self):
        txt_ru = '''Нумерация профилей'''
        return self.tr(txt_ru)

    def shortDescription(self):
        txt_ru = 'Numerating profiles'
        return self.tr(txt_ru)

    def group(self):
        return self.tr('Support')

    def groupId(self):
        return 'support'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return NumerateProfileAlgorithm()
