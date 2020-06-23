"""
Operations Controller

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    13/06/2020

@summary:   TBD

@status:    Under development
@todo:      Extend construction of parameter section (headers, more categories, etc. )

"""

from PyQt5.QtWidgets import QListWidget, QSizePolicy, QLabel
from PyQt5.QtCore import Qt
from operationmodes import operations
from PyQt5.uic import loadUiType

Parameter_Form, Parameter_Base = loadUiType('view/inputparameter.ui')


class OperationsList(QListWidget):
    """
    Operations List Class
    """

    def __init__(self, parent=None):
        super(OperationsList, self).__init__(parent)

        # Add operations to operations list
        self.addItems(list(operations.keys()))
        self.itemClicked.connect(self.setParameters)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Make parent reachable from outside __init__
        self.parent = parent

    def setParameters(self, op: dict):
        # Reset row layout for input parameters
        for i in reversed(range(self.parent.layout_parameters.count())):
            self.parent.layout_parameters.itemAt(i).widget().setParent(None)

        # Add input parameters to row layout
        self.parent.layout_parameters.addWidget(self.getLabelItem("System Properties"))
        properties = operations[op.text()].systemproperties
        items = self.getItems(properties)

        for item in items:
            self.parent.layout_parameters.addWidget(item)

    def getItems(self, struct: dict = None) -> list:
        itemList: list = []
        for key in list(struct.keys()):
            if type(struct[key]) == dict:
                itemList.append(self.getLabelItem(key))
                itemList += self.getItems(struct[key])
            else:
                item = OperationParameter(key, struct[key])
                itemList.append(item)

        return itemList

    @staticmethod
    def getLabelItem(text):
        label = QLabel()
        label.setText(text)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        return label


class OperationParameter(Parameter_Base, Parameter_Form):
    """
    Operation Parameter Widget-Class
    """

    def __init__(self, name, value):
        super(OperationParameter, self).__init__()
        self.setupUi(self)

        # Set input parameter's label and value
        self.label_name.setText(name)
        self.input_value.setText(str(value))
        # Connect text changed signal to getValue function
        self.input_value.textChanged.connect(self.getValue)

    def getValue(self) -> None:
        print("{}: {}".format(self.label_name.text(), self.input_value.text()))

    def setValue(self, value: int) -> None:
        self.input_value.setText(str(value))
