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
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
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
        self.mMapLayerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.checkBox.setChecked(True)
        self.toolButton.clicked.connect(self.getSaveFileName)
        self.pushButton.clicked.connect(self.doResult)

    def getSaveFileName(self):
        fn = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file')[0]
        self.lineEdit.setText(fn + '.shp')

    def getLayer(self):
        # get layer from combobox
        self.layer = self.mMapLayerComboBox.currentLayer()
        cur_lyr_path = self.layer.dataProvider().dataSourceUri()
        char_arr = cur_lyr_path.split('|')
        self.layerpath = char_arr[0]
        self.layername = self.layer.name()

    def getFilepath(self):
        # get file name from line edit
        self.filepath = self.lineEdit.text()
        fn = os.path.basename(self.filepath)
        fn = fn.split('.shp')
        self.filename = fn[0]

    def getAzimut(self):
        self.azimutUser = self.doubleSpinBox.value()

    def uploadLayer(self, filepath, filename, typeOfFile):
        # show our new layer in qgis
        layer = iface.addVectorLayer(filepath, filename, typeOfFile)
        if not layer:
            self.textEdit.append('Не удалось загрузить слой в оболочку!')

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

    def copyLayer(self):
        # copy the layer
        self.textEdit.setText('')
        self.textEdit.append('Создаем новый слой...')
        # self.textEdit.e

        # Open the folder data source for writing
        inds = ogr.Open(self.layerpath, 1)

        if inds is None:
            sys.exit('Could not open folder.')

        # Get the input shapefile
        in_lyr = inds.GetLayer()
        self.initFeatCount = in_lyr.GetFeatureCount()
        self.textEdit.append('Количество точек в оригинальном слое: ' + str(self.initFeatCount))

        # Create an output point layer
        drv = ogr.GetDriverByName('ESRI Shapefile')
        outds = drv.CreateDataSource(self.filepath)

        out_lyr = outds.CopyLayer(in_lyr, self.filename)
        del in_lyr, inds, outds
        if out_lyr is not None:
            # self.textEdit.append('Новый слой успешно создан!')
            del out_lyr
            return ['Новый слой успешно создан!', 1]
        else:
            return ['Произошла ошибка при создании файла!', 0]

    def remZeroPointsFromLayer(self):
        self.newlayer = QgsVectorLayer(self.filepath, self.filename, 'ogr')

        if self.checkBox.isChecked:
            self.textEdit.append('\nУдаление нулевых точек...')
            with edit(self.newlayer):
                # build a request to filter the features based on an attribute
                request = QgsFeatureRequest().setFilterExpression('"LON" = 0.0 and "LAT" = 0.0')

                # we don't need attributes or geometry, skip them to minimize overhead.
                # these lines are not strictly required but improve performance
                request.setSubsetOfAttributes([])
                request.setFlags(QgsFeatureRequest.NoGeometry)

                # loop over the features and delete
                for f in self.newlayer.getFeatures(request):
                    self.newlayer.deleteFeature(f.id())
                self.newlayer.updateFields()

        i = self.newlayer.featureCount()
        self.textEdit.append('Количество точек в новом слое: ' + str(i))
        self.textEdit.append('Количество точек удалено: ' + str(self.initFeatCount - i))


    def setFlightNumber(self):  ## working method
        # self.newlayer = QgsVectorLayer(r'M:\Sourcetree\bpla_plugin_flights\output\test1.shp', 'test1', 'ogr')

        # create new field with no content
        pr = self.newlayer.dataProvider()
        caps = pr.capabilities()
        request = QgsFeatureRequest()
        # request.setLimit(10)

        fieldNum = self.newlayer.fields().count()
        self.textEdit.append('\nНачинаем сквозную нумерацию полетов...')
        if caps & QgsVectorDataProvider.AddAttributes:
            new_field = [QgsField("FLIGHT_NUM", QVariant.Int)]
            if new_field not in self.newlayer.fields():
                pr.addAttributes(new_field)
                self.newlayer.updateFields()

        i = 1
        boolYesNo = False
        prevFeat = None
        nextFeat = None

        for feat in self.newlayer.getFeatures(request):
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
                self.changeFeatValues(self.newlayer, prevFeat.id(), attrs)
                self.changeFeatValues(self.newlayer, nextFeat.id(), attrs)
            elif nextFeat is not None:
                i += 1
                # add new flight number
                attrs = {fieldNum: i}
                self.changeFeatValues(self.newlayer, nextFeat.id(), attrs)

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
            self.newlayer.updateFields()

    #####------ Azimut calc --------------
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
        caps = self.newlayer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.DeleteFeatures:
            res = self.newlayer.dataProvider().deleteFeatures(delFeatIDs)

    def removePointsFromAzimut(self, prevFeat, nextFeat, delFeatIDs):
        angle = self.azimutCalc([prevFeat['LON'], prevFeat['LAT']], [nextFeat['LON'], nextFeat['LAT']])
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
        for feat in self.newlayer.getFeatures(request):
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
        self.textEdit.append('Количество точек в полученном слое: ' + str(self.newlayer.featureCount()))

        self.uploadLayer(self.filepath, self.filename, 'ogr')

    ##--------------END-----------------

    def doResult(self):
        self.getLayer()
        self.getFilepath()
        self.getAzimut()

        # self.layerToList()
        # self.removeZeroFeatures()
        # self.listToShapefile()

        # self.newlayer = QgsVectorLayer(r'M:\YandexDisk\QGIS\temp\test_pro1.shp', 'test_pro1', 'ogr')
        # self.azimutUser = 90

        res = self.copyLayer()
        self.textEdit.append(res[0])
        if res[1] != 0:
            self.remZeroPointsFromLayer()
            self.setFlightNumber()
            self.fromLayerCalcAzimut()




