class Feature:

    def __init__(self, fields_list, values, geom):
        self.content = {}
        self.geometry = geom
        i = 0
        for field in fields_list:
            if str(type(values[i])) == "<class 'PyQt5.QtCore.QDateTime'>":
                values[i] = values[i].currentDateTime().toString(Qt.ISODate)
            self.content.setdefault(field, values[i])
            i += 1

    def addNewVal(self, name, val):
        self.content.setdefault(name, val)

    def setValue(self, name, val):
        if name in self.content.keys():
            self.content[name] = val
        else:
            self.content.setdefault(name, val)

    def getValue(self, name):
        return self.content.get(name)

    def getAllFields(self):
        return list(self.content.keys())

    # def getFieldType(self, field_name):
    #     return self.out_fields.get(field_name)

    def getAllValues(self):
        return list(self.content.values())

    def getGeometry(self):
        return self.geometry

    def setGeometry(self, geom):
        self.geometry = geom

class FeaturesList:
    typex = {'Integer64': QVariant.Int, 'Real': QVariant.Double, 'String': QVariant.String,
             'integer': QVariant.Int, 'double': QVariant.Double, 'text': QVariant.String, 'datetime': QVariant.String}

    def __init__(self, vfields_dict, vfeatures):
        self.fields_types_dict = {}
        self.feat_list = []
        if vfeatures is not None:
            self.fields_types_dict = self.getFieldsTypes(vfields_dict)
            for item in vfeatures:
                f = Feature(list(self.fields_types_dict.keys()), item, item.geometry().asPoint())
                self.feat_list.append(f)

    def sortListByLambda(self, fieldName):
        self.feat_list = sorted(self.feat_list, key=lambda feature: feature.getValue(fieldName), reverse=False)

    def getFieldsTypes(self, vfields):
        fields = {}
        for field in vfields:
            fields.setdefault(field.name(), FeaturesList.typex[field.typeName()])
        return fields

    def getFieldDict(self):
        return self.fields_types_dict

    def getFieldList(self):
        return list(self.fields_types_dict.keys())

    def getFeaturesList(self):
        return self.feat_list

    def getFeature(self, i):
        return self.feat_list[i]

    def addNewField(self, name, type):
        self.fields_types_dict.setdefault(name, FeaturesList.typex[type])

    def setFeature(self, i, name, val):
        self.feat_list[i].setValue(name, val)

    def getFeatureCount(self):
        return len(self.feat_list)

    def addFeature(self, feature):
        self.feat_list.append(feature)

    def setFields(self, fields_dict):
        self.fields_types_dict = fields_dict

    def getOrderedValList(self, i):
        list_val = []
        for field in self.fields_types_dict.keys():
            list_val.append(self.feat_list[i].getValue(field))
        return list_val

    def removeFeature(self, i):
        self.feat_list.pop(i)

    def removeNullPoints(self):
        # lines = [str(len(self.feat_list))]
        new_list = []
        for feat in self.feat_list:
            coordinates = feat.getGeometry()
            # coordinates = [feat.getValue("LON"), feat.getValue("LAT")]
            # lines.append(str(coordinates[0]) + " : " + str(coordinates[1]))

            if coordinates[0] > 0.0 and coordinates[1] > 0.0:
                new_list.append(feat)
        # lines.append(str(len(self.feat_list)))
        # FileWriterUtil().writeToFile(lines)
        self.feat_list = new_list

    def removeSpoiledPoints(self):
        new_list = []
        for feat in self.feat_list:
            if feat.getValue('CLASS') == 3 or feat.getValue('CLASS') == 4:
                new_list.append(feat)
        self.feat_list = new_list
        
def saveToShapefile(driverName, fileEncoding, file_attr, features):
    newfields = QgsFields()
    fields = features.getFields()
    for field in fields:
        newfields.append(QgsField(field, fields[field]))

    crs = QgsProject.instance().crs()
    transform_context = QgsProject.instance().transformContext()
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = driverName
    save_options.fileEncoding = fileEncoding

    writer = QgsVectorFileWriter.create(
        file_attr[0],
        newfields,
        QgsWkbTypes.Point,
        crs,
        transform_context,
        save_options
    )

    # add features
    feat_list = features.getFeatures()
    for i in range(len(feat_list)):
        f = QgsFeature()
        coordinates = feat_list[i].getGeometry()
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(QgsPointXY(coordinates))))
        f.setAttributes(features.getOrderedValList(i))

        writer.addFeature(f)
        i += 1

    # delete the writer to flush features to disk
    del writer

    mess = iface.addVectorLayer(file_attr[0], file_attr[1], 'ogr')
    return mess
