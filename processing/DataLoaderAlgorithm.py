# -*- coding: utf-8 -*-
import datetime

import dateutil.parser
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingException,
                       QgsFeatureSink,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterDefinition,
                       QgsProcessingOutputFile,
                       QgsFeature,
                       QgsPoint,
                       QgsPointXY,
                       QgsLineString,
                       QgsGeometry,
                       QgsField,
                       QgsFields,
                       QgsWkbTypes,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsCoordinateTransformContext,
                       QgsProject)


def detectCrs(lat: float, lon: float, crs) -> str:
    idx = int(lon // 6) + 1 if lon >= 0 else int((180 + lon) // 6) + 31
    try:
        # return QgsCoordinateReferenceSystem('EPSG:209{0:0>2d}'.format(idx))
        return 'EPSG:209{0:0>2d}'.format(idx) if crs == 0 else 'EPSG:284{0:0>2d}'.format(idx)
    except:
        return None


def readFormat1(file, output, s, fields, transform):
    idx_dt = 0
    idx_t = 3
    idx_lon = 4
    idx_lat = 5
    idx_alt = 6
    while s:
        f = s.split('\t')
        lon = float(f[idx_lon])
        lat = float(f[idx_lat])
        dt = float(f[idx_dt])
        alt = float(f[idx_alt])
        d = f[idx_t].split('T')
        d1 = d[0].split('-')
        d2 = d[1].split(':')
        d3 = d2[2].replace(',', '.').split('.')
        day = int(d1[0])
        month = int(d1[1])
        year = int(d1[2])
        hour = int(d2[0])
        minute = int(d2[1])
        second = int(d3[0])
        msecond = int(d3[1])
        if (lon != 0) and (lat != 0):
            feature = QgsFeature(fields)
            pt = QgsPoint(lon, lat)
            pt.transform(transform)
            pt.addZValue(alt)
            feature.setGeometry(pt)
            feature['DAY'] = day
            feature['MONTH'] = month
            feature['YEAR'] = year
            feature['HOUR'] = hour
            feature['MINUTE'] = minute
            feature['SECOND'] = second
            feature['MSECOND'] = msecond
            feature['FIELD'] = dt
            feature['LAT'] = lat
            feature['LON'] = lon
            feature['ALT'] = alt
            output.addFeature(feature, QgsFeatureSink.FastInsert)
        s = file.readline()


def readFormat2(file, output, s, fields, transform):
    idx_dt = 0
    idx_t = 2
    idx_lon = 4
    idx_lat = 3
    idx_alt = 5
    while s:
        f = s.split('\t')
        lon = float(f[idx_lon])
        lat = float(f[idx_lat])
        dt = float(f[idx_dt])
        alt = float(f[idx_alt])
        d = f[idx_t].split('T')
        d1 = d[0].split('-')
        day = int(d1[2])
        month = int(d1[1])
        year = int(d1[0])
        d2 = d[1].split(':')
        d3 = d2[2].replace(',', '.').split('.')
        hour = int(d2[0])
        minute = int(d2[1])
        second = int(d3[0])
        if len(d3) > 1:
            msecond = int(d3[1]) * 100000
        else:
            msecond = 0
        if (lon != 0) and (lat != 0):
            feature = QgsFeature(fields)
            pt = QgsPoint(transform.transform(lon, lat))
            pt.setZ(alt)
            feature.setGeometry(pt)
            feature['DAY'] = day
            feature['MONTH'] = month
            feature['YEAR'] = year
            feature['HOUR'] = hour
            feature['MINUTE'] = minute
            feature['SECOND'] = second
            feature['MSECOND'] = msecond
            feature['FIELD'] = dt
            feature['LAT'] = lat
            feature['LON'] = lon
            feature['ALT'] = alt
            output.addFeature(feature, QgsFeatureSink.FastInsert)
        s = file.readline()


def readFormat3(file, output, s, fields, transform):
    idx_dt = 0
    idx_t = 3
    idx_lon = 4
    idx_lat = 5
    idx_alt = 6
    while s:
        f = s.split('\t')
        lon = float(f[idx_lon])
        lat = float(f[idx_lat])
        dt = float(f[idx_dt])
        alt = float(f[idx_alt])
        d = f[idx_t].split('T')
        d1 = d[0].split('-')
        if len(d1) < 2: d1 = d[0].split('.')
        d2 = d[1].split(':')
        d3 = d2[2].replace(',', '.').split('.')
        day = int(d1[0])
        month = int(d1[1])
        year = int(d1[2])
        hour = int(d2[0])
        minute = int(d2[1])
        second = int(d3[0])
        msecond = int(d3[1])
        if (lon != 0) and (lat != 0):
            feature = QgsFeature(fields)
            pt = QgsPoint(lon, lat)
            pt.transform(transform)
            pt.addZValue(alt)
            feature.setGeometry(pt)
            feature['DAY'] = day
            feature['MONTH'] = month
            feature['YEAR'] = year
            feature['HOUR'] = hour
            feature['MINUTE'] = minute
            feature['SECOND'] = second
            feature['MSECOND'] = msecond
            feature['FIELD'] = dt
            feature['LAT'] = lat
            feature['LON'] = lon
            feature['ALT'] = alt
            output.addFeature(feature, QgsFeatureSink.FastInsert)
        s = file.readline()


class DataLoaderAlgorithm(QgsProcessingAlgorithm):
    """
    """
    INPUT = 'INPUT'
    CRS = 'CRS'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterFile(self.INPUT, self.tr('Исходные данные'),
                                                     extension='txt'))
        self.addParameter(QgsProcessingParameterEnum(self.CRS, self.tr('Целевая система координат'),
                                                     options=['ГСК-2011', 'Пулково-42'], defaultValue=0))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Данные магнитной съёмки'),
                                                            type=QgsProcessing.TypeVectorPoint))

    def processAlgorithm(self, parameters, context, feedback):
        input = self.parameterAsFile(parameters, self.INPUT, context)
        if input is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        out_fields = QgsFields()
        out_fields.append(QgsField('DAY', QVariant.Int))
        out_fields.append(QgsField('MONTH', QVariant.Int))
        out_fields.append(QgsField('YEAR', QVariant.Int))
        out_fields.append(QgsField('HOUR', QVariant.Int))
        out_fields.append(QgsField('MINUTE', QVariant.Int))
        out_fields.append(QgsField('SECOND', QVariant.Int))
        out_fields.append(QgsField('MSECOND', QVariant.Int))
        out_fields.append(QgsField('FIELD', QVariant.Double))
        out_fields.append(QgsField('LAT', QVariant.Double))
        out_fields.append(QgsField('LON', QVariant.Double))
        out_fields.append(QgsField('ALT', QVariant.Double))

        feedback.setProgressText('Загрузка данных ...')
        feedback.setProgressText(f'Входной файл: {input}')

        crs = None
        format = None
        with open(input) as file:
            s = file.readline()
            if s == 'T\tqmc\tst\tTIME\tLON\tLAT\tALT\n':
                format = 1
                idx_lon = 4
                idx_lat = 5
            elif s == 'FIELD\tQMC\tTIME\tLAT\tLON\tALT\n':
                format = 2
                idx_lon = 4
                idx_lat = 3
            elif s == 'FIELD\tqmc\tst\tTIME\tLON\tLAT\tALT\n':
                format = 3
                idx_lon = 4
                idx_lat = 5
            else:
                feedback.setProgressText('Неверный формат файла')
                return {}
            feedback.setProgressText(f'Формат файла: {format}')
            s = file.readline()
            while s:
                f = s.split('\t')
                lon = float(f[idx_lon])
                lat = float(f[idx_lat])
                if (lon != 0) and (lat != 0):
                    crs = detectCrs(lat, lon, self.parameterAsEnum(parameters, self.CRS, context))
                    feedback.setProgressText(f'Целевая система координат - {crs}')
                    crs = QgsCoordinateReferenceSystem(crs)
                    break
                s = file.readline()

            if not crs:
                feedback.setProgressText('Нет точек со значащими координатами. Неверный формат файла?')
                return {}

            if not format:
                feedback.setProgressText('Неверный формат файла')
                return {}

            (output, output_id) = self.parameterAsSink(parameters, self.OUTPUT, context, out_fields, QgsWkbTypes.PointZ,
                                                       crs)
            # ctx = QgsCoordinateTransformContext()
            # ctx.addCoordinateOperation(QgsCoordinateReferenceSystem('EPSG:4326'), crs, '')
            transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'), crs, QgsProject.instance())
            # transform = QgsCoordinateTransform(ctx)

            if format == 1:
                readFormat1(file, output, s, out_fields, transform)
            elif format == 2:
                readFormat2(file, output, s, out_fields, transform)
            elif format == 3:
                readFormat3(file, output, s, out_fields, transform)

        if feedback.isCanceled():
            return {}

        if context.willLoadLayerOnCompletion(output_id):
            l = context.layerToLoadOnCompletionDetails(output_id)
            if l:
                l.name = 'Данные магнитной съёмки'
        return {self.OUTPUT: output_id}

    def name(self):
        return 'load_data'

    def displayName(self):
        txt_ru = 'Загрузка данных магнитной съёмки'
        return self.tr(txt_ru)

    def shortHelpString(self):
        txt_ru = '''Загрузка данных магнитной съёмки'''
        return self.tr(txt_ru)

    def shortDescription(self):
        txt_ru = 'Загрузка данных магнитной съёмки'
        return self.tr(txt_ru)

    def group(self):
        return self.tr('Support')

    def groupId(self):
        return 'support'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return DataLoaderAlgorithm()
