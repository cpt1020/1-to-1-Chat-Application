from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import sys, ipaddress, os, socket
from networking.server import ServerApp

# 載入設計好的GUI介面檔案
ui,_=loadUiType('ui/startWindow.ui')

QLINEEDITCOLOR = "#404040"
FONT = "font/VarelaRound-Regular.ttf"

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

    #     self.loadFont()
    #     constan = QFont(QFontDatabase.applicationFontFamilies(self.font_id)[0])
    #     constan.setPointSize(8)
    #     constan.setWeight(QFont.Normal)
    #     self.main_label.setFont(constan)


    # def loadFont(self):
    #     font_path = os.path.join(os.path.dirname(__file__), 'font', 'VarelaRound-Regular.ttf')
    #     self.font_id = QFontDatabase.addApplicationFont(font_path)
        

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
        # tmpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # try:
        #     tmpSocket.bind((str(ip), int(port)))
        #     self.openChatWindow(ip, port, name, tmpSocket)
        # except socket.error as e:
        #     QMessageBox.warning(None, "Error", f"Error binding to the IP and port\n{e}")
        #     return
        self.openChatWindow(ip, port, name)

    # def openChatWindow(self, ip, port, name, tmpSocket):
    #     tmpSocket.close()
    def openChatWindow(self, ip, port, name):
        self.chatWindow = ServerApp(ip, port, name)
        self.chatWindow.show()
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
