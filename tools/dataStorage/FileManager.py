import os
# from qgis import processing
from qgis.core import edit

import processing
from qgis._core import *
from qgis.utils import iface

from .FileAttribute import FileAttribute


class FileManager:

    EXTENTIONS = {'.shp': 'ESRI Shapefile',
                  '.txt': 'delimitedtext'
                  }

    TYPEGEOM = {'polygon': QgsWkbTypes.Polygon,
                'multipoint': QgsWkbTypes.MultiPoint,
                'point': QgsWkbTypes.Point
                }

    def __init__(self, guiUtil=None):
        self.guiUtil = guiUtil

    def getFeatureGeometry(self, geom):
        geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
        if geom.type() == QgsWkbTypes.PointGeometry:
            # the geometry type can be of single or multi type
            if geomSingleType:
                x = geom.asPoint()
                typeOfGeom = 'Point'
            else:
                x = geom.asMultiPoint()
                typeOfGeom = 'MultiPoint'
        elif geom.type() == QgsWkbTypes.LineGeometry:
            if geomSingleType:
                x = geom.asPolyline()
                typeOfGeom = 'Line'
            else:
                x = geom.asMultiPolyline()
                typeOfGeom = 'MultiLine'
        elif geom.type() == QgsWkbTypes.PolygonGeometry:
            if geomSingleType:
                x = geom.asPolygon()
                typeOfGeom = 'Polygon'
            else:
                x = geom.asMultiPolygon()
                typeOfGeom = 'MultiPolygon'
        else:
            x = "Unknown or invalid geometry"
            typeOfGeom = "Unknown or invalid geometry"
        return x, typeOfGeom

    def getFieldsFromTXT(self, filepath, delimiter='\t'):
        with open(filepath) as reader:
            lines = reader.readlines(0)

        fields = lines[0].split(delimiter)
        return fields

    def getLayerTypeByExtension(self, ext):
        return FileManager.EXTENTIONS.get(ext)

    def getSaveFileAttr(self, lineEdit, isDir=False):  # get file name from line edit
        if lineEdit.text() != '':
            filepath = lineEdit.text()
            if not isDir:
                filename = os.path.basename(filepath).split('.')[0]
                return FileAttribute(filepath, filename)
            else:
                return FileAttribute(filepath)
        else:
            return None

    def getFilesAttrFromDir(self, inputDir, saveDirPath, out_ext):
        file_attr = []
        with os.scandir(inputDir) as dir:
            for file in dir:
                in_fn, in_ex = os.path.splitext(file)  # /path/to/file , .extention

                if self.getLayerTypeByExtension(in_ex) is not None:
                    in_fpath = in_fn + in_ex
                    in_fname = file.name.split(in_ex)[0] + "_test"

                    in_file_attr = FileAttribute(in_fpath, in_fname, in_ex)
                    save_file_attr = FileAttribute(saveDirPath + '/' + in_fname + out_ext, in_fname, out_ext)

                    res = [in_file_attr, save_file_attr]
                    file_attr.append(res)

        return file_attr

    def getFirstFileAttrFromDir(self, inputDir):
        file_attr = None
        with os.scandir(inputDir) as dir:
            for file in dir:
                in_fn, in_ex = os.path.splitext(file)  # /path/to/file , .extention

                if self.getLayerTypeByExtension(in_ex) is not None:
                    in_fpath = in_fn + in_ex
                    # in_fname = file.name.split(in_ex)[0]
                    # file_attr = FileAttribute(in_fpath, in_fname, in_ex)
                    file_attr = FileAttribute(in_fpath)
                    break
        return file_attr

    def getQgsVectorLayer(self, inputFileAttr, txtParams=None):  # [ str or FileAttribute, FileAttribute ]
        vlayer = None

        if isinstance(inputFileAttr, str):  # если слой из комбобокса
            lg = FileManager()
            vlayer = lg.getVlayerFromCanvasByName(inputFileAttr)

        else:  # если слой из файла
            fileType = self.getLayerTypeByExtension(inputFileAttr.getFileExtension())
            file_path = inputFileAttr.getFilePath()
            file_name = inputFileAttr.getFileName()

            if fileType == 'delimitedtext':
                delimiters = {'Tab': '%5Ct'}
                delimiter = delimiters.get(txtParams.get('delimiter'))  # '%5Ct'
                xfield = txtParams.get('xfield')  # 'LON'
                yfield = txtParams.get('yfield')  # 'LAT'
                crs = txtParams.get('crs')  # 'EPSG:28402'
                uri = "file:///" + file_path + "?type=csv&delimiter=" + delimiter + \
                      "&maxFields=10000&detectTypes=yes&xField=" + xfield + "&yField=" + yfield + \
                      "&zField=ALT&crs=" + crs + "&spatialIndex=no&subsetIndex=no&watchFile=no"
                vlayer = QgsVectorLayer(uri, file_name, fileType)

            elif fileType == 'ESRI Shapefile':
                vlayer = QgsVectorLayer(file_path, file_name, "ogr")

        return vlayer

    def getActiveLayersFromCanvas(self, exclude_lyr=None):
        actVecLyrDict = {}
        layers = iface.mapCanvas().layers()  # по умолчанию только видимые слои
        for item in layers:
            if item.name() != exclude_lyr:
                actVecLyrDict.setdefault(item.name(), item)
        return actVecLyrDict

    def getVlayerFromCanvasByName(self, layerstr):
        layer = self.getActiveLayersFromCanvas().get(layerstr)  # QgsVectorLayer ?
        return layer

    def uploadLayer(self, file_path):
        # show the layer in qgis
        layer = iface.addVectorLayer(file_path, '', 'ogr')
        if not layer:
            return -1, '\nНе удалось загрузить слой в оболочку!'
        else:
            return 1, '\nСлой успешно сохранен и загружен в QGIS!'

    def removeLyrFromLegend(self, lyrName):
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == lyrName:
                QgsProject.instance().removeMapLayers([lyr.id()])

    def createNewFileByExtension(self, type, features, filepath):
        # записываем объекты в новый слой
        if type.get('txt'):
            mess = self.createNewTextfile(features, filepath, '\t')
            return mess

        elif type.get('shp'):
            mess = self.createNewShapefile(features, filepath, "UTF-8")
            return mess


    def createNewShapefile(self, features, file_path, fileEncoding='utf-8', geometry=None, beUploaded=True):
        """ Создает новый шейпфайл из объектов Features """
        newfields = QgsFields()
        fields = features.getFieldDict()

        for field in fields:
            newfields.append(QgsField(field, fields.get(field)))

        crs = QgsProject.instance().crs()
        transform_context = QgsProject.instance().transformContext()
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = "ESRI Shapefile"
        save_options.fileEncoding = fileEncoding

        writer = QgsVectorFileWriter.create(
            file_path,
            newfields,
            QgsWkbTypes.Point,
            crs,
            transform_context,
            save_options
        )

        # add features
        feat_list = features.getFeatures()
        for i in range(len(feat_list)):
            f = QgsFeature()
            if geometry is None:  # используем старую геометрию слоя
                coordinates = feat_list[i].getGeometry()
                # f.setGeometry(QgsGeometry.fromPointXY(geom))
                f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coordinates)))
            else:  # присваиваем новую геометрию
                point = 'POINT(' + str(geometry[i][0]) + ' ' + str(geometry[i][1]) + ')'
                geom = QgsGeometry.fromWkt(point)
                f.setGeometry(geom)
            f.setAttributes(features.getOrderedValList(i))

            writer.addFeature(f)
            i += 1

        # delete the writer to flush features to disk
        del writer
        if beUploaded:
            mess = self.uploadLayer(file_path)
            return mess
        else:
            return 'Файл успешно создан!'

    def createNewTextfile(self, features, file_path, separator):
        with open(file_path, 'w') as my_file:  # Change the path of the file
            fields = features.getFields()
            field_str = ''
            for field in fields:
                field_str = field_str + field + separator
            my_file.write(field_str)

            for i in range(features.featureCount()):
                turple_str = ''
                values = features.getOrderedValList(i)
                for val in values:
                    turple_str = turple_str + str(val) + separator
                my_file.write('\n' + turple_str)

            my_file.close()  # close the file

        return 1, 'Файл успешно сохранен!\n'

    def createLayerByWriter(self, fields, feats, crs, outFn, typeName='polygon', newGeom=None):
        typeGeom = FileManager.TYPEGEOM.get(typeName)
        writer = QgsVectorFileWriter(outFn, 'UTF-8', fields, typeGeom, crs, 'ESRI Shapefile')
        i = 0
        for feat in feats:
            if newGeom is None:
                geom = feat.geometry()
            else:
                geom = QgsGeometry.fromWkt('POINT (' + str(newGeom[i][0]) + ' ' + str(newGeom[i][1]) + ')')
            feat.setGeometry(geom)
            writer.addFeature(feat)
            i += 1
        del(writer)
        return 1, 'Файл успешно сохранен!\n'

    def makeBufferOperation(self, layer, outFn):
        fields = layer.fields()
        feats = layer.getFeatures()

        writer = QgsVectorFileWriter(outFn, 'UTF-8', fields, QgsWkbTypes.Polygon, layer.sourceCrs(), 'ESRI Shapefile')
        bufferDist = 10
        for feat in feats:
            geom = feat.geometry()
            buff = geom.buffer(bufferDist, 5, QgsGeometry.CapRound, QgsGeometry.JoinStyleRound, 2.0)
            feat.setGeometry(buff)
            writer.addFeature(feat)
        del(writer)
        return 1, 'Файл Buffered успешно создан!\n'

    def makeDissolveOperation(self, inFn, outFn):
        processing.run("native:dissolve", {'INPUT': inFn, 'FIELD': ['FLIGHT_NUM'], 'OUTPUT': outFn})
        return 1, 'Файл Dissolved успешно создан!\n'

    def intersectionOperation(self, lyr1, lyr2, outFn, input_fields=[], overlay_fields=[]):
        params = {'INPUT': lyr1,
                  'INPUT_FIELDS': input_fields,
                  'OUTPUT': outFn,
                  'OVERLAY': lyr2,
                  'OVERLAY_FIELDS': overlay_fields,
                  'OVERLAY_FIELDS_PREFIX': ''
                  }
        processing.run("native:intersection", params)
        return 1, 'Операция intersection успешно выполнена!\n'

    def multipartToSingleparts(self, in_fpath, out_fpath):
        params = {'INPUT': in_fpath,
                  'OUTPUT': out_fpath,
                  }
        processing.run("native:multiparttosingleparts", params)
        return 1, 'Операция multiparts to singleparts успешно выполнена!\n'

    def createFieldByExpression(self, inFn, field, type, expression):
        # create new area field
        layer = QgsVectorLayer(inFn, '', 'ogr')
        pv = layer.dataProvider()
        pv.addAttributes([QgsField(field, type)])
        layer.updateFields()
        expression = QgsExpression(expression)
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))

        with edit(layer):
            for f in layer.getFeatures():
                context.setFeature(f)
                f[field] = expression.evaluate(context)
                layer.updateFeature(f)

        return 1, 'Поле ' + field + ' создано!\n'

    def createVirtualLayerByQuery(self, sql, layerName):
        vlayer = QgsVectorLayer(sql, layerName, "virtual")
        return vlayer

    def makeJoinOperation(self, csv, shp, csvField, shpField, outFn):
        joinObject = QgsVectorLayerJoinInfo()
        joinObject.setJoinFieldName(csvField)
        joinObject.setTargetFieldName(shpField)
        joinObject.setJoinLayerId(csv.id())
        joinObject.setUsingMemoryCache(True)
        joinObject.setJoinLayer(csv)
        shp.addJoin(joinObject)

        parameters = {'INPUT': shp,
                      'INPUT_2': csv,
                      'FIELD': shpField,
                      'FIELD_2': csvField,
                      'OUTPUT': outFn}

        # result = processing.runAndLoadResults('qgis:joinattributestable', parameters)
        result = processing.run("qgis:joinattributestable", parameters)
        # result = processing.runandload('qgis:joinattributestable', shp, csv, shpField, csvField, None)
        # QgsProject.instance().addMapLayer(result)
        return 1, 'Операция Joins успешно выполнена!\n'

    def mergeVectorLayers(self, vlayers, outFn, csv=None):
        parameters = {'LAYERS': vlayers,
                      'CRS': csv,
                      'OUTPUT': outFn}
        result = processing.run("native:mergevectorlayers", parameters)
        return 1, 'Операция mergeVectorLayers успешно выполнена!\n'

    def removeFields(self, layer, indexes):
        caps = layer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.DeleteAttributes:
            res = layer.dataProvider().deleteAttributes(indexes)

    def selectByExpression(self, layer, expression=None):
        if expression is None:
            layer.selectAll()
        else:
            layer.selectByExpression(expression)
        fields = layer.fields()
        feats = layer.selectedFeatures()
        return fields, feats

    def removeFile(self, fpath):
        if os.path.exists(fpath):
            os.remove(fpath)

    def removeShapeFile(self, outDir, fname):
        self.removeFile(os.path.join(outDir, fname + '.shp'))
        self.removeFile(os.path.join(outDir, fname + '.shx'))
        self.removeFile(os.path.join(outDir, fname + '.cpg'))
        self.removeFile(os.path.join(outDir, fname + '.dbf'))
        self.removeFile(os.path.join(outDir, fname + '.prj'))




