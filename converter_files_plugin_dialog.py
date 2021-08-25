# -*- coding: utf-8 -*-
import os

from PyQt5.QtGui import QIcon
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtGui import *

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer

from time import perf_counter
from .tools.dataStorage.FileManager import FileManager
from .tools.dataStorage.FeaturesList import FeaturesList
from .tools.GuiElemIFace import GuiElemIFace

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'converter_files_plugin.ui'))


class converter_files_plugin_Dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(converter_files_plugin_Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.initComponents()

    def initComponents(self):
        self.loadInputData()
        self.tb_reload_1.setIcon(QIcon(':/plugins/bpla_plugin_flights/icons/icon_reload.png'))
        self.tb_reload_1.clicked.connect(self.loadInputData)

        self.tb_reload_2.setIcon(QIcon(':/plugins/bpla_plugin_flights/icons/icon_reload.png'))
        self.tb_reload_2.clicked.connect(self.loadInputData)

        # self.le_output_1.setText(r'/Users/ronya/My_Documents/output/data_converted_1.txt')
        self.tb_output_1.clicked.connect(self.setSavefileLine)

        # self.le_output_2.setText(r'/Users/ronya/My_Documents/output/data_merged_1.txt')
        self.tb_output_2.clicked.connect(self.setSavefileLine)

        self.pushButton_res_1.clicked.connect(self.convertFiles)
        self.pushButton_res_2.clicked.connect(self.mergeFiles)


    def loadInputData(self):
        lg = FileManager()
        guiUtil = GuiElemIFace()
        if self.tabWidget.currentIndex() == 0:  # tab_1
            guiUtil.setComboBoxWithLayers(self.cb_lyr_1)
        else:  # tab_2
            activeLayers = lg.getActiveLayersFromCanvas()
            guiUtil.setListWidgetWithData(self.listWidget_2, activeLayers.keys(), 'multiselect')

    def setSavefileLine(self):
        if self.tabWidget.currentIndex() == 0:  # tab_1
            rb = [self.rb_txt_1, self.rb_shp_1]
            outFileLine = self.le_output_1
        else:  # tab_2
            rb = [self.rb_txt_2, self.rb_shp_2]
            outFileLine = self.le_output_2

        dlg = QtWidgets.QFileDialog(self)
        filter = '*' + GuiElemIFace().getTextFromRadioButton(rb)
        fn = dlg.getSaveFileName(self, 'Save file', r'/Users/ronya/My_Documents', filter=filter)[0]
        outFileLine.setText(fn)

    def convertFiles(self):
        self.textEdit.setText('')
        start = perf_counter()
        guiUtil = GuiElemIFace(self.textEdit)
        lg = FileManager(guiUtil)

        layerName = self.cb_lyr_1.currentText()

        # создаем вектор qgis
        vlayer = lg.getQgsVectorLayer(layerName)
        features = FeaturesList(vlayer.fields().names(), [f.type() for f in vlayer.fields()], vlayer.getFeatures())

        # # записываем объекты в новый слой
        # extension radioButtons
        whatType = {'txt': self.rb_txt_1.isChecked(),
                    'shp': self.rb_shp_1.isChecked()
                    }
        file_attr = lg.getSaveFileAttr(self.le_output_1)
        lg.createNewFileByExtension(whatType, features, file_attr.getFilePath())

        end = perf_counter()
        guiUtil.setOutputStyle([0, '\nВремя работы плагина: ' + str(end - start)])

    def mergeFiles(self):
        self.textEdit.setText('')
        start = perf_counter()
        guiUtil = GuiElemIFace(self.textEdit)
        lg = FileManager(guiUtil)

        lur = self.listWidget_2.selectedItems()
        layerNames = [i.text() for i in list(lur)]

        # создаем вектор qgis для первого слоя в списке
        vlayer = lg.getQgsVectorLayer(layerNames[0])
        features = FeaturesList(vlayer.fields().names(), [f.type() for f in vlayer.fields()], vlayer.getFeatures())
        i = 1
        while i < len(layerNames):
            vlayer2 = lg.getQgsVectorLayer(layerNames[i])
            features2 = FeaturesList(vlayer2.fields().names(), [f.type() for f in vlayer2.fields()], vlayer2.getFeatures())
            features.addNewFeatsToEndOfList(features2.getFeatures())
            i += 1

        # # записываем объекты в новый слой
        # extension radioButtons
        whatType = {'txt': self.rb_txt_2.isChecked(),
                    'shp': self.rb_shp_2.isChecked()
                    }
        file_attr = lg.getSaveFileAttr(self.le_output_2)
        lg.createNewFileByExtension(whatType, features, file_attr.getFilePath())

        end = perf_counter()
        guiUtil.setOutputStyle([0, '\nВремя работы плагина: ' + str(end - start)])
