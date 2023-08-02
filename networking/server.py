from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import socket, sys, time, datetime, os # os for getting file size
# from socketserver import ThreadingMixIn 

# 載入設計好的GUI介面檔案
ui,_=loadUiType('ui/mainApp.ui')

SYSMSGCOLOR = "#FF9300"
TIMECOLOR = "#7F7F7F"
MSGCOLOR = "#404040"
FONT = "fonts/VarelaRound-Regular.ttf"

class ServerApp(QDialog, ui):
    def __init__(self, ipVal, portVal, nameVal):
        QWidget.__init__(self)
        self.setupUi(self)
        self.sendBtn.clicked.connect(self.showSentMsg)
        self.leaveBtn.clicked.connect(self.closeApp)
        self.sendFileBtn.clicked.connect(self.sendFile)
        self.saveHisBtn.clicked.connect(self.saveHistory)
        self.stickerBtn.clicked.connect(self.showSticker)
        self.chatRoom.setStyleSheet("background-color: white;")
        self.chatRoom.verticalScrollBar().setStyleSheet('height: 0px; width: 0px;')
        self.chatRoom.setReadOnly(True)
        self.typeText.setStyleSheet(f"color: {MSGCOLOR}")
        self.chatRoomTextCursor = self.chatRoom.textCursor()
        self.setWindowTitle("Chatting Room - Server Window")
        # self.show()
        self.ip = ipVal
        self.port = portVal
        self.serverName = nameVal
        self.clientName = None
        
        self.server = ServerThread(self, self.ip, self.port, self.serverName)
        self.server.systemMessage.connect(self.showSysMsg)
        self.server.clientMessage.connect(self.showClientMsg)
        self.server.recFileMessage.connect(self.receiveFile)
        self.server.stickerSentSignal.connect(self.showSentSticker)
        self.server.start()

    def showSentSticker(self, imgName):
        self.chatRoom.moveCursor(self.chatRoomTextCursor.End)
        curTime = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y.%m.%d %H:%M:%S')
        preMsg = f"<span style=\" font-size:16pt; color:{TIMECOLOR};\" >{self.clientName}@{curTime}</span>"
        self.chatRoom.append(preMsg)
        self.chatRoom.setAlignment(Qt.AlignLeft)
        
        imgFormat = QTextImageFormat()
        imgFormat.setWidth(150)
        imgFormat.setHeight(150)
        imgFormat.setName(imgName)
        self.chatRoom.append("")
        self.chatRoomTextCursor.insertImage(imgFormat)
        self.chatRoom.setAlignment(Qt.AlignLeft)
        self.typeText.setText("")
        self.chatRoomTextCursor = self.chatRoom.textCursor()

    def showSticker(self):
        # https://stackoverflow.com/questions/15539075/inserting-qimage-after-string-in-qtextedit
        self.chatRoom.moveCursor(self.chatRoomTextCursor.End)
        curTime = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y.%m.%d %H:%M:%S')
        preMsg = f"<span style=\" font-size:16pt; color:{TIMECOLOR};\" >{self.serverName}@{curTime}</span>"
        self.chatRoom.append(preMsg)
        self.chatRoom.setAlignment(Qt.AlignRight)
        
        imgName = "stickers/001.png"
        imgFormat = QTextImageFormat()
        imgFormat.setWidth(150)
        imgFormat.setHeight(150)
        imgFormat.setName(imgName)
        self.chatRoom.append("")
        self.chatRoomTextCursor.insertImage(imgFormat)
        self.chatRoom.setAlignment(Qt.AlignRight)
        self.typeText.setText("")
        self.chatRoomTextCursor = self.chatRoom.textCursor()
        self.server.clientSocket.sendall(b"<SEND_STICKER>")
        time.sleep(0.1)
        self.server.clientSocket.sendall(imgName.encode('utf-8'))

    def saveHistory(self):
        fdir = QFileDialog.getExistingDirectory(self, "Select a Directory", "")
        if fdir:
            fname = f"Chat history with {self.clientName} @ {datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y.%m.%d %H.%M.%S')}"
            with open(f'{fdir}/{fname}.txt', 'w') as file:
                file.write(str(self.chatRoom.toPlainText()))

    def sendFile(self):
        fdir,_ = QFileDialog.getOpenFileName(self, "Select a File", "", "All Files (*);;PNG Files (*.png);;C++ Files(*.cpp);;Python Files (*.py)")
        # 會return一個tuple，file directory和file extension

        if fdir:
            fsize_actual = os.path.getsize(fdir)
            fsize = self.getSizeUnit(fsize_actual)
            fname = self.getFileName(fdir)
            self.showSysMsg(f"You selected {fname}")
            self.server.sendFileSignal.emit(fdir, fname, fsize, fsize_actual)

    def getFileName(self, fname):
        return fname.split("/")[-1]

    def getSizeUnit(self, fsize):
        exp = 0
        while fsize >= 1000:
            exp += 1
            fsize /= 1000
            if exp == 4:
                break
        
        expMap = {0: "bytes", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
        return f"{round(fsize, 2)} {expMap[exp]}"

    def showSentMsg(self):
        self.chatRoom.moveCursor(self.chatRoomTextCursor.End)
        curTime = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y.%m.%d %H:%M:%S')
        preMsg = f"<span style=\" font-size:16pt; color:{TIMECOLOR};\" >{self.serverName}@{curTime}</span>"
        self.chatRoom.append(preMsg)
        self.chatRoom.setAlignment(Qt.AlignRight)

        msg = self.typeText.text()
        self.server.sendMsg(msg)
        print(f"[SERVER] {msg}")
        msg = f"<span style=\" color:{MSGCOLOR};\" >{msg}</span>"
        self.chatRoom.append(msg)
        self.chatRoom.setAlignment(Qt.AlignRight)
        self.typeText.setText("")
        self.chatRoomTextCursor = self.chatRoom.textCursor()

    def showSysMsg(self, msg):
        self.chatRoom.moveCursor(self.chatRoomTextCursor.End)
        print(f"[SYSTEM MESSAGE] {msg}")
        msg = f"<span style=\" font-size:16pt; color:{SYSMSGCOLOR};\" >{msg}</span>"
        self.chatRoom.append(msg)
        self.chatRoom.setAlignment(Qt.AlignCenter)
        self.chatRoomTextCursor = self.chatRoom.textCursor()
        
    def showClientMsg(self, msg):
        self.chatRoom.moveCursor(self.chatRoomTextCursor.End)
        curTime = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y.%m.%d %H:%M:%S')
        preMsg = f"<span style=\" font-size:16pt; font-weight:600; color:{TIMECOLOR};\" >{self.clientName}@{curTime}</span>"
        self.chatRoom.append(preMsg)
        self.chatRoom.setAlignment(Qt.AlignLeft)

        print(f"[CLIENT] {msg}")
        msg = f"<span style=\" color:{MSGCOLOR};\" >{msg}</span>"
        self.chatRoom.append(msg)
        self.chatRoom.setAlignment(Qt.AlignLeft)
        self.chatRoomTextCursor = self.chatRoom.textCursor()
        
    def closeApp(self):
        self.server.connecting = False
        self.server.serverSocket.close()
        self.server.exit()
        self.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Closing Window", "You sure you wanna close the window? 🥺", QMessageBox.Yes | QMessageBox.No)
        if (reply == QMessageBox.Yes):
            self.showSysMsg("Server closed window")
            self.server.connecting = False
            self.server.serverSocket.close()
            self.server.exit()
            event.accept()
        else:
            event.ignore()

    def receiveFile(self, msg, fname, fsize):
        reply = QMessageBox.question(self, "Receiving file", f"{msg}.\nWould you like to receive? 😊", QMessageBox.Yes | QMessageBox.No)
        
        if (reply == QMessageBox.Yes):
            fdir = QFileDialog.getExistingDirectory(self, "Select a Directory", "")
            if fdir != "":
                reply = True
                self.server.userReply = (reply, fdir, fname, fsize)
            else:
                reply = False
                self.server.userReply = (reply, "", fname, fsize)
        else:
            reply = False
            self.server.userReply = (reply, "", fname, fsize)

        self.server.userReplySignal.emit()

class ServerThread(QThread):
    clientMessage = pyqtSignal(str)
    systemMessage = pyqtSignal(str)
    recFileMessage = pyqtSignal(str, str, int)
    stickerSentSignal = pyqtSignal(str)
    userReplySignal = pyqtSignal()
    sendFileSignal = pyqtSignal(str, str, str, int)

    def __init__(self, window, ipVal, portVal, nameVal):
        QThread.__init__(self, parent = None)
        self.window = window
        self.serverName = nameVal
        self.connecting = True
        self.format = 'utf-8'
        self.port = int(portVal)
        self.server = str(ipVal)
        self.addr = (self.server, self.port)
        self.userReply = None
        self.sentFileDir = None
        self.sendFileSignal.connect(self.sendFileInfo)
        
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind(self.addr)
        self.serverSocket.listen(1)

    def run(self):

        self.systemMessage.emit("Waiting for connection from client...")
        self.clientSocket = None
        (self.clientSocket, (ip, port)) = self.serverSocket.accept()

        self.sendServerName()
        self.clientName = self.clientSocket.recv(2048).decode(self.format)
        self.window.clientName = self.clientName
        self.systemMessage.emit(f"{self.clientName} is now connected ^_^")

        while self.connecting:

            msg = self.clientSocket.recv(2048)
            
            if not msg:
                self.connecting = False
                self.clientSocket.close()
                self.systemMessage.emit(f"{self.clientName} left chat room")
                break
            elif msg == b"<SEND_FILE>":
                self.receiveFile()

                if self.userReply[0] == True:
                    self.clientSocket.sendall(b"<RECEIVE_SENT_FILE>")
                else:
                    self.clientSocket.sendall(b"<REJECT_SENT_FILE>")
            elif msg == b"<RECEIVE_SENT_FILE>":
                self.systemMessage.emit(f"{self.clientName} accepted your file")
                self.sendFile()
            elif msg == b"<REJECT_SENT_FILE>":
                self.systemMessage.emit(f"{self.clientName} refused to receive your file")
            elif msg == b"<SENDING>":
                self.saveFile()
            elif msg == b"<SEND_STICKER>":
                imgName = self.clientSocket.recv(2048).decode(self.format)
                self.stickerSentSignal.emit(imgName)
            else:
                msg = msg.decode(self.format)
                self.clientMessage.emit(msg)
        
        self.serverSocket.close()

    def sendFileInfo(self, fdir, fname, fsize, fsize_actual):

        self.clientSocket.sendall(b"<SEND_FILE>")
        time.sleep(0.1)
        self.clientSocket.sendall(f"{self.serverName} would like to send you a file.\nFile name: {fname}\nFile size: {fsize}".encode(self.format))
        time.sleep(0.1)
        self.clientSocket.sendall(f"{fname}".encode(self.format))
        time.sleep(0.1)
        self.clientSocket.sendall(str(fsize_actual).encode(self.format))
        self.sentFileDir = fdir

    def sendFile(self):
        try:
            self.clientSocket.sendall(b"<SENDING>")

            try:
                file = open(self.sentFileDir, "rb")
            except Exception as e:
                self.systemMessage.emit(f"Error opening file: {e}")
            data = file.read()
            fsize = len(data)
            total_sent = 0

            while total_sent < fsize:
                sent = self.clientSocket.send(data[total_sent:])
                if sent == 0:
                    break
                total_sent += sent
            file.close()

        except Exception as e:
            self.systemMessage.emit(f"Error sending image: {e}")
        self.sentFileDir = None

    def receiveFile(self):
        msg = self.clientSocket.recv(2048).decode(self.format)
        fname = self.clientSocket.recv(2048).decode(self.format)
        fsize = int(self.clientSocket.recv(2048).decode(self.format))
        self.recFileMessage.emit(msg, fname, fsize)

        loop = QEventLoop()
        self.userReplySignal.connect(loop.quit)
        loop.exec_()

        # return self.userReply

    def saveFile(self):

        fdir = self.userReply[1]
        fname = self.userReply[2]

        fpath = f"{fdir}/{fname}"
        file = open(fpath, "wb")
        file_bytes = b""
        fsize = self.userReply[3]

        while len(file_bytes) < fsize:
            data = self.clientSocket.recv(2048)
            if not data:
                break
            file_bytes += data
            if len(file_bytes) == fsize:
                break

        file.write(file_bytes)
        file.close()
        self.systemMessage.emit(f"{fname} received")
        self.userReply = None
    
    # def replyRecFile(self, reply):

    #     if reply == True:
    #         self.clientSocket.sendall(b"<RECEIVE_SENT_FILE>")
    #     else:
    #         self.clientSocket.sendall(b"<REJECT_SENT_FILE>")

    def sendServerName(self):
        try:
            self.clientSocket.send(self.serverName.encode(self.format))
        except Exception as e:
            self.systemMessage.emit(f"Error sending srver name: {e}")

    def sendMsg(self, msg):
        try:
            self.clientSocket.send(msg.encode(self.format))
        except Exception as e:
            self.systemMessage.emit(f"Error sending message: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ServerApp()
    sys.exit(app.exec_())