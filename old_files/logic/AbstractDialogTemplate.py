import sys

import pyperclip as pc
from datetime import datetime
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QHBoxLayout, QTabWidget, QTextEdit, QProgressBar, QPushButton, QSpacerItem, QSizePolicy, \
    QGridLayout, QWidget, QGroupBox, QToolButton, \
    QFileDialog, QSplitter, \
    QComboBox, QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout

from old_files.tools import OutputPen
from old_files.tools import ProgressBarWorker, FileRWriter
from old_files.tools import RunTimer


class AbstractDialogTemplate(QDialog):
    """AbstractDialogTemplate."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.isDevelopMode = False
        # titles
        input = 'Исходные данные'
        save_as = 'Сохранить как...'
        params = 'Параметры'
        log = 'Лог'
        cancel = 'Отменить'
        close = 'Закрыть'
        run = 'ОК'
        save_log = 'Сохранить лог файл как...'
        copy_log = 'Копировать текст'
        self.file_filter = "CSV files (*.txt *.csv);; ESRI Shapefiles (*.shp)"
        self.initial_filter = "ESRI Shapefiles (*.shp)"

        self.setWindowTitle('QDialog')
        self.setMinimumSize(600, 350)
        # Top Layout Components
        # Tab Widget
        self.tabWidget = QTabWidget()
        # params tab
        self.tabParams = QWidget()
        self.paramsTab_layout = QGridLayout()
        # input groupbox
        self.input_toolButton = QToolButton()
        self.input_toolButton.setIcon(QIcon(':/icons/icon_reload.png'))
        self.input_layout = QGridLayout()
        self.input_comboBox = QComboBox()
        self.input_layout.addWidget(self.input_comboBox, 0, 0)
        self.input_layout.addWidget(self.input_toolButton, 0, 1)
        self.input_groupBox = QGroupBox()
        self.input_groupBox.setTitle(input)
        self.input_groupBox.setLayout(self.input_layout)
        self.paramsTab_layout.addWidget(self.input_groupBox, 0, 0)
        self.paramsTab_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), 2, 0)
        # save groupbox
        self.save_line = QLineEdit()
        self.save_toolButton = QToolButton()
        self.save_toolButton.setText('...')
        save_layout = QHBoxLayout()
        save_layout.addWidget(self.save_line)
        save_layout.addWidget(self.save_toolButton)
        saveExt_layout = QVBoxLayout()
        saveExt_layout.addLayout(save_layout)
        self.save_groupBox = QGroupBox()
        self.save_groupBox.setTitle(save_as)
        self.save_groupBox.setLayout(saveExt_layout)
        self.paramsTab_layout.addWidget(self.save_groupBox, 3, 0)
        # adding widgets to params tab
        self.tabParams.setLayout(self.paramsTab_layout)
        self.tabWidget.addTab(self.tabParams, params)
        self.text_editor = QTextEdit()
        self.text_editor.setReadOnly(True)
        font = QFont()
        font.setPointSize(10)
        self.text_editor.setFont(font)
        # self.text_editor.setFixedSize(200, 180)

        # log tab
        self.tabLog = QWidget()
        logTab_layout = QGridLayout()
        self.tabLog.setLayout(logTab_layout)
        self.tabWidget.addTab(self.tabLog, log)
        # log_editor
        self.log_editor = QTextEdit()
        self.log_editor.setReadOnly(True)
        # save log buttons
        self.saveLog_button = QToolButton()
        self.saveLog_button.setIcon(QIcon(':/icons/save.png'))
        self.saveLog_button.setToolTip(save_log)
        self.copyLog_button = QToolButton()
        self.copyLog_button.setIcon(QIcon(':/icons/copy.png'))
        self.copyLog_button.setToolTip(copy_log)
        saveLog_layout = QHBoxLayout()
        saveLog_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        saveLog_layout.addWidget(self.saveLog_button)
        saveLog_layout.addWidget(self.copyLog_button)
        logTab_layout.addWidget(self.log_editor, 0, 0)
        logTab_layout.addLayout(saveLog_layout, 2, 0)
        logTab_layout.setContentsMargins(1, 1, 1, 1)
        logTab_layout.setSpacing(1)
        # adding to the Top Layout (includes TabWidget and TextEditor)
        top_layout = QSplitter(Qt.Horizontal)
        # self.tabWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.text_editor.setSizePolicy(stretch, QtWidgets.QSizePolicy.Expanding)
        top_layout.addWidget(self.tabWidget)
        top_layout.addWidget(self.text_editor)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.setMinimumSize(400, 100)
        # self.resize(450, 100)

        # Bottom Layout
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)
        self.cancel_button = QPushButton(cancel)
        self.cancel_button.setVisible(False)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.progressBar)
        bottom_layout.addWidget(self.cancel_button)

        # Standard Buttons
        self.buttonBox = QDialogButtonBox()
        # self.buttonBox.setStandardButtons(
        #     QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.addButton(close, QDialogButtonBox.RejectRole)
        self.buttonBox.addButton(run, QDialogButtonBox.AcceptRole)

        # Dialog's Layouts
        dlg_layout = QVBoxLayout()  # dialog's layout
        # adding layouts to dialog's form
        dlg_layout.addWidget(top_layout)
        dlg_layout.addLayout(bottom_layout)
        dlg_layout.addWidget(self.buttonBox)
        self.setLayout(dlg_layout)

        # connecting components to listeners
        self.load_combobox()
        self.input_toolButton.clicked.connect(self.load_combobox)
        self.save_toolButton.clicked.connect(self.open_file_dialog)
        self.saveLog_button.clicked.connect(self.save_log_file)
        self.copyLog_button.clicked.connect(self.copy_log_text)
        self.cancel_button.clicked.connect(self.stop_threads)
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.accepted.connect(self.run)

        self.out = OutputPen((self.log_editor, self.text_editor), self.tabWidget)

        if self.isDevelopMode:
            self.save_line.setText('/Users/ronya/Docs/GIS/TESTDATA/output')

    def load_combobox(self):
        """Load input ComboBox with gdf"""
        self.input_comboBox.clear()
        self.input_comboBox.addItems(FileRWriter().layers_from_canvas())
        self.input_comboBox.show()

    def open_file_dialog(self):
        """Диалог для сохранения файла"""
        dlg = QFileDialog(self)
        filename = dlg.getSaveFileName(parent=self,
                                       caption='Сохранить файл как...',
                                       directory='/Users/ronya/Docs/GIS/TESTDATA/',  # os.getcwd(),
                                       filter=self.file_filter,
                                       initialFilter=self.initial_filter,
                                       # options=QFileDialog.DontConfirmOverwrite | QFileDialog.DontUseNativeDialog
                                       )[0]
        self.save_line.setText(filename)

    def copy_log_text(self):
        """ Копирование текст лога в клипбоард """
        pc.copy(self.log_editor.toPlainText())

    def save_log_file(self):
        """ Сохранение лог-файла """
        dlg = QFileDialog(self)
        filename = dlg.getSaveFileName(self,
                                       'Сохранить лог файл...',
                                       f'{datetime.now()}_{self.windowTitle()}.log',
                                       filter='*.log',
                                       # options=QFileDialog.DontConfirmOverwrite | QFileDialog.DontUseNativeDialog
                                       )[0]
        text = self.log_editor.toPlainText()
        style, mess = FileRWriter().write_to_file('wb+', filename, text.encode('utf-8'))
        self.out.print(mess, style)

    def on_count_changed(self, value):
        """Срабатывает каждый раз, когда процент прогрессбара меняется."""
        self.progressBar.setValue(value)

    def run_progress_bar(self):
        self.bar_thread = QThread()
        self.bar_worker = ProgressBarWorker()
        self.bar_worker.moveToThread(self.bar_thread)
        # Connect signals and slots
        self.bar_thread.started.connect(self.bar_worker.run)
        self.bar_worker.progress.connect(self.on_count_changed)
        self.bar_worker.finished.connect(self.bar_thread.quit)
        self.bar_worker.finished.connect(self.bar_worker.deleteLater)
        self.bar_thread.finished.connect(self.bar_thread.deleteLater)
        # Start the thread
        self.bar_thread.start()

        # Final resets
        self.buttonBox.setEnabled(False)
        self.cancel_button.setVisible(True)
        self.bar_thread.finished.connect(lambda: self.buttonBox.setEnabled(True))
        self.bar_thread.finished.connect(lambda: self.cancel_button.setVisible(False))
        # self.bar_thread.finished.connect(self.stop_threads)

    def run_task(self, task):
        self.run_progress_bar()
        self.task_thread = QThread()
        self.task_worker = task  # ProgressBarWorker()
        self.task_worker.moveToThread(self.task_thread)
        # Connect signals and slots
        t = RunTimer(self.out)
        self.task_thread.started.connect(lambda: t.timer(self.task_worker.run)())
        self.task_worker.finished.connect(self.task_thread.quit)
        self.task_worker.finished.connect(self.task_worker.deleteLater)
        self.task_thread.finished.connect(self.task_thread.deleteLater)

        self.task_worker.progress.connect(self.out.print)
        self.task_worker.finished.connect(self.out.print)
        # Start the thread
        self.task_thread.start()

        # Final resets
        self.task_thread.finished.connect(self.stop_threads)

    def stop_threads(self):
        self.bar_worker.stop()
        self.bar_thread.quit()
        self.bar_thread.wait()

        self.task_worker.stop()
        # self.task_thread.requestInterruption()
        self.task_thread.quit()
        self.task_thread.wait()

    def run(self):
        """Запуск основного процесса после нажатия кнопки Run"""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = AbstractDialogTemplate()
    dlg.show()
    sys.exit(app.exec_())
