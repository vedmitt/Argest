# dataformat1 = '2020-03-15T11:28:12'
# dataformat2 = '05-09-2020T02:06:37,000000'
# dataformat3 = '2020/08/19 04:56:19.000'
#
# import dateutil.parser
# yourdate = dateutil.parser.parse(dataformat1)
# print(yourdate)

# vlayer = QgsVectorLayer(r"M:\Sourcetree\input_data\Jarchiha\Jarchiha_all_data.shp", "archiha_all_data", "ogr")

from osgeo import ogr
import os

DriverName = "ESRI Shapefile"      # e.g.: GeoJSON, ESRI Shapefile
FileName = r"M:\Sourcetree\output\test_.shp"
driver = ogr.GetDriverByName(DriverName)

dataSource = driver.Open(FileName, 0)  # 0 means read-only. 1 means writeable.

# Check to see if shapefile is found.
if dataSource is None:
    print('Could not open %s' % FileName)
else:
    print('Opened %s' % FileName)
    layer = dataSource.GetLayer()
    # featureCount = layer.GetFeatureCount()
    # print("Number of features in %s: %d" % (os.path.basename(FileName),featureCount))

    layerDefinition = layer.GetLayerDefn()
    fields_list = [layerDefinition.GetFieldDefn(n).name for n in range(layerDefinition.GetFieldCount())]
    print(fields_list)
    if 'CLASS' in fields_list:
        print("Yes")

dataSource = None
layer = None
