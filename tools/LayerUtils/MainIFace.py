import csv
import os
from random import randint

from osgeo import ogr, osr
from qgis._core import QgsProject

from .FilesTool import FilesTool
from .FeatCalcTool import FeatCalcTool
from .FeatCalcTool import *
from .GuiElemIFace import GuiElemIFace
from .LayerGetter import LayerGetter
from .NumCalcUtil import NumCalcUtil


class MainIFace:

    def __init__(self, guiUtil):
        # self.guiUtil = GuiElemIFace(textEdit)
        self.guiUtil = guiUtil
        self.outDS = None
        self.inDS = None
        self.temLyr = None
        self.memDriver = None

    def exceptionsDecorator(self, function_to_decorate, errStr):
        def the_wrapper_around_the_original_function():
            try:
                function_to_decorate()  # Сама функция
            except Exception as err:
                self.guiUtil.setOutputStyle('red', 'bold', errStr + str(err))

        return the_wrapper_around_the_original_function

    def createTempLayer(self, lg):
        # get layer from combobox
        # lg = LayerGetter()
        # lg.getLayer(curLayer)

        self.guiUtil.setOutputStyle('black', 'normal', 'Создаем новый слой...')

        ft = FilesTool(self.guiUtil)
        if lg.driverName == "Delimited text file":
            ft.csvToMemory(lg.layerpath, lg.csvFileAttrs)
        elif lg.driverName == "ESRI Shapefile":
            self.outDS, self.temLyr = ft.layerToMemory(lg.driverName, lg.layerpath)
            # return tlyr
        return None

    def removeZeroPoints(self, boolChecked):
        # далее работаем с временным слоем
        if self.temLyr is not None:
            self.guiUtil.setOutputStyle('black', 'normal',
                                                 'Количество точек во временном слое: ' + str(
                                                     self.temLyr.GetFeatureCount()))

            FeatCalcTool(self.outDS, self.temLyr, self.guiUtil).removeZeroPointsFromMemory(boolChecked)

    def saveToFile(self, filename, filepath):
        if filepath is not None:
            FilesTool(self.guiUtil).saveTempLayerToFile(self.temLyr, filename, filepath)
        else:
            self.guiUtil.setOutputStyle('red', 'bold', 'Введите данные в форму!\n')

    def mainAzimutCalc(self):
        # try:
        FeatCalcTool(self.outDS, self.temLyr, self.guiUtil).mainAzimutCalc()
        # except Exception as err:
        #     self.guiUtil.setOutputStyle('red', 'bold', '\nНе удалось классифицировать точки! ' + str(err))

    def numbersForFlights(self, vlayerstr):
        # try:
        lg = LayerGetter()
        lg.getLayer(vlayerstr)
        if lg.driverName == "ESRI Shapefile":
            FilesTool(self.guiUtil).layerToMemory(lg.driverName, lg.layerpath)

            NumCalcUtil(self.guiUtil).setFlightNumber(self.outDS, self.temLyr)

            fileName = 'test_' + str(randint(0000, 9999))
            filePath = "M:/Sourcetree/output/" + fileName + ".shp"
            self.saveToFile(fileName, filePath)
        # except Exception as err:
        #     self.guiUtil.setOutputStyle('red', 'bold', '\nНе удалось пронумеровать полеты! ' + str(err))