#----------------------------------------------
import math
def calcRMSE(features, Tr_field, Tk_field):
    summa = 0
    i = 0
    for f in features.getFeatures():
        summa = summa + (f.getValue(Tk_field) - f.getValue(Tr_field)) ** 2
        print('Tk= ', f.getValue(Tk_field)) 
        print('Tr= ', f.getValue(Tr_field))
        i += 1
        
        if i == 10:
            break
            
    res = math.sqrt(summa / (features.featureCount()) - 1)
    return res

def interpolation_func(T1, T2, x, x1, x2):
    if T1 == NULL or T2 == NULL or (x2-x1) == 0:
        return 0
    else:
        Tx = T1 + (x - x1) * ((T2 - T1) / (x2 - x1))
        return Tx
    
def interpolation_loop(features, profile_num, t_field, field_out):
    featsCount = features.featureCount()
    i = 0
    shang = -1
    xia = 1
    while i < featsCount:
        if features.getFeature(i).getValue('FLIGHT_NUM') == profile_num:
            if i-1 < 0: #The fn1 point
                shang = 1
                xia = 3
            elif i >= featsCount-1:
                shang = -1
                xia = -3
            else:
                shang = -1
                xia = 1
            
            T1 = features.getFeature(i+shang).getValue(t_field)
            x1 = features.getFeature(i+shang).getValue('X')
#            print('y_actual = ', y_actual)
            
            T2 = features.getFeature(i+xia).getValue(t_field)
            x2 = features.getFeature(i+xia).getValue('X')
#            print('y_predicted = ', y_predicted)
            
            x = features.getFeature(i).getValue('X')
            Tx = interpolation_func(T1, T2, x, x1, x2)
            features.setFeature(i, field_out, Tx)
#            print(i, features.getFeature(i+shang).getValue('FLIGHT_NUM'), features.getFeature(i+xia).getValue('FLIGHT_NUM'), features.getFeature(i).getValue(out_fields))
#            print('Tx = ', Tx)
#        else:
#            features.setFeature(i, out_fields, features.getFeature(i).getValue(t_field))
            
        i += 1
    
    return features

#data_fn = '/Users/ronya/My_Documents/karelia/karelia_results/the_one_control_lines_2.shp'
#out_fn = '/Users/ronya/My_Documents/karelia/karelia_results/test_data_1.shp'

data_fn = '/Users/ronya/My_Documents/Darhan/controls/control_277_rotated.shp'
out_fn = '/Users/ronya/My_Documents/Darhan/controls/control_277_result.shp'
layer = QgsVectorLayer(data_fn, '', 'ogr')

##create new column T_x
#pv = layer.dataProvider()
#pv.addAttributes([QgsField('T_r', QVariant.Double)])
#pv.addAttributes([QgsField('T_k', QVariant.Double)])
#layer.updateFields()

 # find profile numbers
#controls = [114, 116]
#expression = 'FLIGHT_NUM'
#request = QgsFeatureRequest().setFilterExpression(expression)
#for f in layer.getFeatures(request):
# controls.append(f[expression])
#controls = set(controls)
#print(controls)

# order by X and calculate new vfeature T
features = FeaturesList(layer.fields(), layer.getFeatures())
features.sortListByLambda('X')

#for f in layer.out_fields():
#    print(f.name())

features = interpolation_loop(features, 66, 'T', 'T_r')
features = interpolation_loop(features, 277, 'T_r', 'T_k')  # control
#RMSE = calcRMSE(features, 'T_r', 'T_k')
#print(RMSE)

mess = saveToShapefile("ESRI Shapefile", "UTF-8", [out_fn, 'control_277_result'], features)

#with edit(layer):
#    for f in layer.getFeatures():
#        f['X'] = f.geometry().asPoint()[0]
#        layer.updateFeature(f)
#iface.addVectorLayer(data_fn, '', 'ogr')