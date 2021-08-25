#infn = '/Users/ronya/My_Documents/karelia/karelia_results/join_test.shp'
#outfn = '/Users/ronya/My_Documents/karelia/karelia_results/control_flights.shp'
#outfn2 = '/Users/ronya/My_Documents/karelia/karelia_results/control_flights_scheme.shp'

infn = '/Users/ronya/My_Documents/Darhan/controls/Joins.shp'
outfn = '/Users/ronya/My_Documents/Darhan/controls/control_flights.shp'
outfn2 = '/Users/ronya/My_Documents/Darhan/controls/control_flights_scheme.shp'

##create new area field with an expression
#in_layer = QgsVectorLayer(infn, '', 'ogr')
#writer = QgsVectorFileWriter.writeAsVectorFormat(in_layer, outfn, 'utf-8', driverName='ESRI Shapefile')
#
#layer = QgsVectorLayer(outfn, 'control_flights', 'ogr')
#
#pv = layer.dataProvider()
#pv.addAttributes([QgsField('area_diff', QVariant.Double)])
#layer.updateFields()
#
#expression = QgsExpression('"area" / "Dissolve10"')
#
#context = QgsExpressionContext()
#context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
#
#with edit(layer):
#    for f in layer.getFeatures():
#        context.setFeature(f)
#        f['area_diff'] = expression.evaluate(context)
#        layer.updateFeature(f)
#
#iface.addVectorLayer(outfn, '', 'ogr')
#-------------------------------------------------------

##layer = iface.addVectorLayer(outfn, 'control_flights', 'ogr')        
expression = "if ( area_diff > 0.5, if ( time1 > time2, flight1, flight2), '')"
#
#
##create new area field
#layer = QgsVectorLayer(outfn2, '', 'ogr')
#pv = layer.dataProvider()
#pv.addAttributes([QgsField('FLIGHT_NUM', QVariant.Int)])
#
#layer.updateFields()
#
#expression = QgsExpression(expression)
#
#context = QgsExpressionContext()
#context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
#
#with edit(layer):
#    for f in layer.getFeatures():
#        context.setFeature(f)
#        f['FLIGHT_NUM'] = expression.evaluate(context)
#        layer.updateFeature(f)
#
#iface.addVectorLayer(outfn2, '', 'ogr')


layer.selectAll()
layer.selectByExpression(expression)

fields = layer.fields()
feats = layer.selectedFeatures()
writer = QgsVectorFileWriter(outfn2, 'UTF-8', fields, QgsWkbTypes.Polygon, layer.sourceCrs(), 'ESRI Shapefile')

for feat in feats:
    geom = feat.geometry()
    feat.setGeometry(geom)
    writer.addFeature(feat)
    
del(writer)

iface.addVectorLayer(outfn2, 'control_flights_scheme', 'ogr')
