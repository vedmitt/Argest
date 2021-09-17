from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
                             QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QLineEdit,
                             QSpacerItem, QSizePolicy, QComboBox, QAbstractItemView)

from .dataStorage.FileManager import FileManager


class GuiElemIFace:

    def __init__(self, textEdit=None):
        self.textEdit = textEdit

    def createLabelField(self, labelText, fieldType, content):
        hbox = QHBoxLayout()
        label = QLabel(labelText)
        spaceItem = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        if fieldType == 'QComboBox':
            field = QComboBox()
            field.addItems(content)
        else:
            field = QLineEdit(content[0])

        hbox.addWidget(label)
        hbox.addItem(spaceItem)
        hbox.addWidget(field)
        # hbox.addStretch(1)

        return hbox, field

    def createGroupBox(self, gb_title, content):
        groupBox = QGroupBox(gb_title)
        vbox = QVBoxLayout()

        fields = []
        for line in content:
            labelField, field = self.createLabelField(line[0], line[1], line[2])
            fields.append(field)
            vbox.addLayout(labelField)

        # vbox.minimumSize()
        groupBox.setLayout(vbox)

        return groupBox, fields

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
