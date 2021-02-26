from PyQt5.QtGui import QColor, QFont
from qgis.utils import iface

from .LayerGetter import LayerGetter


class GuiElemIFace:
    def __init__(self):
        pass

    def setComboBox(self, comboBox, dictLyr):
        comboBox.clear()
        comboBox.addItems(dictLyr.keys())
        comboBox.show()

    def uploadLayer(self, textEdit, filepath, filename, typeOfFile):
        # show our new layer in qgis
        layer = iface.addVectorLayer(filepath, filename, typeOfFile)
        if not layer:
            textEdit.append('Не удалось загрузить слой в оболочку!\n')

    def setTextStyle(self, textEdit, color, weight, textstr=''):
        colors = {
            'black': QColor(0, 0, 0),
            'red': QColor(255, 0, 0),
            'green': QColor(51, 153, 0)
        }
        weights = {
            'normal': 1,
            'bold': QFont.Bold
        }
        textEdit.setTextColor(colors.get(color))
        textEdit.setFontWeight(weights.get(weight))
        textEdit.append(textstr)
