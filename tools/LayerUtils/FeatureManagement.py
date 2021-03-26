import math

from osgeo import ogr


class FeatureManagement:
    def __init__(self, outDS, templayer, guiUtil):
        self.outDS = outDS
        self.templayer = templayer
        self.guiUtil = guiUtil

    def removeZeroPointsFromMemory(self, boolChecked):
        # далее работаем с временным слоем
        # -------- удаляем нулевые точки ---------------
        if boolChecked:
            self.guiUtil.setOutputStyle('black', 'normal', '\nНачинаем удаление нулевых точек...')
            for i in range(self.templayer.GetFeatureCount()):
                feat = self.templayer.GetNextFeature()
                if feat is not None:
                    geom = feat.geometry()
                    if geom.GetX() == 0.0 and geom.GetY() == 0.0:
                        self.delFeatByID(feat.GetFID())
            self.templayer.ResetReading()

            self.guiUtil.setOutputStyle('green', 'bold', 'Нулевые точки успешно удалены!')
            self.guiUtil.setOutputStyle('black', 'normal', 'Количество точек после удаления нулевых: ' +
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
        if feature.GetField(fieldName) is None:
            feature.SetField(fieldName, value)
            self.templayer.SetFeature(feature)

    def isTargetAzimuth(self, azimuth, targetAzimuth, accuracy):
        if azimuth > 180:
            azimuth = azimuth - 180
        if math.fabs(targetAzimuth - azimuth) <= accuracy:
            return True
        else:
            return False