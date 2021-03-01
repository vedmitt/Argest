# -*- coding: utf-8 -*-
import os

from PyQt5.QtGui import QIcon
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtGui import *

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
from qgis._core import QgsVectorLayer
from qgis.utils import iface

from .LayerUtils.GuiElemIFace import GuiElemIFace
from .LayerUtils.LayerGetter import LayerGetter
from .LayerUtils.LyrConvTool import LyrConvTool

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
        lg = LayerGetter()
        self.dictLyr = lg.getActiveLayers(iface.mapCanvas())
        GuiElemIFace(None).setComboBox(self.comboBox, self.dictLyr)

    def doResult(self):
        self.textEdit.setText('')
        # vlayer = QgsVectorLayer(lg.layerpath, lg.layername, 'ogr')
        LyrConvTool(self.textEdit).numbersForFlights(self.comboBox.currentText())
