#data = '/Users/ronya/My_Documents/input_data/karelia_2.shp'
#infn = '/Users/ronya/My_Documents/karelia/karelia_results/control_flights_finish.shp'
#outfn = '/Users/ronya/My_Documents/karelia/karelia_results/result_test.shp'

infn = '/Users/ronya/My_Documents/Darhan/controls/control_flights_scheme.shp'
outfn = '/Users/ronya/My_Documents/Darhan/controls/control_flights_all.shp'

layers = QgsProject.instance().mapLayersByName('Darhan_GK20_metric1')
layer_1 = layers[0]
layer_2 = QgsVectorLayer(infn, 'control_flights_scheme', 'ogr')

controls = []

expression = 'FLIGHT_NUM'
request = QgsFeatureRequest().setFilterExpression(expression)

for f in layer_2.getFeatures(request):
    controls.append(f[expression])
    
print(controls)

feats = layer_1.getFeatures()
res = []

for feat in feats:
    if feat[expression] in controls:
        res.append(feat)
        
#print(res)

#create new layer with controls
fields = layer_1.fields()

writer = QgsVectorFileWriter(outfn, 'UTF-8', fields, QgsWkbTypes.Point, layer_1.sourceCrs(), 'ESRI Shapefile')

for feat in res:
    geom = feat.geometry()
    feat.setGeometry(geom)
    writer.addFeature(feat)
    
iface.addVectorLayer(outfn, '', 'ogr')
del(writer)



