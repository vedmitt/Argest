from qgis.core import QgsVectorLayer, QgsProject

#outFn = '/Users/ronya/My_Documents/karelia/karelia_results/intersection.shp'
outFn = '/Users/ronya/My_Documents/Darhan/controls/intersection.shp'

vlayer = QgsVectorLayer( "?query=SELECT st_intersection(a.geometry, b.geometry) as geometry, a.FLIGHT_NUM as flight1, b.FLIGHT_NUM as flight2, a.GLOBAL_NUM as glob1, b.GLOBAL_NUM as glob2, a.TIME as time1, b.TIME as time2 \
FROM Dissolved a JOIN Dissolved b ON ( \
	(a.global_num < b.global_num)and \
	(a.geometry is NOT NULL)and \
	(b.geometry is NOT NULL)and \
	(st_intersects(a.geometry, b.geometry)) \
)  \
", "intersection", "virtual" )

#QgsProject.instance().addMapLayer(vlayer)

#writer = QgsVectorFileWriter.writeAsVectorFormat(vlayer, outFn, 'utf-8', driverName='ESRI Shapefile')

fields = vlayer.fields()
feats = vlayer.getFeatures()
writer = QgsVectorFileWriter(outFn, 'UTF-8', fields, QgsWkbTypes.Polygon, vlayer.sourceCrs(), 'ESRI Shapefile')

for feat in feats:
    geom = feat.geometry()
    feat.setGeometry(geom)
    writer.addFeature(feat)
    
del(writer)
    
#create new area field
layer = QgsVectorLayer(outFn, '', 'ogr')
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
    
iface.addVectorLayer(outFn, '', 'ogr')