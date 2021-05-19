from PyQt5.QtGui import QColor, QFont
from qgis.utils import iface

from .LayerManager import LayerManager


class GuiElemIFace:
    def __init__(self, textEdit):
        self.textEdit = textEdit

    # def setComboBox(self, comboBox, dictLyr):
    #     comboBox.clear()
    #     comboBox.addItems(dictLyr.keys())
    #     comboBox.show()

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
