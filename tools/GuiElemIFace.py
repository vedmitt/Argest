from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QAbstractItemView

from .dataStorage.FileManager import FileManager


class GuiElemIFace:

    def __init__(self, textEdit=None):
        self.textEdit = textEdit

    def setComboBox(self, comboBox, content):
        comboBox.clear()
        comboBox.addItems(content)
        comboBox.show()

    def setComboBoxWithLayers(self, comboBox, exclude_lyr=None):
        lg = FileManager()
        dictLyr = lg.getActiveLayersFromCanvas(exclude_lyr)
        self.setComboBox(comboBox, dictLyr.keys())

    def setListWidgetWithData(self, listWidget, entries, selectMode='multiselect'):
        listWidget.clear()
        for item in entries:
            listWidget.addItem(item)

        if selectMode is 'multiselect':
            listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)  # Hold CTRL to select multiple

    def getTextFromRadioButton(self, radioButtons):
        text = ''
        for rb in radioButtons:
            if rb.isChecked():
                text = rb.text()
        return text

    def setOutputStyle(self, textStyle):
        colors = {
            'black': QColor(0, 0, 0),
            'red': QColor(255, 0, 0),
            'green': QColor(51, 153, 0)
        }
        weights = {
            'normal': 1,
            'bold': QFont.Bold
        }
        style = []
        if textStyle[0] == -1:
            style.append('red')
            style.append('bold')
        elif textStyle[0] == 1:
            style.append('green')
            style.append('bold')
        else:
            style.append('black')
            style.append('normal')

        if self.textEdit and style is not None:
            self.textEdit.setTextColor(colors.get(style[0]))
            self.textEdit.setFontWeight(weights.get(style[1]))
            self.textEdit.append(textStyle[1])
