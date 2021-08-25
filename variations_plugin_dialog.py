# -*- coding: utf-8 -*-
import math
import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
from qgis._core import QgsVectorLayer

from .tools.VariationsTool import VariationsTool
from .tools.GuiElemIFace import GuiElemIFace

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'variations_plugin.ui'))


class variations_plugin_Dialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(variations_plugin_Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        # файлы с вариациями
        self.toolButton_in_var.clicked.connect(self.getPathToFolderOrFile)
        # файлы с магниткой
        self.toolButton_in_magn.clicked.connect(self.getPathToFolderOrFile)
        # сохранить результат
        self.toolButton_output.clicked.connect(self.getPathToFolderOrFile)
        # Получить результат
        self.pushButton_calc.clicked.connect(self.doResult)

        # self.lineEdit_in_var.setText(r'/Users/ronya/My_Documents/karelia/20210523_Karelia/Var')
        # self.lineEdit_in_magn.setText(r'/Users/ronya/My_Documents/karelia/20210523_Karelia/Group_1')
        # self.lineEdit_output.setText(r'/Users/ronya/My_Documents/Karelia/output_test.txt')

    def getPathToFolderOrFile(self):
        sender = self.sender()

        dlg = QtWidgets.QFileDialog(self)

        if str(sender.objectName()) == 'toolButton_in_var':
            fn = dlg.getExistingDirectory(self, r'/Users/ronya/My_Documents')
            self.lineEdit_in_var.setText(fn)

        elif str(sender.objectName()) == 'toolButton_in_magn':
            fn = dlg.getExistingDirectory(self, r'/Users/ronya/My_Documents')
            self.lineEdit_in_magn.setText(fn)
        else:
            fn = dlg.getSaveFileName(self, 'Save file', r'/Users/ronya/My_Documents', filter='*.txt')[0]
            self.lineEdit_output.setText(fn)

    def doResult(self):
        self.textEdit.clear()
        guiUtil = GuiElemIFace(self.textEdit)

        if self.lineEdit_in_var.text() == '' or self.lineEdit_in_magn.text() == '' \
                or self.lineEdit_output.text() == '':
            guiUtil.setOutputStyle([-1, 'Введите данные в форму!'])
        else:
            # если данные введены в форму
            var_path = self.lineEdit_in_var.text()  # путь до папки с вариациями
            magn_path = self.lineEdit_in_magn.text()  # путь до папки с магниткой
            res_path = self.lineEdit_output.text()  # путь до папки с результатами

            mess = VariationsTool().main_calcVariations(var_path, magn_path, res_path)
            guiUtil.setOutputStyle(mess)