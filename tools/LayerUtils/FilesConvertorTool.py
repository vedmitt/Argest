import csv

from osgeo import ogr, osr


class FilesConvertorTool:
    def __init__(self):
        pass

def csvToMemory(layerpath, csvFileAttrs):
    try:
        # Parse a delimited text file of volcano data and create a shapefile
        # use a dictionary reader so we can access by field name
        reader = csv.DictReader(
            open(layerpath, "rt",
                 encoding="utf8"),
            delimiter='\t',
            quoting=csv.QUOTE_NONE)

        # set up the shapefile driver
        driver = ogr.GetDriverByName('MEMORY')

        # create the data source
        outDS = driver.CreateDataSource('memData')

        # create the spatial reference, WGS84
        srs = osr.SpatialReference()
        espg = csvFileAttrs.get('crs').split(':')
        srs.ImportFromEPSG(int(espg[1]))

        # create the layer
        templayer = outDS.CreateLayer("temp_layer", srs, ogr.wkbPoint)

        # Add the all fields
        for field in reader.fieldnames:
            templayer.CreateField(ogr.FieldDefn(field, ogr.OFTString))
        #
        # Process the text file and add the attributes and features to the shapefile
        for row in reader:
            # create the feature
            feature = ogr.Feature(templayer.GetLayerDefn())
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
            templayer.CreateFeature(feature)

    except Exception as err:
        setTextStyle('red', 'bold')
        textEdit.append('\nНе удалось создать временный слой! ' + str(err))