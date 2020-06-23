"""
Output Parameter Controller

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    13/06/2020

@summary:   TBD

@status:    Under development
@todo:

"""

from PyQt5.QtCore import QObject
from PyQt5.uic import loadUiType

Parameter_Form, Parameter_Base = loadUiType('view/outputparameter.ui')


class Output(QObject):
    """
    Output Class
    """

    def __init__(self, parent=None):
        super(Output, self).__init__(parent)

        # Make parent reachable from outside __init__
        self.parent = parent

    def setParameters(self, values: dict):
        # Reset grid layout for output parameter
        for i in reversed(range(self.parent.layout_outputgrid.count())):
            self.parent.layout_outputgrid.itemAt(i).widget().setParent(None)
        # Add values as output parameters to grid layout
        row = 0
        col = 0
        for parameter in list(values.keys()):
            if row > 2:
                col += 1
                row = 0
            item = OutputParameter(parameter, values[parameter])
            self.parent.layout_outputgrid.addWidget(item, row, col)
            row += 1



class OutputParameter(Parameter_Base, Parameter_Form):
    """
    Output Parameter Widget-Class
    """

    def __init__(self, name, value):
        super(OutputParameter, self).__init__()
        self.setupUi(self)

        # Set output parameter's label and value
        self.label_name.setText(name)
        self.output_value.setText(str(value))
        # Connect text changed signal to getValue function
        self.output_value.textChanged.connect(self.getValue)

    def getValue(self) -> None:
        print("{}: {}".format(self.label_name.text(), self.output_value.text()))

    def setValue(self, value: int) -> None:
        self.output_value.setText(str(value))
