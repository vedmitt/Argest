from qgis._core import QgsFeature, QgsWkbTypes

from PyQt5.QtCore import QDateTime, Qt

from .FileManager import FileManager


class Feature:

    def __init__(self, fields, vfeature):  # [out_fields: list], [features: QgsFeature]
        self.feature = {}

        if isinstance(vfeature, QgsFeature):
            self.feature.setdefault('id', vfeature.id())
            geom = vfeature.geometry()
            self.geometry, typeOfGeom = FileManager().getFeatureGeometry(geom)
            # self.geometry = vfeature.geometry().asPoint()

        i = 0
        for field in fields:
            if isinstance(vfeature[i], QDateTime):
                vfeature[i] = vfeature[i].currentDateTime().toString(Qt.ISODate)

            self.feature.setdefault(field, vfeature[i])
            i += 1

    def id(self):
        return self.getValue('id')

    def addNewVal(self, name, val):
        self.feature.setdefault(name, val)

    def removeValue(self, name):
        self.feature.pop(name)

    def setValue(self, name, val):
        if name in self.feature.keys():
            self.feature[name] = val
        else:
            self.feature.setdefault(name, val)

    def getValue(self, name):
        return self.feature.get(name)

    def getAllFields(self):
        return list(self.feature.keys())

    def getAllValues(self):
        return list(self.feature.values())

    def getGeometry(self):
        return self.geometry

    def setGeometry(self, geom):
        self.geometry = geom


