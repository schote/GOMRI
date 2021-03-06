"""
Main View Controller

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    13/06/2020

@summary:   TBD

@status:    Sets up the main view, its views and controllers
@todo:

"""



# Example Plot
# from plotview.exampleplot import ExamplePlot
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.uic import loadUiType, loadUi
from controller.acquisitioncontroller import AcquisitionController
from PyQt5.QtCore import pyqtSignal, pyqtSlot

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
    onOperationChanged = pyqtSignal(str)

    def __init__(self):
        super(MainViewController, self).__init__()
        self.ui = loadUi('view/mainview.ui')
        self.setupUi(self)
        self.styleSheet = style.breezeDark
        self.setupStylesheet(self.styleSheet)

        # Initialisation of operation list
        operationlist = OperationsList(self)
        operationlist.itemClicked.connect(self.operationChangedSlot)
        self.layout_operations.addWidget(operationlist)

        # Initialisation of output section
        outputsection = Output(self)

        # Initialisation of acquisition controller
        acqCtrl = AcquisitionController(self, outputsection, operationlist)

        connectiondialog = ConnectionDialog(self)

        # Toolbar Actions
        self.action_connect.triggered.connect(connectiondialog.show)
        self.action_changeappearance.triggered.connect(self.changeAppearanceSlot)
        # self.action_focusfrequency.triggered.connect(acqCtrl.focusFrequency)
        self.action_acquire.setEnabled(False)

    @pyqtSlot(QListWidgetItem)
    def operationChangedSlot(self, item: QListWidgetItem = None) -> None:
        """
        Operation changed slot function
        @param item:    Selected Operation Item
        @return:        None
        """
        operation = item.text()
        self.onOperationChanged.emit(operation)
        self.action_acquire.setEnabled(True)

    @pyqtSlot(bool)
    def connectionDialogSlot(self) -> None:
        """
        Opens connection dialog
        @return:    None
        """
        dialog = ConnectionDialog(self)
        dialog.show()

    def clearPlotviewLayout(self) -> None:
        """
        Clear the plot layout
        @return:    None
        """
        for i in reversed(range(self.plotview_layout.count())):
            self.plotview_layout.itemAt(i).widget().setParent(None)

    def setupStylesheet(self, style) -> None:
        """
        Setup application stylesheet
        @param style:   Stylesheet to be set
        @return:        None
        """
        self.styleSheet = style
        file = QFile(style)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        stylesheet = stream.readAll()
        self.setStyleSheet(stylesheet)

    @pyqtSlot(bool)
    def changeAppearanceSlot(self) -> None:
        """
        Slot function to switch application appearance
        @return:
        """
        if self.styleSheet is style.breezeDark:
            self.setupStylesheet(style.breezeLight)
        else:
            self.setupStylesheet(style.breezeDark)

    @staticmethod
    def closeEvent(event) -> None:
        """
        Overloaded close function
        @param event:   Close event
        @return:        None
        """
        # Disconnect server connection on closed before accepting the event
        Com.disconnectClient()
        event.accept()
