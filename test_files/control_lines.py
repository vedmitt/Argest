def rotateTransform(x, y, deg_ccw):
    angle = math.radians(-deg_ccw)

    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)

    new_w = cos_theta * x - sin_theta * y
    new_h = sin_theta * x + cos_theta * y

    return new_w, new_h

def affineCoordinate(feat_list, targetAzimuth):
    new_coordinates = []
    angle = 90 - targetAzimuth
    Ox = feat_list[0].geometry().asPoint()[0]
    Oy = feat_list[0].geometry().asPoint()[1]
    for feat in feat_list:
        fg = feat.geometry()
        dx = fg.asPoint()[0] - Ox
        dy = fg.asPoint()[1] - Oy
        new_x, new_y = rotateTransform(dx, dy, angle)
        new_coordinates.append([new_x, new_y])
    return new_coordinates


def main_func():
    infn = '/Users/ronya/My_Documents/karelia/karelia_results/the_one_control_lines_1.shp'
    outfn = '/Users/ronya/My_Documents/karelia/karelia_results/the_one_control_lines_2.shp'
    layer = QgsVectorLayer(infn, '', 'ogr')
    
    feat_list = []
    features = layer.getFeatures()
    for f in features:
        feat_list.append(f)
    
    new_coordinates = affineCoordinate(feat_list, 64)
    
#    print(len(feat_list))
#    print(len(new_coordinates))
    
    #save file with new geometry
    fields = layer.fields()

    writer = QgsVectorFileWriter(outfn, 'UTF-8', fields, QgsWkbTypes.Point, layer.sourceCrs(), 'ESRI Shapefile')
    
    i = 0
    for feat in feat_list:
        geom = QgsGeometry.fromWkt('POINT (' + str(new_coordinates[i][0]) + ' ' + str(new_coordinates[i][1])+')')
#        print(vgeom)
        feat.setGeometry(geom)
        writer.addFeature(feat)
        i += 1
        
    iface.addVectorLayer(outfn, '', 'ogr')
    del(writer)
        

main_func()