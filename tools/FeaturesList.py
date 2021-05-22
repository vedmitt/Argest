from PyQt5.QtCore import QVariant

from .LogFileTool import LogFileTool
from .Feature import Feature


class FeaturesList:
    typex = {'Integer64': QVariant.Int, 'Real': QVariant.Double, 'String': QVariant.String,
             'integer': QVariant.Int, 'double': QVariant.Double, 'text': QVariant.String}

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
        # LogFileTool().writeToFile(lines)
        self.feat_list = new_list

    def removeSpoiledPoints(self):
        new_list = []
        for feat in self.feat_list:
            if feat.getValue('CLASS') == 3 or feat.getValue('CLASS') == 4:
                new_list.append(feat)
        self.feat_list = new_list
