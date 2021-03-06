"""
Startup Code

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    13/06/2020

@summary:   TBD

@status:    Under development
@todo:

"""
import sys
from PyQt5.QtWidgets import QApplication
from controller.mainviewcontroller import MainViewController

VERSION = "0.1.0"
AUTHOR = "David Schote"

if __name__ == '__main__':
    print("Graphical User Interface for Magnetic Resonance Imaging {} by {}".format(VERSION, AUTHOR))
    app = QApplication(sys.argv)
    gui = MainViewController()
    gui.show()
    sys.exit(app.exec_())

"""
import sys
import csv

# import PyQt5 packages
from PyQt5.QtWidgets import QMessageBox, QApplication, QFileDialog
from PyQt5.uic import loadUiType, loadUi
from PyQt5.QtCore import QRegExp, pyqtSignal, QStandardPaths
from PyQt5.QtGui import QRegExpValidator, QPixmap
import matplotlib.pyplot as plt

from ccSpectrometer import CCSpecWidget
from ccT2Relaxometer import CCRelaxT2Widget
from ccT1Relaxometer import CCRelaxT1Widget
from protocol import ProtocolWidget
from cc2DImaging import CC2DImagWidget

from parameters import params
from manager.acquisitionmanager import AcquisitionManager as AcqMngr
from dataLogger import logger

from server.communicationmanager import Com

plt.rc('axes', prop_cycle=params.cycler)
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['axes.grid'] = True
plt.rcParams['figure.autolayout'] = True
plt.rcParams['figure.dpi'] = 75
plt.rcParams['legend.loc'] = "upper right"

Main_Window_Form, Main_Window_Base = loadUiType('ui/mainwindow.ui')
Conn_Dialog_Form, Conn_Dialog_Base = loadUiType('ui/connDialog.ui')

class MainWindow(Main_Window_Base, Main_Window_Form):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # Setup
        self.ui = loadUi('ui/mainwindow.ui')
        self.setWindowTitle('Relax')
        self.setStyleSheet(params.stylesheet)

        #self.plotTabWidget.setStyleSheet("border: 0.5px solid #BAB9B8; ")

        # Load GUI parameter
        params.loadParam()
        params.dispVars()

        #self.data = data()

        # Establish connection
        #self.establish_conn()

        ## Skip connection to server for development
        params.ip = 0; self.start_com()

#_______________________________________________________________________________
#   Establish connection to server and start communication

    def establish_conn(self):
        self.dialog = ConnectionDialog(self)
        self.dialog.show()
        self.dialog.connected.connect(self.start_com)

    def start_com(self):
        # Set default view
        self.plotTabWidget.setCurrentIndex(0)
        self.plotTabWidget.currentChanged.connect(self.switchView)
        self.switchView()

        self.action_exportData.triggered.connect(self.save_data_csv)
        self.action_saveFig.triggered.connect(self.save_figure)
        self.action_saveLog.triggered.connect(self.save_log)
        self.action_clearLog.triggered.connect(self.clear_log)

        logger.init()

#_______________________________________________________________________________
#   Setup Main Window

    def switchView(self):
        try: self.action_exportData.setEnabled(True)
        except: pass
        try: self.updateGUIsignal.disconnect
        except: print("Could not disconnect update gui signal.")
        try: self.environment.update_params
        except: print("Could not update params.")
        try: AcqMngr.readoutFinished.disconnect#self.environment.data.readout_finished.disconnect
        except: print("Could not disconnect finished readout signal.")

        params.saveFile()
        #self.resetLayout(self.ccLayout)

        self.idx = self.plotTabWidget.currentIndex()
        views = {
            0: self.setupSpectrometer,
            1: self.setupT1Relaxometer,
            2: self.setupT2Relaxometer,
            3: self.setupProtocol,
            4: self.setup2DImag
        }
        views[self.idx]()

        try: self.updateGUIsignal.connect(self.update_gui)
        except: pass

    def resetLayout(self, layout):
        for i in range(layout.count()):
            layout.itemAt(0).widget().close()
            layout.takeAt(0)

    def setupSpectrometer(self):
        print("\n---Spectrometer---\n")

        self.resetLayout(self.spectrometerLayout)
        self.environment = CCSpecWidget()
        self.updateGUIsignal = self.environment.call_update

        self.spectrometerLayout.addWidget(self.environment.fig_canvas)
        #self.ccLayout.addWidget(self.environment)
        self.ccScroll.setWidget(self.environment)

    def setupT1Relaxometer(self):
        print("\n---T1 Relaxometer---\n")

        self.resetLayout(self.T1relaxLayout)
        self.environment = CCRelaxT1Widget()
        self.updateGUIsignal = self.environment.call_update

        self.T1relaxLayout.addWidget(self.environment.fig_canvas)
        #self.ccLayout.addWidget(self.environment)
        self.ccScroll.setWidget(self.environment)

    def setupT2Relaxometer(self):
        print("\n---T2 Relaxometer---\n")

        self.resetLayout(self.T2relaxLayout)
        self.environment = CCRelaxT2Widget()
        self.updateGUIsignal = self.environment.call_update

        self.T2relaxLayout.addWidget(self.environment.fig_canvas)
        #self.ccLayout.addWidget(self.environment)
        self.ccScroll.setWidget(self.environment)

    def setupProtocol(self):
        print("\n---Measurement Protocol---\n")

        self.action_exportData.setEnabled(False)

        self.resetLayout(self.protocolLayout)
        self.resetLayout(self.protocolPlotLayout)

        self.protocol_env = ProtocolWidget()
        self.environment = self.protocol_env.protocolCC
        self.updateGUIsignal = self.protocol_env.call_update

        self.protocolLayout.addWidget(self.protocol_env)
        self.protocolPlotLayout.addWidget(self.environment.fig_canvas)
        #self.ccLayout.addWidget(self.environment)
        self.ccScroll.setWidget(self.environment)

    def setup2DImag(self):
        print("\n---2D Imaging---\n")

        self.resetLayout(self.imagingLayout)
        self.environment = CC2DImagWidget()
        self.updateGUIsignal = self.environment.call_update

        #self.imagingLayout.addWidget(self.environment.fig_canvas)
        #self.imagingLayout.addWidget(self.environment.mdi)
        self.imagingLayout.addWidget(self.environment.tabview)
        #self.ccLayout.addWidget(self.environment)
        self.ccScroll.setWidget(self.environment)

    def update_gui(self):

        #while QApplication.hasPendingEvents():
        QApplication.processEvents()
        #self.centralwidget.update()

    def closeEvent(self, event):
        params.saveFile()
        choice = QMessageBox.question(self, 'Close Relaxo', 'Are you sure that you want to quit Relax?',\
            QMessageBox.Cancel | QMessageBox.Close, QMessageBox.Cancel)

        if choice == QMessageBox.Close:
            params.dispVars()
            #self.data.disconn_client()
            server.disconnect()
            event.accept()
        else: event.ignore()

#_______________________________________________________________________________
#   Save-functions (data, settings, log)

    def save_data_csv(self):
        path = QFileDialog.getSaveFileName(self, 'Save Acquisitiondata', QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation), 'csv (*.csv)')
        if not path[0] == '':
            tab_idx = self.plotTabWidget.currentIndex()
            if tab_idx == 2 or tab_idx == 1:
                try: self.environment.saveData(path[0])
                except: return
            elif tab_idx == 4:
                try: self.environment.saveData(path[0])
                except: return
            else:
                with open(path[0], mode='w', newline='') as file:
                    writer = csv.writer(file, delimiter=',')
                    writer.writerow([params.dataTimestamp])
                    writer.writerow(['Center frequency', params.freq])
                    writer.writerow([''])
                    writer.writerow(['freq', 'cplx data','fft centered'])
                    for n in range(len(params.freqaxis)):
                        writer.writerow([params.freqaxis[n], params.data[n], params.fft[n]])
            print("\nAcquisitiondata saved.")

    def save_figure(self):
        path = QFileDialog.getSaveFileName(self, 'Save Figure',\
            QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),\
            "JPEG Image (*.jpg);;PNG Image (*.png);;PDF Format (*.pdf)")
        if not path[0] == '':
            self.environment.fig.savefig(path[0], dpi=600, orientation='portrait', papertype=None, format=None, transparent=True,\
                bbox_inches=None, pad_inches=0.1, frameon=None, metadata=None)
            print("\nFigure saved.")

    def save_log(self):
        path = QFileDialog.getSaveFileName(self, 'Save Logfile', QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation), 'Textfile (*.txt)')
        if not path[0] == '':
            file = open(path[0], 'w')
            for line in logger.log:
                file.write(str(line))
            file.close()
            print("\nLogfile saved.")

    def clear_log(self):
        logger.init()
        print("\nLog cleared.")

#_______________________________________________________________________________
#   Connection Dialog/Popup

class ConnectionDialog(Conn_Dialog_Base, Conn_Dialog_Form):

    connected = pyqtSignal()

    def __init__(self, parent=None):
        super(ConnectionDialog, self).__init__(parent)
        

        # setup closeEvent
        self.ui = loadUi('ui/connDialog.ui')
        self.ui.closeEvent = self.closeEvent
        self.conn_help = QPixmap('ui/connection_help.png')
        self.help.setVisible(False)

        # connect interface signals
        self.conn_btn.clicked.connect(self.connect_event)
        self.addIP_btn.clicked.connect(self.add_IP)
        self.rmIP_btn.clicked.connect(self.remove_IP)
        self.status_label.setVisible(False)

        IPvalidator = QRegExp(
            '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)'
            '{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
        self.ip_box.setValidator(QRegExpValidator(IPvalidator, self))
        for item in params.hosts: self.ip_box.addItem(item)

        self.mainwindow = parent

    def connect_event(self):
        params.ip = self.ip_box.currentText()
        print(params.ip)
        params.saveFile()

        connection = Com.connectClient(params.ip) #self.data.conn_client(params.ip)

        if connection:
            self.status_label.setText('Connected.')
            self.connected.emit()
            #self.data.set_at(params.at)
            #self.data.set_freq(params.freq)
            #self.data.set_gradients(params.grad[0], params.grad[1], params.grad[2], params.grad[3])
            Com.setFrequency(params.freq)
            Com.setAttenuation(params.at)
            Com.setGradients(params.grad[0], params.grad[1], params.grad[2], params.grad[3])
            self.mainwindow.show()
            self.close()

        elif not connection:
            self.status_label.setText('Not connected.')
            self.conn_btn.setText('Retry')
            self.help.setPixmap(self.conn_help)
            self.help.setVisible(True)
        else:
            self.status_label.setText('Not connected with status: '+str(connection))
            self.conn_btn.setText('Retry')
            self.help.setPixmap(self.conn_help)
            self.help.setVisible(True)

        self.status_label.setVisible(True)

    def add_IP(self):
        print("Add ip address.")
        ip = self.ip_box.currentText()

        if not ip in params.hosts: self.ip_box.addItem(ip)
        else: return

        params.hosts = [self.ip_box.itemText(i) for i in range(self.ip_box.count())]
        print(params.hosts)

    def remove_IP(self):
        idx = self.ip_box.currentIndex()
        try:
            del params.hosts[idx]
            self.ip_box.removeItem(idx)
        except: pass
        print(params.hosts)

#_______________________________________________________________________________
#   Run Application

def run():

    print("\n________________________________________________________\n",\
    "Graphical user interface for relaxometry and spectroscopy. \n",\
    "Programmed by David Schote, OvGU Magdeburg, 2019\n",\
    "Stable build version 1.0.0",\
    "\n________________________________________________________\n")

    app = QApplication(sys.argv)
    gui = MainWindow()

    ## Skip connection to server for development
    gui.show()

    sys.exit(app.exec_())

#_______________________________________________________________________________
#   Main Function

if __name__ == '__main__':
    run()
"""
