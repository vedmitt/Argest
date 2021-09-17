import processing

#infn = '/Users/ronya/My_Documents/karelia/karelia_results/Buffered.shp'
#outfn = '/Users/ronya/My_Documents/karelia/karelia_results/Dissolved.shp'

infn = '/Users/ronya/My_Documents/Darhan/controls/Buffered.shp'
outfn = '/Users/ronya/My_Documents/Darhan/controls/Dissolved.shp'

processing.run("native:dissolve", {'INPUT':infn, 'FIELD':['FLIGHT_NUM'], 'OUTPUT':outfn})

#create new area field
layer = QgsVectorLayer(outfn, '', 'ogr')
pv = layer.dataProvider()
pv.addAttributes([QgsField('area', QVariant.Double)])

layer.updateFields()

expression = QgsExpression('$area')

context = QgsExpressionContext()
context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))

with edit(layer):
    for f in layer.getFeatures():
        context.setFeature(f)
        f['area'] = expression.evaluate(context)
        layer.updateFeature(f)

iface.addVectorLayer(outfn, '', 'ogr')