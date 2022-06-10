# TODO: add shaving data before numerating

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
import geopandas as gpd
from ..tools.azimuth_math import numerate_profiles
from ..tools.write_read_methods import *


class ExtractControlsAlgorithm(QgsProcessingAlgorithm):
    """
        Входные данные - данные магнитной съемки
        Выходные данные - слой с обрезанными долетами
        """
    INPUT = 'INPUT'
    OUT_CONTROLS = 'OUT_CONTROLS'
    OUT_ORDINARIES = 'OUT_ORDINARIES'
    AZIMUTH = 'AZIMUTH'
    FLIGHT_NUM = 'FLIGHT_NUM'
    PAIR_NUM = 'PAIR_NUM'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Входные данные'),
                                                              [QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUT_CONTROLS, self.tr('Контрольные профиля'),
                                                            type=QgsProcessing.TypeVectorPoint))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUT_ORDINARIES, self.tr('Рядовые профиля'),
                                                            type=QgsProcessing.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):
        input = self.parameterAsSource(parameters, self.INPUT, context)
        if input is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        feedback.setProgressText(f'Loading {input.featureCount()} points...')
        if feedback.isCanceled():
            return {}

        uri = self.parameterDefinition(self.INPUT).valueAsPythonString(parameters[self.INPUT], context).strip("'")
        file = read_file_to_gdf_from_uri(uri)
        if file[0] == 1:
            feedback.setProgressText(file[1])
        else:
            feedback.reportError(file[1])

        gdf = file[2]

        if self.FLIGHT_NUM not in gdf.columns:
            feedback.setProgressText(f'\nNumerating points...')
            gdf = numerate_profiles(gdf, self.AZIMUTH, self.FLIGHT_NUM)

        feedback.setProgressText(f'\nBuilding a scheme...')
        scheme = self.build_scheme(gdf)

        if scheme is not None and len(scheme) > 0:

            controls, ordinals = self.classify(scheme, gdf)

            #  save result
            feedback.setProgressText(f'\nSaving results...')
            res_fields = input.fields()
            res_fields.append(QgsField(self.FLIGHT_NUM, QVariant.Int))
            res_fields.append(QgsField(self.PAIR_NUM, QVariant.Int))

            (out_contr, out_contr_id) = self.parameterAsSink(parameters, self.OUT_CONTROLS, context, res_fields,
                                                             input.wkbType(),
                                                             input.sourceCrs())
            (out_ord, out_ord_id) = self.parameterAsSink(parameters, self.OUT_ORDINARIES, context, res_fields,
                                                             input.wkbType(),
                                                             input.sourceCrs())

            save_gdf_to_output(controls, res_fields, out_contr)
            save_gdf_to_output(ordinals, res_fields, out_ord)

            if context.willLoadLayerOnCompletion(out_contr_id):
                l = context.layerToLoadOnCompletionDetails(out_contr_id)
                l1 = context.layerToLoadOnCompletionDetails(out_ord_id)
                if l:
                    l.name = input.sourceName() + '_controls'
                    l1.name = input.sourceName() + '_ordinaries'
            return {
                self.OUT_CONTROLS: out_contr_id,
                self.OUT_ORDINARIES: out_ord_id
            }
        else:
            feedback.reportError(f'\nКонтрольные профиля не найдены!')
            return {}

    def build_scheme(self, gdf):  # create the scheme of repeated profiles
        """Returns a scheme of points intersections where area > 10000"""

        # make buffer
        scheme = gdf[[self.FLIGHT_NUM, 'geometry']]
        scheme = scheme.set_geometry(gdf.buffer(10))

        # make dissolve
        scheme = scheme.dissolve(by=self.FLIGHT_NUM, as_index=False, aggfunc="first")

        # build scheme with profile polygons
        flight1 = []
        flight2 = []
        geometry = []
        area = []

        i = 0
        while i < len(scheme):
            j = 0
            while j < len(scheme):
                if scheme.geometry[i] is None or scheme.geometry[j] is None:
                    pass
                else:
                    if scheme.geometry[i].intersects(scheme.geometry[j]) and i < j:
                        f1 = scheme.loc[i, self.FLIGHT_NUM]
                        f2 = scheme.loc[j, self.FLIGHT_NUM]
                        intersection = scheme.geometry[i].intersection(scheme.geometry[j])
                        flight1.append(f1)
                        flight2.append(f2)
                        geometry.append(intersection)
                        area.append(intersection.area)
                j += 1
            i += 1

        scheme = gpd.GeoDataFrame(
            {
                'flight1': flight1,
                'flight2': flight2,
                'area': area,
                'geometry': geometry,
            },
            crs=gdf.crs
        )
        scheme = scheme.query('area > 10000')
        if len(scheme) > 0:
            return scheme
        else:
            return None

    def classify(self, scheme, gdf):
        """Returns controls and ordinaries geodataframes from gdf overlapping by scheme
                :gdf scheme: geometry type Polygon
                :gdf gdf: input data geometry type Points"""

        gdf[self.PAIR_NUM] = 0
        i = 0
        while i < len(gdf):
            f0 = gdf.loc[i, self.FLIGHT_NUM]
            for index, row in scheme.iterrows():
                f1 = row["flight1"]
                f2 = row["flight2"]
                if (f0 == f1 and gdf.geometry[i].intersects(row["geometry"])) \
                        or (f0 == f2 and gdf.geometry[i].intersects(row["geometry"])):
                    gdf.loc[i, self.PAIR_NUM] = f2
            i += 1
        controls = gdf.query(f'{self.PAIR_NUM} > 0 and {self.FLIGHT_NUM} == {self.PAIR_NUM}')
        ordinals = gdf.query(f'{self.PAIR_NUM} == 0 or {self.FLIGHT_NUM} != {self.PAIR_NUM}')
        return controls, ordinals

    def name(self):
        return 'extracting_controls'

    def displayName(self):
        txt_ru = 'Выделение контролей'
        return self.tr(txt_ru)

    def shortHelpString(self):
        txt_ru = '''Выделение контролей'''
        return self.tr(txt_ru)

    def shortDescription(self):
        txt_ru = 'Extracting controls'
        return self.tr(txt_ru)

    def group(self):
        return self.tr('Support')

    def groupId(self):
        return 'support'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExtractControlsAlgorithm()
