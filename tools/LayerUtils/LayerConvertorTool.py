import csv
import os

from osgeo import ogr, osr
from qgis._core import QgsProject

# import LayerGetter
from .GuiElemIFace import GuiElemIFace


class LayerConvertorTool:

    def __init__(self):
        self.inDS = None
        self.memDriver = None
        self.outDS = None
        self.templayer = None

    def csvToMemory(self, textEdit, layerpath, csvFileAttrs):
        GuiElemIFace().setTextStyle(textEdit, 'black', 'normal', 'Создаем новый слой...')
        try:
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

        except Exception as err:
            GuiElemIFace().setTextStyle(textEdit, 'red', 'bold', '\nНе удалось создать временный слой! ' + str(err))


    def layerToMemory(self, textEdit, layer, driverName, layerpath):
        GuiElemIFace().setTextStyle(textEdit, 'black', 'normal', 'Создаем новый слой...')

        try:

            self.inDS = ogr.GetDriverByName(driverName).Open(layerpath, 0)

            # Get the input shapefile
            in_lyr = self.inDS.GetLayer()

            textEdit.append('Количество точек в оригинальном слое: ' + str(layer.featureCount()))

            # create an output datasource in memory
            self.memDriver = ogr.GetDriverByName('MEMORY')
            self.outDS = self.memDriver.CreateDataSource('memData')
            tmpDS = self.memDriver.Open('memData', 1)

            self.templayer = self.outDS.CopyLayer(in_lyr, 'temp_layer', ['OVERWRITE=YES'])

            # del self.inDS
        except Exception as err:
            GuiElemIFace().setTextStyle(textEdit, 'red', 'bold', '\nНе удалось создать временный слой! ' + str(err))


    def saveTempLayerToFile(self, textEdit, filename, filepath, qgproject):
        # -------- сохраняем результат в шейпфайл (код рабочий) ----------------------
        try:
            fileDriver = ogr.GetDriverByName('ESRI Shapefile')

            # если слой уже существует и загружен, то удаляем его из проекта
            for layer in qgproject.mapLayers().values():
                if layer.name() == filename:
                    qgproject.removeMapLayers([layer.id()])
                    break

            if os.path.exists(filepath):
                fileDriver.DeleteDataSource(filepath)

            fileDS = fileDriver.CreateDataSource(filepath)
            newDS = fileDriver.Open(filepath, 1)

            newlayer = fileDS.CopyLayer(self.templayer, filename, ['OVERWRITE=YES'])
            # if newlayer is not None:
            #     LayerGetter.uploadLayer(filepath, filename, 'ogr')
            #     LayerGetter.setTextStyle('green', 'bold')
            #     textEdit.append('Слой успешно загружен в QGIS!')
            #     LayerGetter.setTextStyle('black', 'normal')
        except Exception as err:
            GuiElemIFace().setTextStyle(textEdit, 'red', 'bold', '\nНе удалось сохранить файл! ' + str(err))

        # del outDS, newDS, fileDS
