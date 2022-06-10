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
                       QgsLineString,
                       QgsGeometry,
                       QgsField,
                       QgsFields,
                       QgsWkbTypes)

def loadMinimag(source, feedback, context, output, fields):
    def scanHeader(file):
        date = None
        found = False
        s = file.readline()
        while s:
            if s.strip() == 'Режим автоматических измерений':
                found = True
            if s.strip('').startswith('Дата:'):
                s = s[5:]
                d = s.split('.')
                date = datetime.date(int(d[2]), int(d[1]), int(d[0]))
                feedback.setProgressText(f'Дата: {date}')
            if s.strip() == 'Поле   	  Время   	   Широта   	   Долгота   	FM	US':
                return date if found else None
            s = file.readline()
        return None

    def readLines(file, date):
        first = True
        s = file.readline()
        while s:
            f = s.split('\t')
            if len(f) > 1:
                dt = f[0]
                t = f[1].split(':')
                hrs = int(t[0])
                min = int(t[1])
                sec = round(float(t[2]))
                ft = QgsFeature(fields)
                ft['DAY'] = date.day
                ft['MONTH'] = date.month
                ft['YEAR'] = date.year
                ft['HOUR'] = hrs
                ft['MINUTE'] = min
                ft['SECOND'] = sec
                ft['MSECOND'] = round(float(t[2]) % 1 * 1e6)
                ft['FIELD'] = dt
                output.addFeature(ft)
                if first:
                    feedback.setProgressText(f'Время первого отсчёта: {datetime.datetime(date.year, date.month, date.day, hrs, min, sec)}')
                    first = False
            else:
                return
            s = file.readline()

    feedback.setProgressText('Выбран формат MiniMag')
    with open(source, encoding='utf8') as file:
        while True:
            date = scanHeader(file)
            if date:
                readLines(file, date)
            else:
                return

def loadPos(source, feedback, context, output, fields):
    def scanHeader(file):
        s = file.readline()
        while s:
            if not s.startswith(';'):
                feedback.setProgressText(f'String is: {s}')
                t = s.split(' ')
                try:
                    if len(t[3].split('-')) > 1: return s, '-'
                    elif len(t[3].split('.')) > 1: return s, '.'
                    else: return None
                except:
                    return None
            s = file.readline()
        return None

    feedback.setProgressText('Выбран формат POS')
    with open(source, encoding='utf8') as file:
        s, sep = scanHeader(file)
        if sep == '-':
            feedback.setProgressText('Разделитель даты - дефис')
        elif sep == '.':
            feedback.setProgressText('Разделитель даты - точка')
        else:
            feedback.setProgressText('Не удалось определить разделитель даты. Неверный формат файла?')
            return
        while s:
            t = s.split(' ')
            dt = float(t[0]) / 1000
            d = t[3].split(sep)
            t = t[4].split(':')
            ft = QgsFeature(fields)
            ft['DAY'] = int(d[1])
            ft['MONTH'] = int(d[0])
            ft['YEAR'] = int(d[2]) + 2000
            ft['HOUR'] = int(t[0])
            ft['MINUTE'] = int(t[1])
            ft['SECOND'] = round(float(t[2].replace(',','.')))
            ft['MSECOND'] = round(float(t[2].replace(',','.')) % 1 * 1e6)
            ft['FIELD'] = dt
            output.addFeature(ft)
            s = file.readline()

class variationsLoaderAlgorithm(QgsProcessingAlgorithm):
    """
    """
    INPUT  = 'INPUT'
    FORMAT = 'FORMAT'
    OUTPUT = 'OUTPUT'
    output_names = ['Вариации POS', 'Вариации MiniMag']

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterFile(self.INPUT, self.tr('Исходные данные'),
                                                              extension='txt'))
        self.addParameter(QgsProcessingParameterEnum(self.FORMAT, self.tr('Формат данных'), options = self.output_names, defaultValue=0))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Результат'),
                                                              type=QgsProcessing.TypeVector))

    def processAlgorithm(self, parameters, context, feedback):
        input = self.parameterAsFile(parameters, self.INPUT, context)
        format = self.parameterAsEnum(parameters, self.FORMAT, context)
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
        (output, output_id) = self.parameterAsSink(parameters, self.OUTPUT, context, out_fields)
        feedback.setProgressText('Загрузка данных ...')
        feedback.setProgressText(f'Входной файл: {input}')
        if format == 1:
            loadMinimag(input, feedback, context, output, out_fields)
        else:
            loadPos(input, feedback, context, output, out_fields)

        if feedback.isCanceled():
            return {}

        if context.willLoadLayerOnCompletion(output_id):
            l = context.layerToLoadOnCompletionDetails(output_id)
            if l:
                l.name = self.output_names[format]
        return {self.OUTPUT: output_id}

    def name(self):
        return 'load_variations'

    def displayName(self):
        txt_ru = 'Загрузка данных вариаций'
        return self.tr(txt_ru)

    def shortHelpString(self):
        txt_ru = '''Загрузка данных вариаций из файлов POS или MiniMag'''
        return self.tr(txt_ru)

    def shortDescription(self):
        txt_ru = 'Загрузка данных вариаций из файлов POS или MiniMag'
        return self.tr(txt_ru)

    def group(self):
        return self.tr('Support')

    def groupId(self):
        return 'support'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return variationsLoaderAlgorithm()
