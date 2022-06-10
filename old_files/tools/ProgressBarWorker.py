import time

from PyQt5.QtCore import pyqtSignal, QObject

TIME_LIMIT = 100


class ProgressBarWorker(QObject):
    """
    Runs a counter thread.
    """
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self):
        super(ProgressBarWorker, self).__init__()
        self._isRunning = True

    def run(self):
        count = 0
        while count < TIME_LIMIT and self._isRunning is True:
            count += 1
            time.sleep(0.5)
            self.progress.emit(count)
        else:
            self.progress.emit(100)

        self.finished.emit()

    def stop(self):
        self._isRunning = False