# -*- coding: utf-8 -*-

import csv
import math
import os
from datetime import datetime
from random import random, randint

from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QIcon
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtGui import *
from qgis.core import *

from osgeo import ogr, osr
import sys

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
from qgis.utils import iface

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'numit_plugin.ui'))


class numit_pluginDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(numit_pluginDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.initActiveLayersComboBox()
        self.toolButton_cbreload.setIcon(QIcon(':/plugins/bpla_plugin_flights/icons/icon_reload.png'))
        self.toolButton_cbreload.clicked.connect(self.initActiveLayersComboBox)
        self.pushButton.clicked.connect(self.doResult)

    def initActiveLayersComboBox(self):
        canvas = iface.mapCanvas()
        layers = canvas.layers()  # по умолчанию только видимые слои
        self.actVecLyrDict = {}
        self.comboBox.clear()
        for layer in layers:
            if ((type(layer) == QgsVectorLayer) and (layer.geometryType() == 0)):
                # setdefault добавляет элементы с проверкой на повторяющиеся
                # если у пользователя два слоя с одиноковыми именами, в комбобокс попадет только один из них
                self.actVecLyrDict.setdefault(layer.name(), layer)
        self.comboBox.addItems(self.actVecLyrDict.keys())
        self.comboBox.show()

    def getLayer(self):
        # get layer from combobox
        self.layer = self.actVecLyrDict.get(self.comboBox.currentText())
        if self.layer is not None:
            self.layername = self.layer.name()
            self.driverName = self.layer.dataProvider().storageType()
            cur_lyr_path = self.layer.dataProvider().dataSourceUri()

            if self.driverName == 'ESRI Shapefile':
                char_arr = cur_lyr_path.split('|')
                self.layerpath = char_arr[0]



    def doResult(self):
        self.setTextStyle('black', 'normal')
        self.textEdit.setText('')