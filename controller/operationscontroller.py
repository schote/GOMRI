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
        """
        Initialization
        @param parent:  Mainviewcontroller (access to parameter layout)
        """
        super(OperationsList, self).__init__(parent)

        # Add operations to operations list
        self.addItems(list(operations.keys()))
        self.itemClicked.connect(self.set_parameters)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Make parent reachable from outside __init__
        self.parent = parent

    def set_parameters(self, op: dict):
        """
        Set input parameters from operation object
        @param op:  Operation object
        @return:    None
        """
        # Reset row layout for input parameters
        for i in reversed(range(self.parent.layout_parameters.count())):
            self.parent.layout_parameters.itemAt(i).widget().setParent(None)

        # Add input parameters to row layout
        properties = operations[op.text()].properties
        items = self.get_items(properties)

        for item in items:
            self.parent.layout_parameters.addWidget(item)

    def get_items(self, struct: dict = None) -> list:
        itemlist: list = []
        for key in list(struct.keys()):
            if type(struct[key]) == dict:
                itemlist.append(self.get_labelitem(key))
                itemlist += self.get_items(struct[key])
            else:
                item = OperationParameter(key, struct[key])
                itemlist.append(item)

        return itemlist

    @staticmethod
    def get_labelitem(text):
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
        self.input_value.textChanged.connect(self.get_value)

    def get_value(self) -> None:
        print("{}: {}".format(self.label_name.text(), self.input_value.text()))

    def set_value(self, value: int) -> None:
        self.input_value.setText(str(value))
