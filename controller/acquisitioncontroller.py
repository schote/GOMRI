"""
Acquisition Manager
@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    19/06/2020

@summary:   Class for controlling the acquisition

@status:    Under development
@todo:      Subdivide "startAcquisition" routine into subroutines (modularity)

"""

import numpy as np
from PyQt5.QtCore import pyqtSlot
from manager.acquisitionmanager import AcquisitionManager
from plotview.spectrumplot import SpectrumPlot
from operationmodes import defaultoperations
from operationsnamespace import Namespace as nmpsc
from PyQt5.QtCore import QObject
from server.communicationmanager import Com, Commands
from manager.datamanager import DataManager

version_major = 0
version_minor = 0
version_debug = 8
version_full = (version_major << 16) | (version_minor << 8) | version_debug


class AcquisitionController(QObject):
    def __init__(self, parent=None, outputsection=None, operationlist=None):
        super(AcquisitionController, self).__init__(parent)

        self.parent = parent
        self.outputsection = outputsection
        self.operationlist = operationlist
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

    # TODO: Implementation of "reacquire" command with different frequency
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
    """

    @pyqtSlot(bool)
    def startAcquisition(self):

        self.parent.clearPlotviewLayout()
        operation = defaultoperations[self.operationlist.getCurrentOperation()]
        frequency = operation.systemproperties[nmpsc.frequency][0]
        packetIdx: int = 0
        command: int = 0    # 0 equals request a packet
        assert version_major < 256 and version_minor < 256 and version_debug < 256, "Version is too high for a byte!"
        version = (version_major << 16) | (version_minor << 8) | version_major

        # Get/construct package to be send
        tmp_sequence_pack = Com.constructSequencePacket(operation)
        tmp_property_pack = Com.constructPropertyPacket(operation)
        tmp_package = {**tmp_sequence_pack, **tmp_sequence_pack, **tmp_property_pack}
        fields = [command, packetIdx, 0, version, tmp_package]

        response = Com.sendPacket(fields)
        if response is None:
            print("Nothing received.")
            return

        tmp_data = np.frombuffer(response[4]['acq'], np.complex64)

        # print("Data: {}".format(tmp_data))
        print("Size of received data: {}".format(len(tmp_data)))

        dataobject: DataManager = DataManager(tmp_data, frequency, len(tmp_data))
        f_plotview = SpectrumPlot(dataobject.f_axis, dataobject.f_fftMagnitude, "frequency", "signal intensity")
        t_plotview = SpectrumPlot(dataobject.t_axis, dataobject.t_magnitude, "time", "signal intensity")
        outputvalues = AcquisitionManager().getOutputParameterObject(dataobject, operation.systemproperties)

        self.outputsection.set_parameters(outputvalues)
        self.parent.plotview_layout.addWidget(f_plotview)
        self.parent.plotview_layout.addWidget(t_plotview)
        self.acquisitionData = dataobject

        print("Operation: \n {}".format(operation))


# TODO: Startup routine (set frequency, set attenuation, set shim, upload sequence, etc. )
