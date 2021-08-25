import math

from PyQt5.QtCore import QVariant

from .Feature import Feature


class FeaturesList:

    TYPEX = {'Integer64': QVariant.Int, 'Real': QVariant.Double, 'String': QVariant.String,
             'integer': QVariant.Int, 'double': QVariant.Double, 'text': QVariant.String, 'datetime': QVariant.String
             }

    def __init__(self, fields, field_types, vfeatures, metadata=None):
        self.metadata = metadata  # { metadata }
        self.fields = fields
        self.field_types = field_types  # self.convertFieldTypes(field_types)  # тип поля
        self.feat_list = []  # список объектов Feature

        if vfeatures is not None:
            for vfeature in vfeatures:
                f = Feature(self.fields, vfeature)  # создаем объекты Features
                self.feat_list.append(f)

    def convertFieldType(self, vtype):
        return FeaturesList.TYPEX.get(vtype)

    def getFields(self):
        return self.fields

    def getFieldTypes(self):
        return self.field_types

    def getFieldDict(self):
        fields_types = {}
        k = 0
        for field in self.fields:
            if isinstance(self.field_types[k], str):
                fields_types.setdefault(field, self.convertFieldType(self.field_types[k]))
            else:
                fields_types.setdefault(field, self.field_types[k])
            k += 1
        return fields_types

    def addNewField(self, name, type=None):
        self.fields.append(name)
        if type is not None:
            self.field_types.append(self.convertFieldType(type))

    def removeField(self, name):
        if self.field_types is not None:
            i = self.fields.index(name)
            self.field_types.pop(i)
        self.fields.remove(name)

    def setNewFieldsOrder(self, fields, types):
        self.fields = fields
        self.field_types = types

    def getMetadata(self):
        return self.metadata

    def getMetadataValueByName(self, name):
        return self.metadata.get(name)

    def id(self, i):
        return self.getFeature(i).id()

    def sortByField(self, fieldName):
        self.feat_list = sorted(self.feat_list, key=lambda feature: feature.getValue(fieldName), reverse=False)

    def getFeatures(self):
        return self.feat_list

    def featureCount(self):
        return len(self.feat_list)

    def getFeature(self, i):
        return self.feat_list[i]

    def getFeatureValue(self, i, name):
        return self.getFeature(i).getValue(name)

    def setFeature(self, i, name, val):
        self.feat_list[i].setValue(name, val)

    def addFeature(self, feature):
        self.feat_list.append(feature)

    def getOrderedValList(self, i):
        values_list = []
        for field in self.fields:
            values_list.append(self.feat_list[i].getValue(field))
        return values_list

    def removeFeature(self, i):
        self.feat_list.pop(i)

    def removeValue(self, i, name):
        self.feat_list[i].removeValue(name)

    def setValuesByField(self, name, values, type='float'):  # [values]
        i = 0
        while i < self.featureCount():
            if i < len(values):
                if type is 'float':
                    self.feat_list[i].setValue(name, float(values[i]))
                else:
                    self.feat_list[i].setValue(name, values[i])
            i += 1

    def addNewFeatsToEndOfList(self, features):  # ( list )
        for f in features:
            if isinstance(f, list):
                self.addFeature(Feature(self.getFields(), f))

            if isinstance(f, Feature):
                self.addFeature(f)

    def removeNullPoints(self):
        new_list = []
        for feat in self.feat_list:
            coordinates = feat.getGeometry()

            if coordinates[0] > 0.0 and coordinates[1] > 0.0:
                new_list.append(feat)

        self.feat_list = new_list

    def removeSpoiledPoints(self):
        new_list = []
        for feat in self.feat_list:
            if feat.getValue('CLASS') == 3 or feat.getValue('CLASS') == 4:
                new_list.append(feat)
        self.feat_list = new_list

    def getVectorOfValues(self, field_name):
        return [feat.getValue(field_name) for feat in self.feat_list]

    def getArrayOfValues(self, field_names):
        res = [[feat.getValue(field) for field in field_names] for feat in self.feat_list]
        return res

    def selectValueByCondition(self, fields, condition):  # condition = [Field_name, condition_value]
        res = []
        for feat in self.feat_list:
            if feat.getValue(condition[0]) == condition[1]:
                if len(fields) > 1:
                    res_line = []
                    for field in fields:
                        res_line.append(feat.getValue(field))
                    res.append(res_line)
                else:
                    res.append(feat.getValue(fields[0]))
        return res
