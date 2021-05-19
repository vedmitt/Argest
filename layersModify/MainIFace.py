from tools.ClassificationTool import ClassificationTool
from .FeatureManagement import FeatureManagement
from .LayerManagement import LayerManagement


class MainIFace:

    def __init__(self, guiUtil):
        # self.guiUtil = GuiElemIFace(textEdit)
        self.guiUtil = guiUtil
        self.outDS = None
        self.inDS = None
        self.temLyr = None
        self.memDriver = None

    def exceptionsDecorator(self, function_to_decorate, errStr):
        def the_wrapper_around_the_original_function():
            try:
                function_to_decorate()  # Сама функция
            except Exception as err:
                self.guiUtil.setOutputStyle(0, errStr + str(err))

        return the_wrapper_around_the_original_function

    def createTempLayer(self, lg):
        # get layer from combobox
        # lg = LayerGetter()
        # lg.getLayer(curLayer)

        self.guiUtil.setOutputStyle(0, 'Создаем новый слой...')

        ft = LayerManagement(self.guiUtil)
        if lg.driverName == "Delimited text file":
            ft.csvToMemory(lg.layerpath, lg.csvFileAttrs)
        elif lg.driverName == "ESRI Shapefile":
            self.outDS, self.temLyr = ft.layerToMemory(lg.driverName, lg.layerpath)
            # return tlyr
        return None

    def removeZeroPoints(self):
        # далее работаем с временным слоем
        if self.temLyr is not None:
            self.guiUtil.setOutputStyle(0, 'Количество точек во временном слое: ' + str(
                self.temLyr.GetFeatureCount()))

            FeatureManagement(self.outDS, self.temLyr, self.guiUtil).removeZeroPointsFromMemory()

    # def saveToFile(self, feat_list, filename, filepath):
    #     if filepath is not None:
    #         ClassificationTool(self.guiUtil).saveFeatListToFile(feat_list, filename, filepath)
    #     else:
    #         self.guiUtil.setOutputStyle('red', 'bold', 'Введите данные в форму!\n')

    def mainAzimutCalc(self, filename, filepath, checkBox_delete, checkBox_numProfiles):
        ClassificationTool(self.outDS, self.temLyr, self.guiUtil, filename, filepath).mainAzimutCalc(checkBox_delete,
                                                                                                     checkBox_numProfiles, )
        # ClassificationTool_2(self.outDS, self.temLyr, self.guiUtil).mainAzimutCalc()

    # def numbersForFlights(self, vlayerstr):
    #     # try:
    #     lg = LayerGetter()
    #     lg.getLayer(vlayerstr)
    #     if lg.driverName == "ESRI Shapefile":
    #         LayerManagement(self.guiUtil).layerToMemory(lg.driverName, lg.layerpath)
    #
    #         NumCalcUtil(self.guiUtil).setFlightNumber(self.outDS, self.temLyr)
    #
    #         fileName = 'test_' + str(randint(0000, 9999))
    #         filePath = "M:/Sourcetree/output/" + fileName + ".shp"
    #         self.saveToFile(fileName, filePath)
    #     # except Exception as err:
    #     #     self.guiUtil.setOutputStyle('red', 'bold', '\nНе удалось пронумеровать полеты! ' + str(err))

