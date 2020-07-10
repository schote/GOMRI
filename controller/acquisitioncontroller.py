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

        self.parent.clearPlotviewLayout()

        op = defaultoperations['Example FID Spectrum'].systemproperties
        [outputValues, plotView, dataObject] = AcquisitionManager().get_exampleFidData(op)
        # [output, plot] = AcquisitionManager().get_spectrum(op[nmspc.systemproperties],
        #                                                           op[nmspc.shim])
        self.outputsection.set_parameters(outputValues)
        self.parent.plotview_layout.addWidget(plotView)
        self.acquisitionData = dataObject

        print("Operation: \n {}".format(op))

    # TODO: Startup routine (set frequency, set attenuation, set shim, upload sequence, etc. )
