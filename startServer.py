from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import sys
from networking.server import ServerApp

# 載入設計好的GUI介面檔案
ui,_=loadUiType('ui/startWindow.ui')

QLINEEDITCOLOR = "#404040"
FONT = "fonts/VarelaRound-Regular.ttf"

class StartApp(QWidget, ui):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Enter Host IP & Port")
        self.cntBtn.clicked.connect(self.openServerWindow)
        self.ipField.setStyleSheet(f"color: {QLINEEDITCOLOR}")
        self.portField.setStyleSheet(f"color: {QLINEEDITCOLOR}")
        self.nameField.setStyleSheet(f"color: {QLINEEDITCOLOR}")
        self.show()

    def openServerWindow(self):
        server = ServerApp(self.ipField.text(), self.portField.text(), self.nameField.text())
        server.show()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StartApp()
    sys.exit(app.exec_())
