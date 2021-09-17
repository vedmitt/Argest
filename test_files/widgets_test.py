import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
                             QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QLineEdit,
                             QSpacerItem, QSizePolicy, QComboBox)


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        grid = QGridLayout()

        # test
        gb_title = "Параметры текстовых файлов:"
        entries1 = ['1', '2', '3']
        entries2 = ['4', '5', '6']
        entries3 = ['7', '8', '9']
        entries4 = ['10']

        content = [
            ['Разделитель:', 'QComboBox', entries1],
            ['X field:', 'QComboBox', entries2],
            ['Y field:', 'QComboBox', entries3],
            ['Geometry CRS:', 'QLineEdit', entries4]
        ]

        groupBox, fields = self.createGroupBox(gb_title, content)
        grid.addWidget(groupBox, 0, 0)
        # grid.addWidget(self.createExampleGroup(), 1, 0)
        # grid.addWidget(self.createExampleGroup(), 0, 1)
        # grid.addWidget(self.createExampleGroup(), 1, 1)
        self.setLayout(grid)

        self.setWindowTitle("PyQt5 Group Box")
        # self.resize(400, 300)
        self.adjustSize()

        print(fields[3].text())

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

    def lineEdit_clicked(self):
        self.setWindowTitle("New title")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())
