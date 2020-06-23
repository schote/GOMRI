"""
Main View Controller

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    13/06/2020

@summary:   TBD

@status:    Under development
@todo:

"""

from PyQt5.uic import loadUiType, loadUi

# Example Plot
# from plotview.exampleplot import ExamplePlot
from PyQt5.QtCore import QFile, QTextStream
from manager.acquisitionmanager import AcquisitionManager
from controller.acquisitioncontroller import AcquisitionController

from controller.operationscontroller import OperationsList
from controller.connectiondialog import ConnectionDialog
from controller.outputparametercontroller import Output

from globalvars import StyleSheets as style
from server.communicationmanager import Com

MainWindow_Form, MainWindow_Base = loadUiType('view/mainview.ui')


class MainViewController(MainWindow_Base, MainWindow_Form):
    """
    MainViewController Class
    """
    def __init__(self):
        super(MainViewController, self).__init__()

        self.setupUi(self)
        self.ui = loadUi('view/mainview.ui')
        self.set_stylesheet(style.breezeDark)

        # Connection dialog
        self.action_connect.triggered.connect(self.show_connectiondialog)
        self.status_connection.setEnabled(False)

        # Initialisation of operation list
        oplist = OperationsList(self)
        self.layout_operations.addWidget(oplist)

        # Initialisation of output section
        outputsection = Output(self)

        # Initialisation of acquisition controller
        AcquisitionController(self, outputsection)

    def show_connectiondialog(self) -> None:
        """
        Opens connection dialog
        @return:    None
        """
        dialog = ConnectionDialog(self)
        dialog.show()

    def clear_plotlayout(self) -> None:
        """
        Clear the plot layout
        @return:    None
        """
        for i in reversed(range(self.plotview_layout.count())):
            self.plotview_layout.itemAt(i).widget().setParent(None)

    def set_stylesheet(self, style) -> None:
        file = QFile(style)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        stylesheet = stream.readAll()
        self.setStyleSheet(stylesheet)

    def closeEvent(self, event) -> None:
        """
        Overloaded close function
        @param event:   Close event
        @return:        None
        """
        # Disconnect server connection on closed before accepting the event
        Com.disconnectClient()
        event.accept()
