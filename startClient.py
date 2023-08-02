from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import sys, ipaddress, socket
from networking.client import ClientApp

# 載入設計好的GUI介面檔案
ui,_=loadUiType('ui/startWindow.ui')

QLINEEDITCOLOR = "#404040"
FONT = "fonts/VarelaRound-Regular.ttf"

class StartApp(QWidget, ui):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Enter Host IP & Port")
        self.cntBtn.clicked.connect(self.checkInput)
        self.ipField.setStyleSheet(f"color: {QLINEEDITCOLOR}")
        self.portField.setStyleSheet(f"color: {QLINEEDITCOLOR}")
        self.nameField.setStyleSheet(f"color: {QLINEEDITCOLOR}")
        self.show()

    def checkInput(self):
        ip = self.ipField.text()
        if ip == 'localhost' or self.validateIPv4(ip):
            pass
        else:
            QMessageBox.warning(None, "Error", "Please enter IP in IPv4 format")
            return
        
        port = self.portField.text()
        if self.validatePort(port):
            pass
        else:
            QMessageBox.warning(None, "Error", "Please enter port number between 1024-65535")
            return

        name = self.nameField.text()
        if name == "":
            QMessageBox.warning(None, "Error", "Please enter a nickname")
            return
        
        self.checkConnection(ip, port, name)

    def checkConnection(self, ip, port, name):

        # tmpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print("b4")
        # res = tmpSocket.connect_ex((str(ip), int(port)))
        # print("after")
        # if res == 0:
        #     tmpSocket.close()
        #     print("call openChatWindow")
        #     self.openChatWindow(ip, port, name)
        # else:
        #     QMessageBox.warning(None, "Error", f"Error connecting to the IP and port\n{e}")
        #     return
        self.openChatWindow(ip, port, name)

    def openChatWindow(self, ip, port, name):
        chatWindow = ClientApp(ip, port, name)
        chatWindow.show()
        self.hide()

    def validatePort(self, port):
        try:
            port = int(port)
            if port > 1023 and port <= 65535:
                return True
            else:
                return False
        except ValueError:
            return False
                
    def validateIPv4(self, ip):
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StartApp()
    sys.exit(app.exec_())