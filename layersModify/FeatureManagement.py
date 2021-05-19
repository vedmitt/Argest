import math

from osgeo import ogr


class FeatureManagement:
    def __init__(self, outDS, templayer, guiUtil):
        self.outDS = outDS
        self.templayer = templayer
        self.guiUtil = guiUtil

    def removeZeroPointsFromMemory(self):
        # далее работаем с временным слоем
        # -------- удаляем нулевые точки ---------------
        self.guiUtil.setOutputStyle(0, '\nНачинаем удаление нулевых точек...')
        for i in range(self.templayer.GetFeatureCount()):
            feat = self.templayer.GetNextFeature()
            if feat is not None:
                geom = feat.geometry()
                if geom.GetX() == 0.0 and geom.GetY() == 0.0:
                    self.delFeatByID(feat.GetFID())
        self.templayer.ResetReading()

        self.guiUtil.setOutputStyle(0, 'Нулевые точки успешно удалены!')
        self.guiUtil.setOutputStyle(0, 'Количество точек после удаления нулевых: ' +
                                    str(self.templayer.GetFeatureCount()))
        self.outDS.SyncToDisk()

    def delFeatByID(self, ID):
        self.templayer.DeleteFeature(ID)
        self.outDS.ExecuteSQL('REPACK ' + self.templayer.GetName())

    ##------------------------------------------------------------------

    def tempLayerToListFeat(self, templayer):
        feat_list = []
        for i in range(templayer.GetFeatureCount()):
            feat = templayer.GetNextFeature()
            feat_list.append(feat)
        templayer.ResetReading()
        return feat_list

    def sortListByLambda(self, mylist, fieldName):
        mylist = sorted(mylist, key=lambda feature: feature.GetField(fieldName), reverse=False)
        return mylist

    def createNewField(self, fieldName, fieldType):
        fieldDefn = ogr.FieldDefn(fieldName, fieldType)
        if fieldType == ogr.OFTString:
            fieldDefn.SetWidth(30)
        self.templayer.CreateField(fieldDefn)

    def setFieldValue(self, feature, fieldName, value):
        feature.SetField(fieldName, value)
        self.templayer.SetFeature(feature)

    def getFieldValue(self, feature, fieldName):
        if feature.GetField(fieldName) is not None:
            return feature.GetField(fieldName)

    def getAllFieldValuesAsList(self, templayer, fieldName):
        values = []
        for i in range(templayer.GetFeatureCount()):
            feat = templayer.GetNextFeature()
            val = self.getFieldValue(feat, fieldName)
            values.append(val)
        templayer.ResetReading()
        return values

    def isTargetAzimuth(self, azimuth, targetAzimuth, accuracy):
        if azimuth > 180:
            azimuth = azimuth - 180
        if math.fabs(targetAzimuth - azimuth) <= accuracy:
            return True
        else:
            return False
