"""
Acquisition Manager

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    19/06/2020

@summary:   Class for controlling the acquisition

@status:    Under development
@todo:      Pre acquisition setup, implementation of GPA controller

"""

from PyQt5.QtCore import pyqtSlot
from manager.acquisitionmanager import AcquisitionManager
from plotview.exampleplot import ExamplePlot
from PyQt5.QtCore import QObject


class AcquisitionController(QObject):
    def __init__(self, parent=None, outputsection=None):
        super(AcquisitionController, self).__init__(parent)

        self.parent = parent
        self.outputsection = outputsection

        parent.action_acquire.triggered.connect(self.startAcquisition)

        # TODO: Implementation of GPA controller widget

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

        self.outputsection.setParameters(outputvalues)

        # TODO: Type dependent acquisition and plot routine
        self.parent.plotview_layout.addWidget(plot)





    # TODO: Startup routine (set frequency, set attenuation, set shim, upload sequence, etc. )
