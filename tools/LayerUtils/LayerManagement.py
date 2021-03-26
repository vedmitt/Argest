import csv
import os

from osgeo import osr, ogr
from qgis._core import QgsProject
from numba import njit, prange

from .AzimutMathUtil import AzimutMathUtil
from .ClassificationTool_1 import ClassificationTool_1


class LayerManagement:
    def __init__(self, guiUtil):
        self.guiUtil = guiUtil
        self.outDS = None
        self.inDS = None
        self.templayer = None
        self.memDriver = None

    def csvToMemory(self, layerpath, csvFileAttrs):
        # Parse a delimited text file of volcano data and create a shapefile
        # use a dictionary reader so we can access by field name
        reader = csv.DictReader(
            open(layerpath, "rt",
                 encoding="utf8"),
            delimiter='\t',
            quoting=csv.QUOTE_NONE)

        # set up the shapefile memDriver
        self.memDriver = ogr.GetDriverByName('MEMORY')

        # create the data source
        self.outDS = self.memDriver.CreateDataSource('memData')

        # create the spatial reference, WGS84
        srs = osr.SpatialReference()
        espg = csvFileAttrs.get('crs').split(':')
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
            wkt = "POINT(%f %f)" % (float(row[csvFileAttrs.get('xField')]),
                                    float(row[csvFileAttrs.get('yField')]))

            # Create the point from the Well Known Txt
            point = ogr.CreateGeometryFromWkt(wkt)

            # Set the feature geometry using the point
            feature.SetGeometry(point)
            # Create the feature in the layer (shapefile)
            self.templayer.CreateFeature(feature)

    # @njit(fastmath=True, cache=True)
    def layerToMemory(self, driverName, layerpath):
        self.inDS = ogr.GetDriverByName(driverName).Open(layerpath, 0)

        # Get the input shapefile
        in_lyr = self.inDS.GetLayer()

        # create an output datasource in memory
        self.memDriver = ogr.GetDriverByName('MEMORY')
        self.outDS = self.memDriver.CreateDataSource('memData')
        tmpDS = self.memDriver.Open('memData', 1)

        self.templayer = self.outDS.CopyLayer(in_lyr, 'temp_layer', ['OVERWRITE=YES'])

        self.guiUtil.setOutputStyle('black', 'normal', 'Количество точек в слое: ' + str(
            self.templayer.GetFeatureCount()))
        self.guiUtil.setOutputStyle('green', 'bold', 'Временный слой успешно создан!')
        # del self.inDS
        return self.outDS, self.templayer

    # @njit(fastmath=True, cache=True)
    def saveTempLayerToFile(self, templayer, filename, filepath):
        # -------- сохраняем результат в шейпфайл (код рабочий) ----------------------
        self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем сохранение файла...')

        fileDriver = ogr.GetDriverByName('ESRI Shapefile')

        # если слой уже существует и загружен, то удаляем его из проекта
        # for layer in QgsProject.instance().mapLayers().values():
        #     if layer.name() == filename:
        #         QgsProject.instance().removeMapLayers([layer.id()])
        #         # break

        if os.path.exists(filepath):
            fileDriver.DeleteDataSource(filepath)

        fileDS = fileDriver.CreateDataSource(filepath)
        newDS = fileDriver.Open(filepath, 1)

        newlayer = fileDS.CopyLayer(templayer, filename, ['OVERWRITE=YES'])

        self.guiUtil.setOutputStyle('black', 'normal', 'Файл успешно сохранен!')

        if newlayer is not None:
            self.guiUtil.uploadLayer(filepath, filename, 'ogr')
            self.guiUtil.setOutputStyle('green', 'bold', 'Слой успешно загружен в QGIS!')

        # del outDS, newDS, fileDS

    def createOnePlanLayer(self, folderPath):
        driverName = 'ESRI Shapefile'
        feat_list = None
        with os.scandir(folderPath) as entries:
            i = 0
            for entry in entries:
                if os.path.isdir(entry):
                    # self.guiUtil.setTextEditStyle('black', 'normal', str(entry.name))
                    with os.scandir(entry) as dir:
                        for file in dir:
                            filename, file_extension = os.path.splitext(file)
                            if file_extension == ".shp":
                                filepath = folderPath + '/' + entry.name + '/' + file.name
                                ftool = ClassificationTool_1(self.outDS, self.templayer, self.guiUtil)
                                # copy the first layer to temp
                                if i == 0:
                                    self.layerToMemory(driverName, filepath)
                                    feat_list = ftool.tempLayerToListFeat(self.templayer)
                                    i += 1
                                elif i > 0:
                                    newDS = ogr.GetDriverByName(driverName).Open(filepath, 0)
                                    new_lyr = newDS.GetLayer()
                                    feat_list.append(ftool.tempLayerToListFeat(new_lyr))
                                    for feature in new_lyr:
                                        self.templayer.CreateFeature(feature)

        # save all features in list to file
        self.outDS.SyncToDisk()
        # fileName = 'basic_outline_' + str(randint(0000, 9999))
        # filePath = folderPath + '/' + fileName + ".shp"
        # self.guiUtil.setTextEditStyle('black', 'normal', filePath)
        # self.saveToFile(fileName, filePath)

        av_az = AzimutMathUtil().averageAzimut(feat_list)
        self.guiUtil.setOutputStyle('black', 'normal', str(av_az))

        # except Exception as err:
        #     self.guiUtil.setTextEditStyle('red', 'bold', '\nНе удалось открыть папку с файлами! ' + str(err))
