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


class extractControlsAlgorithm(QgsProcessingAlgorithm):
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

    # def getAsPoint(self, f):
    #     """преобразует очередной считанный объект в точку. Из мультиточек берётся первая точка,
    #     для неточечных объектов - центроид"""
    #     ft = f.geometry().wkbType()
    #     if (ft == QgsWkbTypes.MultiPoint) or (ft == QgsWkbTypes.MultiPointM) or (ft == QgsWkbTypes.MultiPointZ) or (
    #             ft == QgsWkbTypes.MultiPointZM):
    #         g = f.geometry()
    #         g.convertToSingleType()
    #         return g.asPoint()
    #     else:
    #         return f.geometry().asPoint()

    def processAlgorithm(self, parameters, context, feedback):
        input = self.parameterAsSource(parameters, self.INPUT, context)
        if input is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # --- main algorithm ---

        # # save result
        # res_fields = input.fields()
        #
        # (output, output_id) = self.parameterAsSink(parameters, self.OUTPUT, context, res_fields,
        #                                            QgsWkbTypes.PointZ,
        #                                            input.sourceCrs())
        #
        # if feedback.isCanceled():
        #     return {}
        #
        # if context.willLoadLayerOnCompletion(output_id):
        #     l = context.layerToLoadOnCompletionDetails(output_id)
        #     if l:
        #         l.name = 'Контроли'
        # # return {self.OUTPUT: output_id}
        return {}

    def name(self):
        return 'extracting_controls'

    def displayName(self):
        txt_ru = 'Выделение контролей'
        return self.tr(txt_ru)

    def shortHelpString(self):
        txt_ru = '''Выделение контролей магнитосъемки'''
        return self.tr(txt_ru)

    def shortDescription(self):
        txt_ru = 'Выделение контролей магнитосъемки'
        return self.tr(txt_ru)

    def group(self):
        return self.tr('Support')

    def groupId(self):
        return 'support'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return extractControlsAlgorithm()