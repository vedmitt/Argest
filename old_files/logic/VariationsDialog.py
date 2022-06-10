from PyQt5.QtWidgets import QLineEdit, QToolButton, QGroupBox, QHBoxLayout, QFileDialog, QFormLayout, QSpinBox

from ..tasks import VariationsTask
from .AbstractDialogTemplate import AbstractDialogTemplate


class VariationsDialog(AbstractDialogTemplate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Учет вариаций')

        # магнитка
        self.input_groupBox.setTitle('Магнитка')
        self.input_layout.removeWidget(self.input_comboBox)
        self.input_layout.removeWidget(self.input_toolButton)
        self.input_comboBox = QLineEdit()
        self.input_toolButton = QToolButton()
        self.input_toolButton.setText('...')
        self.input_layout.addWidget(self.input_comboBox)
        self.input_layout.addWidget(self.input_toolButton)

        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(0)
        self.spinbox.setMaximum(900000)
        self.spinbox.setValue(60000)
        formLayout = QFormLayout()
        formLayout.addRow('Константа магнитного поля: ', self.spinbox)
        self.input_layout.addLayout(formLayout, 2, 0)

        # вариации
        self.var_toolButton = QToolButton()
        self.var_toolButton.setText('...')
        self.var_layout = QHBoxLayout()
        self.var_lineEdit = QLineEdit()
        self.var_layout.addWidget(self.var_lineEdit)
        self.var_layout.addWidget(self.var_toolButton)
        self.var_groupBox = QGroupBox()
        self.var_groupBox.setTitle('Вариации')
        self.var_groupBox.setLayout(self.var_layout)

        self.paramsTab_layout.addWidget(self.var_groupBox, 1, 0)

        self.text_editor.setText("<h3>Учет вариаций</h3>"
                                 "Выберите файл(ы) магнитной съемки и файл(ы) вариаций.")

        self.file_filter = "CSV files (*.txt *.csv)"
        self.initial_filter = "CSV files (*.txt *.csv)"

        self.input_toolButton.clicked.connect(self.get_files)
        self.var_toolButton.clicked.connect(self.get_files)

    def get_files(self):
        dlg = QFileDialog(self)
        filenames = dlg.getOpenFileNames(parent=self,
                                         caption='Выбрать файлы...',
                                         directory='/Users/ronya/Docs/GIS/TESTDATA/input/Aunakit',  # os.getcwd(),
                                         filter=self.file_filter,
                                         )[0]
        # self.out.print(f'{filenames}')
        if self.sender() == self.input_toolButton:
            self.magn_files = filenames
            self.input_comboBox.setText(f'[ {len(self.magn_files)} файл(ов) выбрано ]')
        elif self.sender() == self.var_toolButton:
            self.var_files = filenames
            self.var_lineEdit.setText(f'[ {len(self.var_files)} файл(ов) выбрано ]')

    def run(self):
        self.log_editor.clear()
        self.out.print(f'Начинаем учет вариаций...')
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)
        params = {
            'INPUT': self.magn_files,
            'VAR': self.var_files,
            'CONST': self.spinbox.value(),
            'OUTPUT': self.save_line.text(),
        }

        # run threads
        self.run_task(VariationsTask(params, self.out))
