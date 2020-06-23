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

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.uic import loadUiType, loadUi
from server.communicationmanager import Com

ConnectionDialog_Form, ConnectionDialog_Base = loadUiType('view/connectiondialog.ui')


class ConnectionDialog(ConnectionDialog_Base, ConnectionDialog_Form):

    # connected = pyqtSignal()

    def __init__(self, parent=None):
        super(ConnectionDialog, self).__init__(parent)

        self.parent = parent

        self.setupUi(self)

        # Setup close event
        # self.ui = loadUi('view/connectiondialog.ui')
        # self.ui.closeEvent = self.closeEvent

        # self.conn_help = QPixmap('ui/connection_help.png')
        # self.help.setVisible(False)

        # connect interface signals
        self.btn_connect.clicked.connect(self.connect_event)
        # self.btn_addIP.clicked.connect(self.add_IP)
        # self.btn_removeIP.clicked.connect(self.remove_IP)
        self.status_label.setVisible(False)

        IPvalidator = QRegExp(
            '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)'
            '{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
        self.ip_box.setValidator(QRegExpValidator(IPvalidator, self))
        self.ip_box.addItem('192.168.72.43')
        # for item in params.hosts: self.ip_box.addItem(item)

    def connect_event(self):
        ip = self.ip_box.currentText()
        #connection = Com.connectClient(ip)
        connection = True
        if connection:
            self.status_label.setText('Connected')

        elif not connection:
            self.status_label.setText('Not connected')
            self.btn_connect.setText('Retry')
            # self.help.setPixmap(self.conn_help)
            # self.help.setVisible(True)
        else:
            self.status_label.setText('Not connected with status: '+str(connection))
            self.btn_connect.setText('Retry')
            # self.help.setPixmap(self.conn_help)
            # self.help.setVisible(True)

        self.parent.status_connection.setChecked(connection)
        self.status_label.setVisible(True)

    def add_IP(self):

        ip = self.ip_box.currentText()
        """
        if not ip in params.hosts:
            self.ip_box.addItem(ip)
        else: return
        params.hosts = [self.ip_box.itemText(i) for i in range(self.ip_box.count())]
        """
        print(ip)

    def remove_IP(self):
        idx = self.ip_box.currentIndex()
        print(idx)
