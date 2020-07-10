"""
Connection Dialog

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    13/06/2020

@summary:   TBD

@status:    Under development
@todo:

"""

from PyQt5.QtCore import QRegExp, pyqtSlot
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog

from PyQt5.uic import loadUiType, loadUi
from server.communicationmanager import Com

ConnectionDialog_Form, ConnectionDialog_Base = loadUiType('view/connectiondialog.ui')


class ConnectionDialog(ConnectionDialog_Base, ConnectionDialog_Form):

    def __init__(self, parent=None):
        super(ConnectionDialog, self).__init__(parent)

        self.setupUi(self)
        self.parent = parent

        # Com.onStatusChanged.connect(self.setConnectionStatusSlot)

        # connect interface signals
        self.button_connectToServer.clicked.connect(self.connectClientToServer)
        self.button_removeServerAddress.clicked.connect(self.connectClientToServer)
        self.button_addServerAddress.clicked.connect(self.connectClientToServer)
        self.status_label.setVisible(False)

        ipValidator = QRegExp(
            '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)'
            '{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
        self.ip_box.setValidator(QRegExpValidator(ipValidator, self))
        self.ip_box.addItem('192.168.2.2')
        # for item in params.hosts: self.ip_box.addItem(item)
        print("connection dialog ready")

    def connectClientToServer(self):
        ip = self.ip_box.currentText()

        connection = Com.connectClient(ip)
        if connection:
            self.status_label.setText('Connected')
        elif not connection:
            self.status_label.setText('Not connected')
            self.btn_connect.setText('Retry')
        else:
            self.status_label.setText('Not connected with status: '+str(connection))
            self.btn_connect.setText('Retry')

        self.parent.status_connection.setChecked(connection)
        self.status_label.setVisible(True)



    def addNewServerAddress(self):

        ip = self.ip_box.currentText()
        """
        if not ip in params.hosts:
            self.ip_box.addItem(ip)
        else: return
        params.hosts = [self.ip_box.itemText(i) for i in range(self.ip_box.count())]
        """
        print(ip)

    def removeServerAddress(self):
        idx = self.ip_box.currentIndex()
        print(idx)

    @pyqtSlot(str)
    def setConnectionStatusSlot(self, status: str = None) -> None:
        """
        Set the connection status
        @param status:  Server connection status
        @return:        None
        """
        self.parent.status_connection.setText(status)
