"""
Acquisition Manager
@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    19/06/2020

@summary:   Class for controlling the acquisition

@status:    Under development
@todo:      Pre acquisition setup routine, implementation of GPA controller

"""

from PyQt5.QtCore import pyqtSlot
from manager.acquisitionmanager import AcquisitionManager
from plotview.exampleplot import ExamplePlot
from operationmodes import defaultoperations, serviceOperation
from operationsnamespace import Namespace as nmpsc
from PyQt5.QtCore import QObject
from server.communicationmanager import Com
from plotview import exampleplot
from manager.datamanager import DataManager as Data


class AcquisitionController(QObject):
    def __init__(self, parent=None, outputsection=None):
        super(AcquisitionController, self).__init__(parent)

        self.parent = parent
        self.outputsection = outputsection
        self.acquisitionData = None

        parent.action_acquire.triggered.connect(self.startAcquisition)

    """
    @pyqtSlot()
    def startAcquisition(self):

        self.parent.clearPlotLayout()

        data = AcquisitionManager().get_exampleFidData()
        plot = ExamplePlot(data.f_axis, data.f_fftMagnitude, "frequency", "signal intensity")

        outputvalues = {
            "SNR": round(data.get_snr(), 4),
            "FWHM [Hz]": round(data.get_fwhm()[1], 4),
            "FWHM [ppm]": round(data.get_fwhm()[2], 4),
            "Center Frequency [MHz]": round(data.get_peakparameters()[1], 4),
            "Signal Maximum [V]": round(data.get_peakparameters()[3], 4)
        }

        self.outputsection.set_parameters(outputvalues)

        # TODO: Type dependent acquisition and plot routine
        self.parent.plotview_layout.addWidget(plot)
    """

    @pyqtSlot(bool)
    def focusFrequency(self):
        if self.acquisitionData is not None:
            self.parent.clearPlotviewLayout()
            frequency = self.acquisitionData.get_peakparameters()[3]
            AcquisitionManager().reaquireFrequency(frequency)
            # [outputValues, plotView, dataObject] = AcquisitionManager().reaquireFrequency(frequency)
            # self.outputsection.set_parameters(outputValues)
            # self.parent.plotview_layout.addWidget(plotView)
            # self.acquisitionData = dataObject
        else:
            print("No acquisition performed.")

    @pyqtSlot(bool)
    def startAcquisition(self):

        _operation = defaultoperations['Example FID Spectrum'].systemproperties
        _frequency = _operation.systemproperties[nmpsc.frequency]
        _tmp_pack = Com.constructSequencePacket(_operation)
        _tmp_data = Com.sendPacket(_tmp_pack)

        self.parent.clearPlotviewLayout()

        _dataobject: Data = Data(_tmp_data, _frequency)
        _plotview = ExamplePlot(_dataobject.f_axis, _dataobject.f_fftMagnitude, "frequency", "signal intensity")
        _outputvalues = self.getOutputParameterObject(_dataobject, _operation.systemproperties)

        self.outputsection.set_parameters(_outputvalues)
        self.parent.plotview_layout.addWidget(_plotview)
        self.acquisitionData = _dataobject

        print("Operation: \n {}".format(_operation))

    # TODO: Startup routine (set frequency, set attenuation, set shim, upload sequence, etc. )
