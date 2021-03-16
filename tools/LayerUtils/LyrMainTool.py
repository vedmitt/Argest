import csv
import os
from random import randint

from osgeo import ogr, osr
from qgis._core import QgsProject

from .FeatCalcTool import FeatCalcTool
from .FeatCalcTool import *
from .GuiElemIFace import GuiElemIFace
from .LayerGetter import LayerGetter
from .NumCalcUtil import NumCalcUtil


class LyrMainTool:
    inDS = None
    memDriver = None
    outDS = None
    templayer = None
    guiUtil = None

    def __init__(self, textEdit):
        LyrMainTool.guiUtil = GuiElemIFace(textEdit)

    def createOnePlanLayer(self, folderPath):
        try:
            driverName = 'ESRI Shapefile'
            feat_list = None
            with os.scandir(folderPath) as entries:
                i = 0
                for entry in entries:
                    if os.path.isdir(entry):
                        # LyrMainTool.guiUtil.setTextEditStyle('black', 'normal', str(entry.name))
                        with os.scandir(entry) as dir:
                            for file in dir:
                                filename, file_extension = os.path.splitext(file)
                                if file_extension == ".shp":
                                    filepath = folderPath + '/' + entry.name + '/' + file.name
                                    ftool = FeatCalcTool(LyrMainTool.outDS, LyrMainTool.templayer, LyrMainTool.guiUtil)
                                    # copy the first layer to temp
                                    if i == 0:
                                        self.layerToMemory(driverName, filepath)
                                        feat_list = ftool.tempLayerToListFeat(LyrMainTool.templayer)
                                        i += 1
                                    elif i > 0:
                                        newDS = ogr.GetDriverByName(driverName).Open(filepath, 0)
                                        new_lyr = newDS.GetLayer()
                                        feat_list.append(ftool.tempLayerToListFeat(new_lyr))
                                        for feature in new_lyr:
                                            LyrMainTool.templayer.CreateFeature(feature)

            # save all features in list to file
            LyrMainTool.outDS.SyncToDisk()
            # fileName = 'basic_outline_' + str(randint(0000, 9999))
            # filePath = folderPath + '/' + fileName + ".shp"
            # LyrMainTool.guiUtil.setTextEditStyle('black', 'normal', filePath)
            # self.saveToFile(fileName, filePath)

            av_az = AzimutMathUtil().averageAzimut(feat_list)
            LyrMainTool.guiUtil.setTextEditStyle('black', 'normal', str(av_az))

        except Exception as err:
            LyrMainTool.guiUtil.setTextEditStyle('red', 'bold', '\nНе удалось открыть папку с файлами! ' + str(err))


    def createTempLayer(self, curLayer):
        # get layer from combobox
        lg = LayerGetter()
        lg.getLayer(curLayer)

        LyrMainTool.guiUtil.setTextEditStyle('black', 'normal', 'Создаем новый слой...')

        try:
            if lg.driverName == "Delimited text file":
                self.csvToMemory(lg.layerpath, lg.csvFileAttrs)
            elif lg.driverName == "ESRI Shapefile":
                self.layerToMemory(lg.driverName, lg.layerpath)
        except Exception as err:
            LyrMainTool.guiUtil.setTextEditStyle('red', 'bold', '\nНе удалось создать временный слой! ' + str(err))

    def removeZeroPoints(self, boolChecked):
        # далее работаем с временным слоем
        if LyrMainTool.templayer is not None:
            LyrMainTool.guiUtil.setTextEditStyle('black', 'normal',
                                                 'Количество точек во временном слое: ' + str(
                                                     LyrMainTool.templayer.GetFeatureCount()))
            try:
                FeatCalcTool(LyrMainTool.outDS, LyrMainTool.templayer, LyrMainTool.guiUtil).removeZeroPointsFromMemory(
                    boolChecked)
            except Exception as err:
                LyrMainTool.guiUtil.setTextEditStyle('red', 'bold', '\nНе удалось удалить нулевые точки! ' + str(err))

    def saveToFile(self, filename, filepath):
        if LyrMainTool.templayer and filepath is not None:
            try:
                self.saveTempLayerToFile(filename, filepath)
            except Exception as err:
                LyrMainTool.guiUtil.setTextEditStyle('red', 'bold',
                                                     '\nНе удалось сохранить/загрузить файл! ' + str(err))
        else:
            LyrMainTool.guiUtil.setTextEditStyle('red', 'bold', 'Введите данные в форму!\n')

    def mainAzimutCalc(self):
        try:
            FeatCalcTool(LyrMainTool.outDS, LyrMainTool.templayer, LyrMainTool.guiUtil).mainAzimutCalc()
        except Exception as err:
            LyrMainTool.guiUtil.setTextEditStyle('red', 'bold', '\nНе удалось классифицировать точки! ' + str(err))

    def numbersForFlights(self, vlayerstr):
        try:
            lg = LayerGetter()
            lg.getLayer(vlayerstr)
            if lg.driverName == "ESRI Shapefile":
                self.layerToMemory(lg.driverName, lg.layerpath)

                NumCalcUtil(LyrMainTool.guiUtil).setFlightNumber(LyrMainTool.outDS, LyrMainTool.templayer)

                fileName = 'test_' + str(randint(0000, 9999))
                filePath = "M:/Sourcetree/output/" + fileName + ".shp"
                self.saveToFile(fileName, filePath)
        except Exception as err:
            LyrMainTool.guiUtil.setTextEditStyle('red', 'bold', '\nНе удалось пронумеровать полеты! ' + str(err))

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
        LyrMainTool.memDriver = ogr.GetDriverByName('MEMORY')

        # create the data source
        LyrMainTool.outDS = LyrMainTool.memDriver.CreateDataSource('memData')

        # create the spatial reference, WGS84
        srs = osr.SpatialReference()
        espg = csvFileAttrs.get('crs').split(':')
        srs.ImportFromEPSG(int(espg[1]))

        # create the layer
        LyrMainTool.templayer = LyrMainTool.outDS.CreateLayer("temp_layer", srs, ogr.wkbPoint)

        # Add the all fields
        for field in reader.fieldnames:
            LyrMainTool.templayer.CreateField(ogr.FieldDefn(field, ogr.OFTString))
        #
        # Process the text file and add the attributes and features to the shapefile
        for row in reader:
            # create the feature
            feature = ogr.Feature(LyrMainTool.templayer.GetLayerDefn())
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
            LyrMainTool.templayer.CreateFeature(feature)

    def layerToMemory(self, driverName, layerpath):
        try:
            LyrMainTool.inDS = ogr.GetDriverByName(driverName).Open(layerpath, 0)

            # Get the input shapefile
            in_lyr = LyrMainTool.inDS.GetLayer()

            # LyrMainTool.guiUtil.setTextEditStyle('black', 'normal', 'Количество точек в оригинальном слое: ' + str(
            # in_lyr.featureCount()))

            # create an output datasource in memory
            LyrMainTool.memDriver = ogr.GetDriverByName('MEMORY')
            LyrMainTool.outDS = LyrMainTool.memDriver.CreateDataSource('memData')
            tmpDS = LyrMainTool.memDriver.Open('memData', 1)

            LyrMainTool.templayer = LyrMainTool.outDS.CopyLayer(in_lyr, 'temp_layer', ['OVERWRITE=YES'])
            LyrMainTool.guiUtil.setTextEditStyle('green', 'bold', 'Временный слой успешно создан!')
            # del self.inDS
            # return LyrMainTool.templayer
        except Exception as err:
            LyrMainTool.guiUtil.setTextEditStyle('red', 'bold', '\nНе удалось создать временный слой! ' + str(err))

    def saveTempLayerToFile(self, filename, filepath):
        # -------- сохраняем результат в шейпфайл (код рабочий) ----------------------
        LyrMainTool.guiUtil.setTextEditStyle('black', 'normal', '\nНачинаем сохранение файла...')

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

        newlayer = fileDS.CopyLayer(LyrMainTool.templayer, filename, ['OVERWRITE=YES'])

        LyrMainTool.guiUtil.setTextEditStyle('black', 'normal', 'Файл успешно сохранен!')

        if newlayer is not None:
            LyrMainTool.guiUtil.uploadLayer(filepath, filename, 'ogr')
            LyrMainTool.guiUtil.setTextEditStyle('green', 'bold', 'Слой успешно загружен в QGIS!')

        # del outDS, newDS, fileDS
