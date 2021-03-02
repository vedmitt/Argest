import csv
import os
from random import randint

from osgeo import ogr, osr
from qgis._core import QgsProject

from .AzCalcTool import AzCalcTool
from .GuiElemIFace import GuiElemIFace
from .LayerGetter import LayerGetter
from .TimeCalcUtil import TimeCalcUtil


class LyrConvTool:
    inDS = None
    memDriver = None
    outDS = None
    templayer = None
    guiUtil = None

    def __init__(self, textEdit):
        LyrConvTool.guiUtil = GuiElemIFace(textEdit)

    def createTempLayer(self, curLayer):
        # get layer from combobox
        lg = LayerGetter()
        lg.getLayer(curLayer)

        LyrConvTool.guiUtil.setTextEditStyle('black', 'normal', 'Создаем новый слой...')

        try:
            if lg.driverName == "Delimited text file":
                self.csvToMemory(lg.layerpath, lg.csvFileAttrs)
            elif lg.driverName == "ESRI Shapefile":
                self.layerToMemory(lg.layer, lg.driverName, lg.layerpath)
        except Exception as err:
            LyrConvTool.guiUtil.setTextEditStyle('red', 'bold', '\nНе удалось создать временный слой! ' + str(err))

    def removeZeroPoints(self, boolChecked):
        # далее работаем с временным слоем
        if LyrConvTool.templayer is not None:
            LyrConvTool.guiUtil.setTextEditStyle('green', 'bold', 'Временный слой успешно создан!')
            LyrConvTool.guiUtil.setTextEditStyle('black', 'normal',
                                                 'Количество точек во временном слое: ' + str(
                                                     LyrConvTool.templayer.GetFeatureCount()))
            try:
                AzCalcTool(LyrConvTool.outDS, LyrConvTool.templayer, LyrConvTool.guiUtil).removeZeroPointsFromMemory(
                    boolChecked)
            except Exception as err:
                LyrConvTool.guiUtil.setTextEditStyle('red', 'bold', '\nНе удалось удалить нулевые точки! ' + str(err))

    def saveToFile(self, filename, filepath):
        if LyrConvTool.templayer and filepath is not None:
            try:
                self.saveTempLayerToFile(filename, filepath)
            except Exception as err:
                LyrConvTool.guiUtil.setTextEditStyle('red', 'bold',
                                                     '\nНе удалось сохранить/загрузить файл! ' + str(err))
        else:
            LyrConvTool.guiUtil.setTextEditStyle('red', 'bold', 'Введите данные в форму!\n')

    def mainAzimutCalc(self):
        try:
            AzCalcTool(LyrConvTool.outDS, LyrConvTool.templayer, LyrConvTool.guiUtil).mainAzimutCalc()
        except Exception as err:
            LyrConvTool.guiUtil.setTextEditStyle('red', 'bold', '\nНе удалось удалить избыточные точки! ' + str(err))

    def numbersForFlights(self, vlayerstr):
        try:
            lg = LayerGetter()
            lg.getLayer(vlayerstr)
            if lg.driverName == "ESRI Shapefile":
                self.layerToMemory(lg.layer, lg.driverName, lg.layerpath)

                TimeCalcUtil(LyrConvTool.guiUtil).setFlightNumber(LyrConvTool.outDS, LyrConvTool.templayer)

                fileName = 'test_' + str(randint(0000, 9999))
                filePath = "M:/Sourcetree/output/" + fileName + ".shp"
                self.saveToFile(fileName, filePath)
        except Exception as err:
            LyrConvTool.guiUtil.setTextEditStyle('red', 'bold', '\nНе удалось пронумеровать полеты! ' + str(err))

    ##----------------------------------------------------------------------------------------------------
    def csvToMemory(self, layerpath, csvFileAttrs):
        # Parse a delimited text file of volcano data and create a shapefile
        # use a dictionary reader so we can access by field name
        reader = csv.DictReader(
            open(layerpath, "rt",
                 encoding="utf8"),
            delimiter='\t',
            quoting=csv.QUOTE_NONE)

        # set up the shapefile memDriver
        LyrConvTool.memDriver = ogr.GetDriverByName('MEMORY')

        # create the data source
        LyrConvTool.outDS = LyrConvTool.memDriver.CreateDataSource('memData')

        # create the spatial reference, WGS84
        srs = osr.SpatialReference()
        espg = csvFileAttrs.get('crs').split(':')
        srs.ImportFromEPSG(int(espg[1]))

        # create the layer
        LyrConvTool.templayer = LyrConvTool.outDS.CreateLayer("temp_layer", srs, ogr.wkbPoint)

        # Add the all fields
        for field in reader.fieldnames:
            LyrConvTool.templayer.CreateField(ogr.FieldDefn(field, ogr.OFTString))
        #
        # Process the text file and add the attributes and features to the shapefile
        for row in reader:
            # create the feature
            feature = ogr.Feature(LyrConvTool.templayer.GetLayerDefn())
            # Set the attributes using the values from the delimited text file
            for item in row.keys():
                feature.SetField(item, row[item])

            # create the WKT for the feature using Python string formatting
            wkt = "POINT(%f %f)" % (float(row[csvFileAttrs.get('xField')]),
                                    float(row[csvFileAttrs.get('yField')]))

            # Create the point from the Well Known Txt
            point = ogr.CreateGeometryFromWkt(wkt)

            # Set the feature geometry using the point
            feature.SetGeometry(point)
            # Create the feature in the layer (shapefile)
            LyrConvTool.templayer.CreateFeature(feature)

    def layerToMemory(self, layer, driverName, layerpath):
        LyrConvTool.inDS = ogr.GetDriverByName(driverName).Open(layerpath, 0)

        # Get the input shapefile
        in_lyr = LyrConvTool.inDS.GetLayer()

        LyrConvTool.guiUtil.setTextEditStyle('black', 'normal',
                                             'Количество точек в оригинальном слое: ' + str(layer.featureCount()))

        # create an output datasource in memory
        LyrConvTool.memDriver = ogr.GetDriverByName('MEMORY')
        LyrConvTool.outDS = LyrConvTool.memDriver.CreateDataSource('memData')
        tmpDS = LyrConvTool.memDriver.Open('memData', 1)

        LyrConvTool.templayer = LyrConvTool.outDS.CopyLayer(in_lyr, 'temp_layer', ['OVERWRITE=YES'])

        # del self.inDS

    def saveTempLayerToFile(self, filename, filepath):
        # -------- сохраняем результат в шейпфайл (код рабочий) ----------------------
        LyrConvTool.guiUtil.setTextEditStyle('black', 'normal', '\nНачинаем сохранение файла...')

        fileDriver = ogr.GetDriverByName('ESRI Shapefile')

        # если слой уже существует и загружен, то удаляем его из проекта
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == filename:
                QgsProject.instance().removeMapLayers([layer.id()])
                # break

        if os.path.exists(filepath):
            fileDriver.DeleteDataSource(filepath)

        fileDS = fileDriver.CreateDataSource(filepath)
        newDS = fileDriver.Open(filepath, 1)

        newlayer = fileDS.CopyLayer(LyrConvTool.templayer, filename, ['OVERWRITE=YES'])

        LyrConvTool.guiUtil.setTextEditStyle('black', 'normal', 'Файл успешно сохранен!')

        if newlayer is not None:
            LyrConvTool.guiUtil.uploadLayer(filepath, filename, 'ogr')
            LyrConvTool.guiUtil.setTextEditStyle('green', 'bold', 'Слой успешно загружен в QGIS!')

        # del outDS, newDS, fileDS
