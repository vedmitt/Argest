csv_fn = '/Users/ronya/My_Documents/karelia/karelia_results/Dissolved.shp'
out_fn = '/Users/ronya/My_Documents/karelia/karelia_results/join_test.shp'

#remove unnecesary out_fields
layer_dis = QgsVectorLayer(csv_fn, '', 'ogr')
layer_out = QgsVectorLayer(out_fn, '', 'ogr')

fields = layer_dis.fields().count()-4
glob_fields = layer_out.fields().count()-1

print(fields)
print(glob_fields)

#pv = layer_out.dataProvider()
#i = 1
#for i in range(out_fields):
#    pv.deleteAttributes([glob_fields-i])
#    i += 1
#layer.updateFields()

iface.addVectorLayer(out_fn, '', 'ogr')