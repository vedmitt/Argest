# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bpla_plugin_flightsDialog
                                 A QGIS plugin
 Selecting and deleting odds and ends of flights.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-01-13
        git sha              : $Format:%H$
        copyright            : (C) 2021 by SibGis
        email                : sibgis@qgis.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os

from PyQt5.QtGui import QIcon
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtGui import *

from time import perf_counter

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
from qgis.utils import iface

from .tools.LayerUtils.ClassificationTool_1 import ClassificationTool_1
from .tools.LayerUtils.MainIFace import MainIFace
from .tools.LayerUtils.LayerGetter import LayerGetter
from .tools.LayerUtils.GuiElemIFace import GuiElemIFace

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bpla_plugin_flights_dialog_base.ui'))


class bpla_plugin_flightsDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(bpla_plugin_flightsDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.initActiveLayersComboBox()
        self.toolButton_cbreload.setIcon(QIcon(':/plugins/bpla_plugin_flights/icons/icon_reload.png'))
        self.toolButton_cbreload.clicked.connect(self.initActiveLayersComboBox)
        self.checkBox.setChecked(True)
        self.toolButton.clicked.connect(self.getSaveFileName)
        self.pushButton.clicked.connect(self.doResult)
        self.lineEdit.setText(r'M:\Sourcetree\output\test_2.shp')

        # self.toolButton_plan.clicked.connect(self.getFolderName)
        # self.toolButton_cbreload_2.setIcon(QIcon(':/plugins/bpla_plugin_flights/icons/icon_reload.png'))
        # self.toolButton_cbreload_2.clicked.connect(self.initActiveLayersComboBox_2)

    def initActiveLayersComboBox(self):
        lg = LayerGetter()
        dictLyr = lg.getActiveLayers()
        GuiElemIFace(None).setComboBox(self.comboBox, dictLyr)

    # def initActiveLayersComboBox_2(self):
    #     lg = LayerGetter()
    #     dictLyr = lg.getActiveLayers(iface.mapCanvas())
    #     del dictLyr[self.comboBox.currentText()]
    #     GuiElemIFace(None).setComboBox(self.comboBox_2, dictLyr)

    def getSaveFileName(self):
        dlg = QtWidgets.QFileDialog(self)
        fn = dlg.getSaveFileName(self, 'Save file', r'M:\Sourcetree\output\test', filter='*.shp')[0]
        self.lineEdit.setText(fn)

    # def getFolderName(self):
    #     directory = str(QtWidgets.QFileDialog.getExistingDirectory())
    #     self.lineEdit_plan.setText('{}'.format(directory))

    def getFilepath(self):
        # get file name from line edit
        self.filepath = None
        if self.lineEdit.text() != '':
            self.filepath = self.lineEdit.text()
            fn = os.path.basename(self.filepath)
            fn = fn.split('.shp')
            self.filename = fn[0]

    def doResult(self):
        self.textEdit.setText('')
        start = perf_counter()

        # lyr = LyrMainTool()
        # lyr.guiUtil = GuiElemIFace(self.textEdit)
        # if self.lineEdit_plan.text() != '':
        #     lyr.createOnePlanLayer(self.lineEdit_plan.text())
        # else:
        #     lyr.createTempLayer(self.comboBox_2.currentText())

        lyr2 = MainIFace(GuiElemIFace(self.textEdit))
        lg = LayerGetter()
        lg.getLayer(self.comboBox.currentText())
        createTempLyrDeco = lyr2.exceptionsDecorator(lyr2.createTempLayer(lg),
                                                     '\nНе удалось создать временный слой! ')
        self.getFilepath()
        remZeroPointsDeco = lyr2.exceptionsDecorator(lyr2.removeZeroPoints(self.checkBox.isChecked()),
                                                     '\nНе удалось удалить нулевые точки! ')
        # # lyr.mainAzimutCalc()
        mainAlgorithmDeco = lyr2.exceptionsDecorator(lyr2.mainAzimutCalc(), '\nНе удалось классифицировать точки! ')
        saveFileDeco = lyr2.exceptionsDecorator(lyr2.saveToFile(self.filename, self.filepath),
                                                '\nНе удалось сохранить/загрузить файл! ')

        end = perf_counter()
        GuiElemIFace(self.textEdit).setOutputStyle('black', 'normal', 'Время работы плагина: ' + str(end - start))
