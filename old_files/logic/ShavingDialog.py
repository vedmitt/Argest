from PyQt5.QtWidgets import QCheckBox

from ..tasks import ShavingTask
from .AbstractDialogTemplate import AbstractDialogTemplate


class ShavingDialog(AbstractDialogTemplate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Разбраковка точек')
        self.isRemove = QCheckBox('Удалить отбракованные точки')
        self.isRemove.setChecked(True)
        self.input_layout.addWidget(self.isRemove)
        self.text_editor.setText('<h3>Разбраковка точек</h3> '
                                 'Классификация и удаление ненужных участков полетов.')

    def run(self):
        self.log_editor.clear()
        self.out.print(f'Начинаем разбраковку точек...')
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
        params = {
            'INPUT': self.input_comboBox.currentText(),
            'OUTPUT': self.save_line.text(),
            'DEL': self.isRemove.isChecked(),
        }

        # run threads
        self.run_task(ShavingTask(params, self.out))