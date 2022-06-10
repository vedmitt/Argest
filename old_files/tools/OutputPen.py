from PyQt5.QtGui import QColor, QFont

COLORS = {
    'black': QColor(0, 0, 0),
    'red': QColor(255, 0, 0),
    'green': QColor(51, 153, 0)
}
WEIGHTS = {
    'normal': 1,
    'bold': QFont.Bold
}
TEXTSIZE = 10


class OutputPen:

    def __init__(self, text_editors=None, tabWidget=None):
        super().__init__()
        self.text_editors = text_editors
        self.tabWidget = tabWidget
        # self.text_editors = text_editors[0]
        # self.log_editor = text_editors[1]

    def print(self, mess_text, mess_type=0, edit_type=0):
        """ Вывести текст в текстедит заданного стиля"""
        style = []
        if mess_type == -1:
            style.append('red')
            style.append('bold')
        elif mess_type == 1:
            style.append('green')
            style.append('bold')
        else:
            style.append('black')
            style.append('normal')

        self.text_editors[edit_type].setTextColor(COLORS.get(style[0]))
        self.text_editors[edit_type].setFontWeight(WEIGHTS.get(style[1]))
        font = QFont()
        font.setPointSize(TEXTSIZE)
        self.text_editors[edit_type].setFont(font)
        self.text_editors[edit_type].append(str(mess_text))