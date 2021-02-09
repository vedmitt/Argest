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
import math
import os
from datetime import datetime
from time import sleep

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QIcon
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *


from osgeo import ogr
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
        layers = canvas.layers()
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
        fn = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file')[0]
        self.lineEdit.setText(fn + '.shp')

    def getLayer(self):
        # get layer from combobox
        self.layer = self.actVecLyrDict.get(self.comboBox.currentText())
        if self.layer is None:
            self.textEdit.append('Слой не выбран!\n')
        else:
            self.layername = self.layer.name()
            cur_lyr_path = self.layer.dataProvider().dataSourceUri()

            if self.layer.dataProvider().storageType() == 'ESRI Shapefile':
                self.driverName = self.layer.dataProvider().storageType()
                char_arr = cur_lyr_path.split('|')
                self.layerpath = char_arr[0]

            elif self.layer.dataProvider().storageType() == 'Delimited text file':
                self.driverName = 'delimitedtext'
                fn = cur_lyr_path.split('?')
                fn = fn[0].split('///')
                self.layerpath = fn[1]
                # self.textEdit.append(self.layerpath)


    def getFilepath(self):
        # get file name from line edit
        if self.lineEdit.text() != '':
            self.filepath = self.lineEdit.text()
            fn = os.path.basename(self.filepath)
            fn = fn.split('.shp')
            self.filename = fn[0]
        else:
            self.textEdit.append("Файл для сохранения не выбран!\n")

    def getAzimut(self):
        self.azimutUser = self.doubleSpinBox.value()

    def uploadLayer(self, filepath, filename, typeOfFile):
        # show our new layer in qgis
        layer = iface.addVectorLayer(filepath, filename, typeOfFile)
        if not layer:
            self.textEdit.append('Не удалось загрузить слой в оболочку!\n')

    # def layerToList(self):
    #     self.textEdit.append(self.layerpath)
    #     self.textEdit.append(self.layername)
    #     self.textEdit.append(self.filepath)
    #     self.textEdit.append(self.filename)
    #
    #     # create temp layer
    #     # open an input datasource
    #     indriver = ogr.GetDriverByName('ESRI shapefile')
    #     srcdb = indriver.Open(self.layerpath, 0)
    #
    #     # create an output datasource in memory
    #     outdriver = ogr.GetDriverByName('MEMORY')
    #     source = outdriver.CreateDataSource('memData')
    #
    #     # open the memory datasource with write access
    #     tmp = outdriver.Open('memData', 1)
    #
    #     # copy a layer to memory
    #     pipes_mem = source.CopyLayer(srcdb.GetLayer(self.layername), 'temp_layer', ['OVERWRITE=YES'])
    #
    #     # the new layer can be directly accessed via the handle pipes_mem or as source.GetLayer('temp_layer'):
    #     templayer = source.GetLayer('temp_layer')
    #
    #     # next we work only with temp layer
    #     # create list of features
    #     self.listFeat = []
    #     for f in templayer:
    #         self.listFeat.append(f)
    #     self.textEdit.append('List items count: ' + str(len(self.listFeat)))
    #     templayer.ResetReading()
    #
    #     del indriver, outdriver, srcdb, source
    #
    #
    # def removeZeroFeatures(self):
    #     if self.checkBox.isChecked:
    #         self.textEdit.append('Checkbox is checked!')
    #         self.listFeat.sort(key=lambda val: val['LON'] == 0.0, reverse=True)
    #         for i in self.listFeat:
    #             # self.textEdit.append(str(i['LON'])+' '+str(i['LAT']))
    #             if i['LON'] == 0.0 and i['LAT'] == 0.0:
    #                 # self.textEdit.append('first zero point!')
    #                 self.listFeat.remove(i)
    #                 # break
    #     self.textEdit.append('List items count: ' + str(len(self.listFeat)))
    #
    # def listToShapefile(self):  # from memory layer to shapefile
    #     # Open the folder data source for writing
    #     inds = ogr.Open(self.layerpath, 1)
    #
    #     if inds is None:
    #         sys.exit('Could not open folder.')
    #
    #     # Get the input shapefile
    #     in_lyr = inds.GetLayer()
    #
    #     # Create an output point layer
    #     drv = ogr.GetDriverByName('ESRI Shapefile')
    #     outds = drv.CreateDataSource(self.filepath)
    #
    #     # if outds.GetLayer('capital_cities'):
    #     #     outds.DeleteLayer('capital_cities')
    #     out_lyr = outds.CreateLayer(self.filename,
    #                                 in_lyr.GetSpatialRef(),
    #                                 ogr.wkbPoint)
    #     out_lyr.CreateFields(in_lyr.schema)  # get old fields schema
    #
    #     # Create a blank feature
    #     out_defn = out_lyr.GetLayerDefn()
    #     out_feat = ogr.Feature(out_defn)
    #
    #     for in_feat in self.listFeat:
    #         # Copy geometry and attributes
    #         geom = in_feat.geometry()
    #         out_feat.SetGeometry(geom)
    #
    #         for i in range(in_feat.GetFieldCount()):
    #             value = in_feat.GetField(i)
    #             out_feat.SetField(i, value)
    #
    #         # Insert the feature
    #         out_lyr.CreateFeature(out_feat)
    #
    #     i = 0
    #     for f in out_lyr:
    #         # print(f['NAME'])
    #         i += 1
    #     self.textEdit.append('Features in layer ' + str(i))
    #     out_lyr.ResetReading()
    #
    #     # out_lyr = outds.CopyLayer(inlyr, 'test2')
    #     self.outlayer = out_lyr
    #     del in_lyr, inds, out_lyr, outds
    #
    # #     # Write to an ESRI Shapefile format dataset using UTF-8 text encoding
    # #     save_options = QgsVectorFileWriter.SaveVectorOptions()
    # #     save_options.driverName = "ESRI Shapefile"
    # #     save_options.fileEncoding = "UTF-8"
    # #     transform_context = QgsProject.instance().transformContext()
    # #
    # #     error = QgsVectorFileWriter.writeAsVectorFormat(self.layer, self.filename,
    # #                                                     "CP1250", self.layer.crs(),
    # #                                                     "ESRI Shapefile")
    # #
    # #     if error[0] == QgsVectorFileWriter.NoError:
    # #         iface.messageBar().pushMessage("Successfully saved!", level=0)
    # #         # # uploading new file to the map
    # #         # layer = iface.addVectorLayer(r"M:\Sourcetree\bpla_plugin_flights\output\test1.shp", "new_layer", "ogr")
    # #         filepath = self.filename + '.shp'
    # #         # iface.messageBar().pushMessage(filepath, level=0)
    # #         layer = iface.addVectorLayer(filepath, "new_layer", "ogr")
    # #         if not layer:
    # #             iface.messageBar().pushMessage("Layer failed to load!", level=0)
    # #     else:
    # #         iface.messageBar().pushMessage("Something went wrong... ", error,  level=0)

    def remZeroPointsFromLayer(self):
        self.templayer = QgsVectorLayer(self.filepath, self.filename, 'ogr')

        if self.checkBox.isChecked:
            self.textEdit.append('\nУдаление нулевых точек...')
            with edit(self.templayer):
                # build a request to filter the features based on an attribute
                request = QgsFeatureRequest().setFilterExpression('"LON" = 0.0 and "LAT" = 0.0')

                # we don't need attributes or geometry, skip them to minimize overhead.
                # these lines are not strictly required but improve performance
                request.setSubsetOfAttributes([])
                request.setFlags(QgsFeatureRequest.NoGeometry)

                # loop over the features and delete
                for f in self.templayer.getFeatures(request):
                    self.templayer.deleteFeature(f.id())
                self.templayer.updateFields()

        i = self.templayer.featureCount()
        self.textEdit.append('Количество точек в новом слое: ' + str(i))
        self.textEdit.append('Количество точек удалено: ' + str(self.initFeatCount - i))


    def setFlightNumber(self):  ## working method
        # self.newlayer = QgsVectorLayer(r'M:\Sourcetree\bpla_plugin_flights\output\test1.shp', 'test1', 'ogr')

        # create new field with no content
        pr = self.templayer.dataProvider()
        caps = pr.capabilities()
        request = QgsFeatureRequest()
        # request.setLimit(10)

        fieldNum = self.templayer.fields().count()
        self.textEdit.append('\nНачинаем сквозную нумерацию полетов...')
        if caps & QgsVectorDataProvider.AddAttributes:
            new_field = [QgsField("FLIGHT_NUM", QVariant.Int)]
            if new_field not in self.templayer.fields():
                pr.addAttributes(new_field)
                self.templayer.updateFields()

        i = 1
        boolYesNo = False
        prevFeat = None
        nextFeat = None

        for feat in self.templayer.getFeatures(request):
            if feat.id() == 0:
                prevFeat = feat
            elif feat.id() == 1:
                nextFeat = feat
                boolYesNo = self.timeSort(prevFeat, nextFeat)
            else:
                prevFeat = nextFeat
                nextFeat = feat
                boolYesNo = self.timeSort(prevFeat, nextFeat)

            if (boolYesNo is False) and (nextFeat is not None):
                # add new flight number
                attrs = {fieldNum: i}
                self.changeFeatValues(self.templayer, prevFeat.id(), attrs)
                self.changeFeatValues(self.templayer, nextFeat.id(), attrs)
            elif nextFeat is not None:
                i += 1
                # add new flight number
                attrs = {fieldNum: i}
                self.changeFeatValues(self.templayer, nextFeat.id(), attrs)

        self.textEdit.append('Полетов выделено: ' + str(i))


    def timeSort(self, prevFeat, nextFeat):
        data_format = '%m-%d-%YT%H:%M:%S,%f'

        prevDataTime = datetime.strptime(prevFeat['TIME'], data_format)
        nextDataTime = datetime.strptime(nextFeat['TIME'], data_format)

        if nextDataTime.date() != prevDataTime.date():
            return True
        elif (nextDataTime.time().second - prevDataTime.time().second) > 1:
            return True
        else:
            return False

    def changeFeatValues(self, layer, fid, attrs):
        pr = layer.dataProvider()
        caps = pr.capabilities()
        if caps & QgsVectorDataProvider.ChangeAttributeValues:
            pr.changeAttributeValues({fid: attrs})
            self.templayer.updateFields()

    #--- весь алгоритм программы насчет азимутов реализуется в коде ниже ---
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

    def delFeatures(self, delFeatIDs):
        caps = self.templayer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.DeleteFeatures:
            res = self.templayer.dataProvider().deleteFeatures(delFeatIDs)

    def removePointsFromAzimut(self, prevFeat, nextFeat, delFeatIDs):
        # geomPrev = prevFeat.geometry()
        # geomNext = nextFeat.geometry()
        angle = self.azimutCalc([prevFeat.GetX(), prevFeat.GetY()], [nextFeat.GetX(), nextFeat.GetY()])
        accuracy = 5

        if (math.fabs(angle - self.azimutUser) < accuracy) or (math.fabs(angle - (self.azimutUser + 180)) < accuracy):
            pass
        else:
            delFeatIDs.append(prevFeat.id())

        return delFeatIDs

    def fromLayerCalcAzimut(self):
        self.textEdit.append('\nНачинаем удаление избыточных точек...')

        request = QgsFeatureRequest()
        # request.setLimit(10)

        prevFeat = None
        nextFeat = None
        delFeatIDs = []
        for feat in self.templayer.getFeatures(request):
            if feat.id() == 0:
                prevFeat = feat
            elif feat.id() == 1:
                nextFeat = feat
                delFeatIDs = self.removePointsFromAzimut(prevFeat, nextFeat, delFeatIDs)
            else:
                prevFeat = nextFeat
                nextFeat = feat
                delFeatIDs = self.removePointsFromAzimut(prevFeat, nextFeat, delFeatIDs)

        self.textEdit.append('Количество удаленных точек: ' + str(len(delFeatIDs)))
        self.delFeatures(delFeatIDs)
        self.textEdit.append('Количество точек в полученном слое: ' + str(self.templayer.featureCount()))

        self.uploadLayer(self.filepath, self.filename, 'ogr')
    ##--------------END-----------------

    def doResult(self):
        self.textEdit.setText('')
        self.getLayer()
        self.getFilepath()
        self.getAzimut()

        # self.layerToList()
        # self.removeZeroFeatures()
        # self.listToShapefile()

        # self.newlayer = QgsVectorLayer(r'M:\YandexDisk\QGIS\temp\test_pro1.shp', 'test_pro1', 'ogr')
        # self.azimutUser = 90

        # # этот кусок кода полностью рабочий, его лучше не трогать
        # res = self.copyLayer()
        # self.textEdit.append(res[0])
        # if res[1] != 0:
        #     self.remZeroPointsFromLayer()
        #     self.setFlightNumber()
        #     self.fromLayerCalcAzimut()
        ####---------------------------------

        if self.layer is not None:
            # main code here
            # copy the layer
            self.textEdit.append('Создаем новый слой...')

            # open an input datasource
            # driverName = self.layer.dataProvider().storageType()
            # indriver = ogr.GetDriverByName(self.driverName)
            # inDS = indriver.Open(self.layerpath, 0)

            inDS = ogr.Open(self.layerpath, 0)
            # fn = os.path.split(self.layerpath)
            # inDS = ogr.Open(fn[0], 0)

            if inDS is None:
                # sys.exit('Could not open folder.')
                return ['Произошла ошибка при создании файла!', 0]

            # Get the input shapefile
            in_lyr = inDS.GetLayer()
            # in_lyr = QgsVectorLayer(self.layer.dataProvider().dataSourceUri(), self.layerpath, "delimitedtext")

            self.textEdit.append('Количество точек в оригинальном слое: ' + str(self.layer.featureCount()))

            # create an output datasource in memory
            memDriver = ogr.GetDriverByName('MEMORY')
            outDS = memDriver.CreateDataSource('memData')
            # open the memory datasource with write access
            tmpDS = memDriver.Open('memData', 1)

            self.templayer = outDS.CopyLayer(in_lyr, 'temp_layer', ['OVERWRITE=YES'])

            # далее работаем с временным слоем
            if self.templayer is None:
                # outDS.SyncToDisk()
                del inDS, tmpDS, outDS
                self.textEdit.append('Произошла ошибка при создании файла!')
                # return ['Произошла ошибка при создании файла!', 0]
            else:
                self.textEdit.append('Новый слой успешно создан!')
                self.textEdit.append('Количество точек в новом слое: ' + str(self.templayer.GetFeatureCount()))

                if self.checkBox.isChecked:
                    self.textEdit.append('\nНачинаем удаление нулевых точек...')
                    for i in range(self.templayer.GetFeatureCount()):
                        feat = self.templayer.GetNextFeature()
                        if feat is not None:
                            geom = feat.geometry()
                            if geom.GetX() == 0.0 and geom.GetY() == 0.0:
                                self.templayer.DeleteFeature(feat.GetFID())
                                inDS.ExecuteSQL('REPACK ' + self.templayer.GetName())
                                # self.textEdit.append(str(feat.GetField("TIME")))
                    self.templayer.ResetReading()
                    self.textEdit.append('Количество точек после удаления нулевых: ' + str(self.templayer.GetFeatureCount()))

                outDS.SyncToDisk()

                # основная часть плагина
                self.textEdit.append('\nНачинаем удаление избыточных точек...')
                prevFeat = None
                nextFeat = None
                delFeatIDs = []
                for i in range(self.templayer.GetFeatureCount()):
                    feat = self.templayer.GetNextFeature()
                    if feat is not None:
                        if feat.GetFID() == 0:
                            prevFeat = feat
                        elif feat.GetFID() == 1:
                            nextFeat = feat
                            delFeatIDs = self.removePointsFromAzimut(prevFeat.geometry(), nextFeat.geometry(), delFeatIDs)
                        else:
                            prevFeat = nextFeat
                            nextFeat = feat
                            delFeatIDs = self.removePointsFromAzimut(prevFeat.geometry(), nextFeat.geometry(), delFeatIDs)
                self.templayer.ResetReading()
                self.textEdit.append('Количество удаленных точек: ' + str(len(delFeatIDs)))
                # self.delFeatures(delFeatIDs)
                # self.templayer.DeleteFeatures(delFeatIDs)
                # inDS.ExecuteSQL('REPACK ' + self.templayer.GetName())
                self.textEdit.append('Количество точек в полученном слое: ' + str(self.templayer.GetFeatureCount()))

                # сохраняем результат в шейпфайл (код рабочий)
                fileDriver = ogr.GetDriverByName('ESRI Shapefile')
                fileDS = fileDriver.CreateDataSource(self.filepath)
                tmpDS = fileDriver.Open(self.filepath, 1)

                self.newlayer = fileDS.CopyLayer(self.templayer, self.filename, ['OVERWRITE=YES'])
                if self.newlayer is not None:
                    self.uploadLayer(self.filepath, self.filename, 'ogr')

                del inDS, tmpDS, outDS, fileDS




