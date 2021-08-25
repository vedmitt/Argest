# -*- coding: utf-8 -*-
import os

from PyQt5.QtGui import QIcon
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtGui import *

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer

from time import perf_counter

from .tools.CalcRMSETool import CalcRMSETool
from .tools.ControlsExtactTool import ControlsExtractTool
from .tools.dataStorage.FileManager import FileManager
from .tools.GuiElemIFace import GuiElemIFace

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'control_flights_plugin.ui'))


class control_flights_Dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(control_flights_Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.setInputData()

        self.cp_reload.setIcon(QIcon(':/plugins/bpla_plugin_flights/icons/icon_reload.png'))
        self.cp_reload.clicked.connect(self.setInputData)

        self.rm_reload_1.setIcon(QIcon(':/plugins/bpla_plugin_flights/icons/icon_reload.png'))
        self.rm_reload_1.clicked.connect(self.setInputData)

        self.rm_reload_2.setIcon(QIcon(':/plugins/bpla_plugin_flights/icons/icon_reload.png'))
        # self.rm_reload_2.clicked.connect(self.setInputComboBox)

        # self.cp_output.setText(r'/Users/ronya/My_Documents/output')
        # self.cp_output.setText(r'/Users/ronya/My_Documents/Darhan/controls')
        self.cp_outputBut.clicked.connect(self.setSavefileLine)

        # self.rm_output.setText(r'/Users/ronya/My_Documents/Darhan/controls/plots')
        self.rm_outputBut.clicked.connect(self.setSavefileLine)

        self.cp_resBut.clicked.connect(self.findControlFlights)
        # self.rm_resBut.clicked.connect(self.calcRMSE)
        self.rm_resBut.clicked.connect(self.doCalcRMSE_main)

    def setInputData(self):
        # self.le_saveFile = QLineEdit()
        # self.button = QToolButton()
        # self.horizontalLayout_5.addWidget(self.le_saveFile)
        # self.horizontalLayout_5.addWidget(self.button)
        # self.button.clicked.connect(self.setSavefileLine)

        guiUtil = GuiElemIFace()
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.adjustSize()
        # if self.tabWidget.currentIndex() == 0:
        guiUtil.setComboBoxWithLayers(self.cp_input)
        # else:
        # guiUtil.setComboBoxWithLayers(self.rm_input_1)
        entries = FileManager().getActiveLayersFromCanvas().keys()
        guiUtil.setListWidgetWithData(self.rm_lw_input, entries)
        # guiUtil.setComboBoxWithLayers(self.rm_input_2, self.rm_input_2.currentText())

    def setSavefileLine(self):
        if self.tabWidget.currentIndex() == 0:
            self.cp_output.setText(QtWidgets.QFileDialog(self).getExistingDirectory(self, r'/Users/ronya/My_Documents'))
        else:
            self.rm_output.setText(QtWidgets.QFileDialog(self).getExistingDirectory(self, r'/Users/ronya/My_Documents'))

    def findControlFlights(self):
        start = perf_counter()
        self.textEdit.setText('')
        guiUtil = GuiElemIFace(self.textEdit)
        ControlsExtractTool(guiUtil, self.cp_selectControls.isChecked(), self.cp_input.currentText(),
                            self.cp_output.text()).main_controlFlightsExtract()

        # self.textEdit.setHtml(QCoreApplication.translate("Dialog", u"<!DOCTYPE html><html><body><h1>My First Heading</h1><p>My first paragraph.</p></body></html>", None))
        # html_fpath = 'control_flights_extraction.html'
        # # htmlFile = open(html_fpath, 'r')
        # self.textEdit.setHtml(QCoreApplication.translate("Dialog", html_fpath, None))
        end = perf_counter()
        guiUtil.setOutputStyle([0, '\nВремя работы плагина: ' + str(end - start)])

    def doCalcRMSE_main(self):
        self.textEdit.setText('')
        start = perf_counter()
        guiUtil = GuiElemIFace(self.textEdit)
        CalcRMSETool(guiUtil).main_calcRMSE(self.rm_lw_input.selectedItems(), self.rm_output.text())
        end = perf_counter()
        guiUtil.setOutputStyle([0, '\nВремя работы плагина: ' + str(end - start)])
