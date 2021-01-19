import os
import sys
from osgeo import ogr

# fn = r'D:\Ronya\YandexDisk\QGIS\my_data_source\shapefiles\20200905_F25_27_wMagnCoord.shp'
# fn = r'D:\Ronya\YandexDisk\QGIS\osgeopy\osgeopy-data\global\ne_50m_populated_places.shp'
fn = r'M:\YandexDisk\QGIS\osgeopy\osgeopy-data\global\ne_50m_populated_places.shp'

# def printAttributes(fn): #working on home PC
#     import ospybook as pb
#     # pb.print_attributes(fn, 3, ['T', 'TIME'])
#     pb.print_attributes(fn, 3, ['NAME', 'POP_MAX'])

# def showVectorPlot(): #not working
#     from ospybook.vectorplotter import VectorPlotter
#     os.chdir(r'D:\Ronya\YandexDisk\QGIS\osgeopy\osgeopy-data\global')
#     vp = VectorPlotter(True)
#     vp.plot('ne_50m_admin_0_countries.shp', fill=False)
#     vp.plot('ne_50m_populated_places.shp', 'bo')

def readData(fn): #working
    ds = ogr.Open(fn, 0)
    if ds is None:
        sys.exit('Could not open {0}.'.format(fn))
    lyr = ds.GetLayer(0)
    num_features = lyr.GetFeatureCount()
    print('\n All features amount: {0}'.format(num_features))

    i = 0
    for feat in lyr:
        pt = feat.geometry()
        x = pt.GetX() #longitude
        y = pt.GetY() #latitude
        if (x!=0 and y!=0):
            # t = feat.GetField('T')
            # time = feat.GetField('TIME')
            t = feat.GetField('FEATURECLA')
            time = feat.GetField('NAME')
            print(x, y,"  " , t," ", time)  
            i += 1
            if i == 10:
                break
    del ds

def writeData():
    # Open the folder dataa source for writing
    # ds = ogr.Open(r'D:\Ronya\YandexDisk\QGIS\osgeopy\osgeopy-data\global', 1)
    ds = ogr.Open(r'M:\YandexDisk\QGIS\osgeopy\osgeopy-data\global', 1)
    if ds is None:
        sys.exit('Could not open folder.')

    # Get the input shapefile
    in_lyr = ds.GetLayer('ne_50m_populated_places')

    # Create a point layer
    if ds.GetLayer('capital_cities'):
        ds.DeleteLayer('capital_cities')
    out_lyr = ds.CreateLayer('capital_cities',
                            in_lyr.GetSpatialRef(),
                            ogr.wkbPoint)
    out_lyr.CreateFields(in_lyr.schema)

    # Create a blank feature
    out_defn = out_lyr.GetLayerDefn()
    out_feat = ogr.Feature(out_defn)

    for in_feat in in_lyr:
        if in_feat.GetField('FEATURECLA') == 'Admin-0 capital':

            # Copy geometry and attributes
            geom = in_feat.geometry()
            out_feat.SetGeometry(geom)
            for i in range(in_feat.GetFieldCount()):
                value = in_feat.GetField(i)
                out_feat.SetField(i, value)

            # Insert the feature
            out_lyr.CreateFeature(out_feat)

    # Close files
    del ds
    # ds.SyncToDisk()


if __name__ == "__main__":
    # writeData()
    # readData(fn)
    # printAttributes(fn)
    # showVectorPlot()

    import create_new_layer as cr
    cr.createNewLayer()
    pass