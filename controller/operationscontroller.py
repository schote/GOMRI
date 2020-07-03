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
from operationmodes import defaultoperations
from operationsnamespace import Namespace as nmspc
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
        self.addItems(list(defaultoperations.keys()))
        self.itemClicked.connect(self.setParametersUI)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Make parent reachable from outside __init__
        self.parent = parent

    def setParametersUI(self, op: dict = None) -> None:
        """
        Set input parameters from operation object
        @param op:  Operation object
        @return:    None
        """
        operation = op.text()
        # Reset row layout for input parameters
        for i in reversed(range(self.parent.layout_parameters.count())):
            self.parent.layout_parameters.itemAt(i).widget().setParent(None)

        # Add input parameters to row layout
        inputwidgets: list = []

        if hasattr(defaultoperations[operation], 'systemproperties'):
            sys_prop = defaultoperations[operation].systemproperties
            inputwidgets += [self.generateLabelItem(nmspc.systemproperties)]
            inputwidgets += self.generateWidgetsFromDict(sys_prop, operation)

        if hasattr(defaultoperations[operation], 'gradientshims'):
            shims = defaultoperations[operation].gradientshims
            inputwidgets += [(self.generateLabelItem(nmspc.shim))]
            inputwidgets += (self.generateWidgetsFromDict(shims))

        for item in inputwidgets:
            self.parent.layout_parameters.addWidget(item)

    @staticmethod
    def generateWidgetsFromDict(obj: dict = None, operation: str = None) -> list:
        widgetlist: list = []
        for key in obj:
            widget = OperationParameter(key, obj[key], operation)
            widgetlist.append(widget)
        return widgetlist

    @staticmethod
    def generateLabelItem(text):
        label = QLabel()
        label.setText(text)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        return label

    def get_items(self, struct: dict = None) -> list:
        itemlist: list = []
        for key in list(struct.keys()):
            if type(struct[key]) == dict:
                itemlist.append(self.generateLabelItem(key))
                itemlist += self.get_items(struct[key])
            else:
                item = OperationParameter(key, struct[key])
                itemlist.append(item)

        return itemlist


class OperationParameter(Parameter_Base, Parameter_Form):
    """
    Operation Parameter Widget-Class
    """
    # Get reference to position in operation object
    def __init__(self, name, parameter, operation):
        super(OperationParameter, self).__init__()
        self.setupUi(self)

        # Set input parameter's label and value
        self.operation = operation
        self.parameter = parameter
        self.label_name.setText(name)
        self.input_value.setText(str(parameter[0]))
        # Connect text changed signal to getValue function
        self.input_value.textChanged.connect(self.get_value)

    def get_value(self) -> None:
        print("{}: {}".format(self.label_name.text(), self.input_value.text()))
        value: float = float(self.input_value.text())
        setattr(defaultoperations[self.operation], self.parameter[1], value)

    def set_value(self, value: int) -> None:
        self.input_value.setText(str(value))
