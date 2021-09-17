#from qgis._core import QgsVectorLayer, QgsVectorJoinInfo

import processing

#def rename_dp_field(rlayer, oldname, newname):
#  findex = rlayer.dataProvider().fieldNameIndex(oldname)
#  if findex != -1:
#    rlayer.dataProvider().renameAttributes({findex: newname})
#    rlayer.updateFields()

#csv_fn = '/Users/ronya/My_Documents/karelia/karelia_results/Dissolved.shp'
#shp_fn = '/Users/ronya/My_Documents/karelia/karelia_results/intersection.shp'
#out_fn = '/Users/ronya/My_Documents/karelia/karelia_results/join_test.shp'

csv_fn = '/Users/ronya/My_Documents/Darhan/controls/Dissolved.shp'
shp_fn = '/Users/ronya/My_Documents/Darhan/controls/intersection.shp'
out_fn = '/Users/ronya/My_Documents/Darhan/controls/Joins.shp'

csv =  QgsVectorLayer(csv_fn, 'Dissolved', 'ogr')
shp =  QgsVectorLayer(shp_fn, 'intersection', 'ogr')

#QgsMapLayerRegistry.instance().addMapLayer(csv)
#QgsMapLayerRegistry.instance().addMapLayer(shp)

#shpField='flight1' #intersection
#csvField='FLIGHT_NUM' #dissolved
#joinObject = QgsVectorLayerJoinInfo()
#joinObject.joinLayerId = csv.id()
#joinObject.joinFieldName = csvField
#joinObject.targetFieldName = shpField
#joinObject.memoryCache = True
##joinObject.setJoinLayer(csv)
#shp.addJoin(joinObject)
#shp.reload()
#
#parameters = {  'INPUT': shp, 
#                'INPUT_2': csv, 
#                'FIELD': shpField,
#                'FIELD_2': csvField,
#                'OUTPUT': out_fn
#                }
#
#result = processing.runAndLoadResults('qgis:joinattributestable', parameters)
#result = processing.runandload('qgis:joinattributestable', shp, csv, shpField, csvField, None)
#QgsProject.instance().addMapLayer(result)

shpField='flight1' #intersection
csvField='FLIGHT_NUM' #dissolved
joinObject = QgsVectorLayerJoinInfo()
joinObject.setJoinFieldName(csvField)
joinObject.setTargetFieldName(shpField)
joinObject.setJoinLayerId(csv.id())
joinObject.setUsingMemoryCache(True)
joinObject.setJoinLayer(csv)
shp.addJoin(joinObject)
#shp.reload()

parameters = {  'INPUT': shp, 
                'INPUT_2': csv, 
                'FIELD': shpField,
                'FIELD_2': csvField,
                'OUTPUT': out_fn
                }
#
#result = processing.runAndLoadResults('qgis:joinattributestable', parameters)

res = processing.run("qgis:joinattributestable", parameters)
#iface.addVectorLayer(out_fn, '', 'ogr')
#res = processing.run("qgis:joinattributestable", shp_fn, csv_fn, shpField, csvField, out_fn)
#layer = QgsVectorLayer(res['OUTPUT_LAYER'], "joined_layer", "ogr")
#QgsMapLayerRegistry.instance().addMapLayer(layer)

joinLyr = QgsVectorLayer(out_fn, 'Joins', 'ogr')
# remove useless out_fields
disFields = csv.fields().names()
interFields = shp.fields().names()
joinFields =  joinLyr.fields().names()

#print(disFields)
#print(interFields)
#print(joinFields)

start = len(interFields)-len(disFields)+1
i = start
j = 0
indexesToRemove = []
while i < len(joinFields):
    
    if i < start+len(disFields)-1:
        # rename out_fields
#        rename_dp_field(joinLyr, joinFields[i], disFields[j])
#        print(joinFields[i])
        with edit(joinLyr):
            idx = joinLyr.fields().indexFromName(joinFields[i])
            joinLyr.renameAttribute(idx, (disFields[j]))
            print(disFields[j])
            j += 1
    else:
        # remove out_fields
        indexesToRemove.append(i)
    i += 1

#print(indexesToRemove)
#print(joinFields[len(interFields):])

caps = joinLyr.dataProvider().capabilities()
if caps & QgsVectorDataProvider.DeleteAttributes:
    res = joinLyr.dataProvider().deleteAttributes(indexesToRemove)

iface.addVectorLayer(out_fn, '', 'ogr')
    
    
    
    