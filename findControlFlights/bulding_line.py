#line_fn = '/Users/ronya/My_Documents/karelia/karelia_results/line.shp'
#start_point = QgsPoint(x=-4.74, y=0)
#end_point = QgsPoint(x=2126, y=0)        
#v_layer = QgsVectorLayer("LineString", "line", "memory")
#pr = v_layer.dataProvider()
#seg = QgsFeature()
#seg.setGeometry(QgsGeometry.fromPolyline([start_point, end_point]))
#pr.addFeatures( [ seg ] )
#v_layer.updateExtents()
#crs = v_layer.crs()
#crs.createFromId(28406)
#v_layer.setCrs(crs)
#QgsProject.instance().addMapLayers([v_layer])

#put x and y coordinates to the attribute table
#data_fn = '/Users/ronya/My_Documents/karelia/karelia_results/the_one_control_lines_2.shp'
data_fn = '/Users/ronya/My_Documents/Darhan/controls/control_277_rotated.shp'

layer = QgsVectorLayer(data_fn, '', 'ogr')
pv = layer.dataProvider()
pv.addAttributes([QgsField('X', QVariant.Double)])
pv.addAttributes([QgsField('Y', QVariant.Double)])
layer.updateFields()

with edit(layer):
    for f in layer.getFeatures():
        f['X'] = f.geometry().asPoint()[0]
        f['Y'] = f.geometry().asPoint()[1]
        layer.updateFeature(f)

iface.addVectorLayer(data_fn, '', 'ogr')