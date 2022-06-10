from PyQt5.QtWidgets import QFileDialog

from old_files.tasks.ExtractControlsTask import ExtractControlsTask
from .AbstractDialogTemplate import AbstractDialogTemplate


class ExtractControlsDialog(AbstractDialogTemplate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Выделение контролей')
        self.save_groupBox.setTitle('Сохранить в папку...')
        self.text_editor.setText("<h3>Выделение контролей</h3>"
                                 "Классификация рядовых и контрольных профилей. "
                                 "Перед выполнением убедитесь, что все долеты обрезаны, а профиля пронумерованы.")

    def open_file_dialog(self):
        """Диалог для сохранения файла"""
        dlg = QFileDialog()
        fn = dlg.getExistingDirectory(self, 'Выбрать папку', r'/Users/ronya/My_Documents')
        self.save_line.setText(fn)

    def run(self):
        self.log_editor.clear()
        self.out.print(f'Начинаем выделение контролей...')
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
        params = {
            'INPUT': self.input_comboBox.currentText(),
            'OUTPUT': self.save_line.text(),
        }

        self.run_task(ExtractControlsTask(params, self.out))
