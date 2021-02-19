# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bpla_plugin_flightsDialog
                                 A QGIS plugin
 Selecting and deleting odds and ends of flights.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-01-13
        git sha              : $Format:%H$
        copyright            : (C) 2021 by SibGis
        email                : sibgis@qgis.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import csv
import math
import os
from datetime import datetime
from random import random, randint

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QIcon
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtGui import *
from qgis.core import *

from osgeo import ogr, osr
import sys

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
from qgis.utils import iface

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bpla_plugin_flights_dialog_base.ui'))


class bpla_plugin_flightsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(bpla_plugin_flightsDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.initActiveLayersComboBox()
        self.toolButton_cbreload.setIcon(QIcon(':/plugins/bpla_plugin_flights/icon_reload.png'))
        self.toolButton_cbreload.clicked.connect(self.initActiveLayersComboBox)
        self.checkBox.setChecked(True)
        self.toolButton.clicked.connect(self.getSaveFileName)
        self.pushButton.clicked.connect(self.doResult)

    def initActiveLayersComboBox(self):
        canvas = iface.mapCanvas()
        layers = canvas.layers()  # по умолчанию только видимые слои
        self.actVecLyrDict = {}
        self.comboBox.clear()
        for layer in layers:
            if ((type(layer) == QgsVectorLayer) and (layer.geometryType() == 0)):
                # setdefault добавляет элементы с проверкой на повторяющиеся
                # если у пользователя два слоя с одиноковыми именами, в комбобокс попадет только один из них
                self.actVecLyrDict.setdefault(layer.name(), layer)
        self.comboBox.addItems(self.actVecLyrDict.keys())
        self.comboBox.show()

    def getSaveFileName(self):
        dlg = QtWidgets.QFileDialog(self)
        fn = dlg.getSaveFileName(self, 'Save file', r'M:\Sourcetree\bpla_plugin_flights\output\test', filter='*.shp')[0]
        self.lineEdit.setText(fn)

    def getLayer(self):
        # get layer from combobox
        self.layer = self.actVecLyrDict.get(self.comboBox.currentText())
        if self.layer is not None:
            self.layername = self.layer.name()
            self.driverName = self.layer.dataProvider().storageType()
            cur_lyr_path = self.layer.dataProvider().dataSourceUri()

            if self.driverName == 'ESRI Shapefile':
                char_arr = cur_lyr_path.split('|')
                self.layerpath = char_arr[0]

            elif self.driverName == 'Delimited text file':
                fn = cur_lyr_path.split('?')
                fn1 = fn[0].split('///')
                self.layerpath = fn1[1]
                attr = fn[1].split('&')
                self.csvFileAttrs = {}
                for i in range(len(attr)):
                    elem = attr[i].split('=')
                    self.csvFileAttrs.setdefault(elem[0], elem[1])

    def getFilepath(self):
        # get file name from line edit
        self.filepath = None
        if self.lineEdit.text() != '':
            self.filepath = self.lineEdit.text()
            fn = os.path.basename(self.filepath)
            fn = fn.split('.shp')
            self.filename = fn[0]

    def setTextStyle(self, color, weight):
        colors = {
            'black': QColor(0, 0, 0),
            'red': QColor(255, 0, 0),
            'green': QColor(51, 153, 0)
        }
        weights = {
            'normal': 1,
            'bold': QFont.Bold
        }
        self.textEdit.setTextColor(colors.get(color))
        self.textEdit.setFontWeight(weights.get(weight))

    def uploadLayer(self, filepath, filename, typeOfFile):
        # show our new layer in qgis
        layer = iface.addVectorLayer(filepath, filename, typeOfFile)
        if not layer:
            self.textEdit.append('Не удалось загрузить слой в оболочку!\n')

    def csvToMemory(self):
        try:
            self.textEdit.append('Создаем новый слой...')

            # Parse a delimited text file of volcano data and create a shapefile
            # use a dictionary reader so we can access by field name
            reader = csv.DictReader(
                open(self.layerpath, "rt",
                     encoding="utf8"),
                delimiter='\t',
                quoting=csv.QUOTE_NONE)

            # set up the shapefile driver
            driver = ogr.GetDriverByName('MEMORY')

            # create the data source
            self.outDS = driver.CreateDataSource('memData')

            # create the spatial reference, WGS84
            srs = osr.SpatialReference()
            espg = self.csvFileAttrs.get('crs').split(':')
            srs.ImportFromEPSG(int(espg[1]))

            # create the layer
            self.templayer = self.outDS.CreateLayer("temp_layer", srs, ogr.wkbPoint)

            # Add the all fields
            for field in reader.fieldnames:
                self.templayer.CreateField(ogr.FieldDefn(field, ogr.OFTString))
            #
            # Process the text file and add the attributes and features to the shapefile
            for row in reader:
                # create the feature
                feature = ogr.Feature(self.templayer.GetLayerDefn())
                # Set the attributes using the values from the delimited text file
                for item in row.keys():
                    feature.SetField(item, row[item])

                # create the WKT for the feature using Python string formatting
                wkt = "POINT(%f %f)" % (float(row[self.csvFileAttrs.get('xField')]),
                                        float(row[self.csvFileAttrs.get('yField')]))

                # Create the point from the Well Known Txt
                point = ogr.CreateGeometryFromWkt(wkt)

                # Set the feature geometry using the point
                feature.SetGeometry(point)
                # Create the feature in the layer (shapefile)
                self.templayer.CreateFeature(feature)

        except Exception as err:
            self.setTextStyle('red', 'bold')
            self.textEdit.append('\nНе удалось создать временный слой! ' + str(err))

    def layerToMemory(self):
        try:
            self.textEdit.append('Создаем новый слой...')

            self.inDS = ogr.GetDriverByName(self.driverName).Open(self.layerpath, 0)

            # Get the input shapefile
            in_lyr = self.inDS.GetLayer()

            self.textEdit.append('Количество точек в оригинальном слое: ' + str(self.layer.featureCount()))

            # create an output datasource in memory
            memDriver = ogr.GetDriverByName('MEMORY')
            self.outDS = memDriver.CreateDataSource('memData')
            self.tmpDS = memDriver.Open('memData', 1)

            self.templayer = self.outDS.CopyLayer(in_lyr, 'temp_layer', ['OVERWRITE=YES'])

            del self.inDS
        except Exception as err:
            self.setTextStyle('red', 'bold')
            self.textEdit.append('\nНе удалось создать временный слой! ' + str(err))

    def removeZeroPointsFromMemory(self):
        # далее работаем с временным слоем
        if self.templayer is not None:
            self.setTextStyle('green', 'bold')
            self.textEdit.append('Временный слой успешно создан!')
            self.setTextStyle('black', 'normal')
            self.textEdit.append('Количество точек во временном слое: ' + str(self.templayer.GetFeatureCount()))
            # -------- удаляем нулевые точки ---------------
            if self.checkBox.isChecked:
                self.textEdit.append('\nНачинаем удаление нулевых точек...')
                try:
                    for i in range(self.templayer.GetFeatureCount()):
                        feat = self.templayer.GetNextFeature()
                        if feat is not None:
                            geom = feat.geometry()
                            if geom.GetX() == 0.0 and geom.GetY() == 0.0:
                                self.templayer.DeleteFeature(feat.GetFID())
                                self.outDS.ExecuteSQL('REPACK ' + self.templayer.GetName())
                                # self.textEdit.append(str(feat.GetField("TIME")))
                    self.templayer.ResetReading()
                    self.setTextStyle('green', 'bold')
                    self.textEdit.append('Нулевые точки успешно удалены!')
                    self.setTextStyle('black', 'normal')
                    self.textEdit.append(
                        'Количество точек после удаления нулевых: ' + str(self.templayer.GetFeatureCount()))
                except Exception as err:
                    self.setTextStyle('red', 'bold')
                    self.textEdit.append('\nНе удалось удалить нулевые точки! ' + str(err))

            self.outDS.SyncToDisk()

    def saveTempLayerToFile(self):
        # -------- сохраняем результат в шейпфайл (код рабочий) ----------------------
        try:
            fileDriver = ogr.GetDriverByName('ESRI Shapefile')

            # если слой уже существует и загружен, то удаляем его из проекта
            for layer in QgsProject.instance().mapLayers().values():
                if layer.name() == self.filename:
                    QgsProject.instance().removeMapLayers([layer.id()])
                    break

            if os.path.exists(self.filepath):
                fileDriver.DeleteDataSource(self.filepath)

            fileDS = fileDriver.CreateDataSource(self.filepath)
            newDS = fileDriver.Open(self.filepath, 1)

            self.newlayer = fileDS.CopyLayer(self.templayer, self.filename, ['OVERWRITE=YES'])
            if self.newlayer is not None:
                self.uploadLayer(self.filepath, self.filename, 'ogr')
                self.setTextStyle('green', 'bold')
                self.textEdit.append('Слой успешно загружен в QGIS!')
                self.setTextStyle('black', 'normal')
        except Exception as err:
            self.setTextStyle('red', 'bold')
            self.textEdit.append('\nНе удалось сохранить файл! ' + str(err))

        del self.outDS, newDS, fileDS

    def azimutCalc(self, x1, x2):
        dX = x2[0] - x1[0]
        dY = x2[1] - x1[1]
        dist = math.sqrt((dX * dX) + (dY * dY))
        dXa = math.fabs(dX)
        if dist != 0:
            beta = math.degrees(math.acos(dXa / dist))
            if (dX > 0):
                if (dY < 0):
                    angle = 270 + beta
                else:
                    angle = 270 - beta
            else:
                if (dY < 0):
                    angle = 90 - beta
                else:
                    angle = 90 + beta
            return angle
        else:
            return 0

    def distanceCalc(self, x1, x2):
        dX = x2[0] - x1[0]
        dY = x2[1] - x1[1]
        dist = math.sqrt((dX * dX) + (dY * dY))
        return dist

    def mainAzimutCalc(self):
        # ------ основная часть плагина -------------------------
        global azimut_2
        self.textEdit.append('\nНачинаем удаление избыточных точек...')
        try:
            feat_list = []
            for i in range(self.templayer.GetFeatureCount()):
                feat = self.templayer.GetNextFeature()
                feat_list.append(feat)
            self.templayer.ResetReading()

            # отсортируем список по времени
            feat_list = sorted(feat_list, key=lambda feature: feature.GetField("TIME"), reverse=False)

            accuracy = 10
            flightList = []
            parts_list = []
            # min_dist = 6.966525707833812e-08
            # bad_paths = []
            i = 0
            az_temp = []
            avg_az_list = []
            while i + 2 < len(feat_list):
                azimut_1 = self.azimutCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
                                           [feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()])
                azimut_2 = self.azimutCalc([feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()],
                                           [feat_list[i + 2].geometry().GetX(), feat_list[i + 2].geometry().GetY()])

                # dist = self.distanceCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
                #                          [feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()])

                if math.fabs(azimut_1 - azimut_2) < accuracy:
                    # if dist < min_dist:
                    #     bad_paths.append(feat_list[i].GetFID())
                    # else:
                        parts_list.append(feat_list[i])
                        az_temp.append(azimut_1)
                else:
                    if parts_list is not None:
                        flightList.append(parts_list)
                        az_sum = 0
                        for item in az_temp:
                            az_sum = az_sum + item
                        avg_az_list.append(az_sum / len(az_temp))
                    parts_list = [feat_list[i]]
                    az_temp = [azimut_1]
                i += 1

            if parts_list is not None:
                parts_list.append(feat_list[i])
                parts_list.append(feat_list[i + 1])
                avg_az_list.append(azimut_2)
                flightList.append(parts_list)

            # # удаляем аномальные пути в начале полетов
            # for item in bad_paths:
            #     self.templayer.DeleteFeature(item)
            #     self.outDS.ExecuteSQL('REPACK ' + self.templayer.GetName())

            self.textEdit.append('Количество частей полетов: ' + str(len(flightList)))
            self.textEdit.append('Количество усредненных азимутов: ' + str(len(avg_az_list)))
            longest_path = max(len(elem) for elem in flightList)
            self.textEdit.append('Самый длинный полет: ' + str(longest_path))
            shortest_path = min(len(elem) for elem in flightList)
            self.textEdit.append('Самый короткий полет: ' + str(shortest_path))

            # i_longest = 0
            # for path in flightList:
            #     if len(path) == longest_path:
            #         i_longest = flightList.index(path)
            #         break
            #
            # target_az = avg_az_list[i_longest]
            # self.textEdit.append('Целевой азимут: ' + str(target_az))
            # for i in range(len(avg_az_list)):
            #     if math.fabs(avg_az_list[i] - target_az) < accuracy or math.fabs((avg_az_list[i]+180) - target_az) < accuracy:
            #         if len(flightList[i]) < 20:
            #             for feat in flightList[i]:
            #                 self.templayer.DeleteFeature(feat.GetFID())
            #                 self.outDS.ExecuteSQL('REPACK ' + self.templayer.GetName())
            #     else:
            #         for feat in flightList[i]:
            #             self.templayer.DeleteFeature(feat.GetFID())
            #             self.outDS.ExecuteSQL('REPACK ' + self.templayer.GetName())

            while i + 2 < len(avg_az_list):
                if math.fabs(avg_az_list[i] - avg_az_list[i+1]) in range(85, 95) \
                        or math.fabs(avg_az_list[i+1] - avg_az_list[i+2]) in range(85, 95):
                    if len(flightList[i]) > len(flightList[i+1]) and len(flightList[i+2]) > len(flightList[i+1]):
                        for feat in flightList[i+1]:
                            self.templayer.DeleteFeature(feat.GetFID())
                            self.outDS.ExecuteSQL('REPACK ' + self.templayer.GetName())
                else:
                    for feat in flightList[i]:
                        self.templayer.DeleteFeature(feat.GetFID())
                        self.outDS.ExecuteSQL('REPACK ' + self.templayer.GetName())

            # for path in flightList:
            #     if len(path) < longest_path / 2:
            #         for feat in path:
            #             self.templayer.DeleteFeature(feat.GetFID())
            #             self.outDS.ExecuteSQL('REPACK ' + self.templayer.GetName())

            self.setTextStyle('green', 'bold')
            self.textEdit.append('Избыточные точки успешно удалены!')
            self.setTextStyle('black', 'normal')
            self.textEdit.append('\nКоличество точек в полученном слое: ' + str(self.templayer.GetFeatureCount()))

        except Exception as err:
            self.setTextStyle('red', 'bold')
            self.textEdit.append('\nНе удалось удалить избыточные точки! ' + str(err))

        self.outDS.SyncToDisk()

    def doResult(self):
        self.setTextStyle('black', 'normal')
        self.textEdit.setText('')

        self.getLayer()
        self.getFilepath()

        if self.layer and self.filepath is not None:
            if self.driverName == "Delimited text file":
                self.csvToMemory()
            elif self.driverName == "ESRI Shapefile":
                self.layerToMemory()
            self.removeZeroPointsFromMemory()
            self.mainAzimutCalc()
            self.saveTempLayerToFile()
        else:
            self.setTextStyle('red', 'bold')
            self.textEdit.append('Введите данные в форму!\n')
