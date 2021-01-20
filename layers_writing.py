from qgis.core import (
    QgsVectorFileWriter,
    QgsProject, QgsFields, QgsField, QgsWkbTypes, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer,
)
from qgis.PyQt.QtCore import QVariant

# class VectorFileWriter(QgsVectorFileWriter):
#     def __init__(self):
#         QgsVectorFileWriter.__init__(self)

def createFileDirectlyFromFeatures(): ## QgsVectorFileWriter has no attribute create
    # define fields for feature attributes. A QgsFields object is needed
    fields = QgsFields()
    fields.append(QgsField("first", QVariant.Int))
    fields.append(QgsField("second", QVariant.String))

    """ create an instance of vector file writer, which will create the vector file.
    Arguments:
    1. path to new file (will fail if exists already)
    2. field map
    3. geometry type - from WKBTYPE enum
    4. layer's spatial reference (instance of
       QgsCoordinateReferenceSystem)
    5. coordinate transform context
    6. save options (driver name for the output file, encoding etc.)
    """

    crs = QgsProject.instance().crs()
    transform_context = QgsProject.instance().transformContext()
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "ESRI Shapefile"
    save_options.fileEncoding = "UTF-8"

    writer = QgsVectorFileWriter.create(
        "testdata/my_new_shapefile.shp",
        fields,
        QgsWkbTypes.Point,
        crs,
        transform_context,
        save_options
    )

    if writer.hasError() != QgsVectorFileWriter.NoError:
        print("Error when creating shapefile: ", writer.errorMessage())

    # add a feature
    fet = QgsFeature()

    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 10)))
    fet.setAttributes([1, "text"])
    writer.addFeature(fet)

    # delete the writer to flush features to disk
    del writer

def saveLayerToFile(layer): ## QgsVectorFileWriter  has no attriburte writeAsVectorFormatV2
    # # SaveVectorOptions contains many settings for the writer process
    # save_options = QgsVectorFileWriter.SaveVectorOptions()
    # transform_context = QgsProject.instance().transformContext()
    # # Write to a GeoPackage (default)
    # error = QgsVectorFileWriter.writeAsVectorFormatV2(layer,
    #                                                   "testdata/my_new_file.gpkg",
    #                                                   transform_context,
    #                                                   save_options)
    # if error[0] == QgsVectorFileWriter.NoError:
    #     print("success!")
    # else:
    #     print(error)

    # Write to an ESRI Shapefile format dataset using UTF-8 text encoding
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "ESRI Shapefile"
    save_options.fileEncoding = "UTF-8"
    transform_context = QgsProject.instance().transformContext()
    # error = QgsVectorFileWriter.writeAsVectorFormatV2(layer,
    #                                                   "testdata/my_new_shapefile",
    #                                                   transform_context,
    #                                                   save_options)
    error = QgsVectorFileWriter.writeAsVectorFormat(layer,
                                                      "testdata/my_new_shapefile",
                                                      # transform_context,
                                                    layer.crs(),
                                                      save_options)
    # writer = QgsVectorFileWriter(fn, 'UTF-8', layerFields, QgsWkbTypes.Point, \
    #                              QgsCoordinateReferenceSystem('EPSG:26912'), 'ESRI Shapefile')
    if error[0] == QgsVectorFileWriter.NoError:
        print("success again!")
    else:
        print(error)

def createFromMemoryProvider():
    # create layer
    vl = QgsVectorLayer("Point", "temporary_points", "memory")
    pr = vl.dataProvider()

    # add fields
    pr.addAttributes([QgsField("name", QVariant.String),
                      QgsField("age", QVariant.Int),
                      QgsField("size", QVariant.Double)])
    vl.updateFields()  # tell the vector layer to fetch changes from the provider

    # add a feature
    fet = QgsFeature()
    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 10)))
    fet.setAttributes(["Johny", 2, 0.3])
    pr.addFeatures([fet])

    # update layer's extent when new features have been added
    # because change of extent in provider is not propagated to the layer
    vl.updateExtents()

    # show some stats
    print("fields:", len(pr.fields()))
    print("features:", pr.featureCount())
    e = vl.extent()
    print("extent:", e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum())

    # iterate over features
    features = vl.getFeatures()
    for fet in features:
        print("F:", fet.id(), fet.attributes(), fet.geometry().asPoint())

if __name__ == "__main__":
    # vlayer = QgsVectorLayer(r'M:\YandexDisk\QGIS\osgeopy\osgeopy-data\global\ne_50m_populated_places.shp', 'capital_cities', 'ogr')
    vlayer = QgsVectorLayer(r'M:\YandexDisk\QGIS\temp\newpoints.shp', 'degree_days', 'ogr')
    # for field in vlayer.fields():
    #     print(field.name(), field.typeName())

    # createFileDirectlyFromFeatures()
    saveLayerToFile(vlayer)
    # createFromMemoryProvider()
    pass


