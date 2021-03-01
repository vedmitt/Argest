from PyQt5.QtGui import QColor, QFont
from qgis.utils import iface

from .LayerGetter import LayerGetter


class GuiElemIFace:
    textEdit = None

    def __init__(self, textEdit):
        GuiElemIFace.textEdit = textEdit

    def setComboBox(self, comboBox, dictLyr):
        comboBox.clear()
        comboBox.addItems(dictLyr.keys())
        comboBox.show()

    def uploadLayer(self, filepath, filename, typeOfFile):
        # show our new layer in qgis
        layer = iface.addVectorLayer(filepath, filename, typeOfFile)
        if not layer:
            self.setTextEditStyle('red', 'bold', 'Не удалось загрузить слой в оболочку!\n')

    def setTextEditStyle(self, color, weight, textstr=''):
        colors = {
            'black': QColor(0, 0, 0),
            'red': QColor(255, 0, 0),
            'green': QColor(51, 153, 0)
        }
        weights = {
            'normal': 1,
            'bold': QFont.Bold
        }
        if GuiElemIFace.textEdit is not None:
            GuiElemIFace.textEdit.setTextColor(colors.get(color))
            GuiElemIFace.textEdit.setFontWeight(weights.get(weight))
            GuiElemIFace.textEdit.append(textstr)
