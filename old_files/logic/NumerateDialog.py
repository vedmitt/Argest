from ..tasks import NumerateTask
from .AbstractDialogTemplate import AbstractDialogTemplate


class NumerateDialog(AbstractDialogTemplate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Нумерация профилей')
        self.text_editor.setText("<h3>Нумерация профилей</h3>"
                                 "Перед выполнением убедитесь, что данные разбракованы и участки долетов удалены.")

    def run(self):
        self.log_editor.clear()
        self.out.print(f'Начинаем нумерацию точек...')
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
        params = {
            'INPUT': self.input_comboBox.currentText(),
            'OUTPUT': self.save_line.text(),
        }

        # run threads
        self.run_task(NumerateTask(params, self.out))
