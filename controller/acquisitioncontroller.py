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

import msgpack
from PyQt5.QtCore import pyqtSlot
from manager.acquisitionmanager import AcquisitionManager
from plotview.exampleplot import ExamplePlot
from operationmodes import defaultoperations, serviceOperation
from operationsnamespace import Namespace as nmpsc
from PyQt5.QtCore import QObject
from server.communicationmanager import Com, Commands
from plotview import exampleplot
from manager.datamanager import DataManager as Data

version_major = 0
version_minor = 0
version_debug = 8
version_full = (version_major << 16) | (version_minor << 8) | version_debug


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

        operation = defaultoperations['Example FID Spectrum']
        frequency = operation.systemproperties[nmpsc.frequency]
        #tmp_sequence_pack = Com.constructSequencePacket(operation)
        tmp_property_pack = Com.constructPropertyPacket(operation)
        acquire_cmd = {Commands.runAcquisition: 5000}
        #t mp_pack = {**tmp_property_pack, **_tmp_sequence_pack, **_acquire}
        # tmp_pack = {**tmp_property_pack, **acquire_cmd}
        tmp_pack = {
            'lo_freq': self.lo_freq_bin,
            'rx_rate': self.rx_div_real,
            'tx_div': self.tx_div,
            'tx_size': self.tx_data.size * 4,
            'raw_tx_data': self.tx_bytes,
            'grad_mem_x': self.grad_x_bytes,
            'grad_mem_y': self.grad_y_bytes,
            'grad_mem_z': self.grad_z_bytes,
            'seq_data': self.instructions,
            'acq': self.samples }

        packetIdx: int = 0
        command: int = 0 # 0 equals request a packet
        assert version_major < 256 and version_minor < 256 and version_debug < 256, "Version is too high for a byte!"
        version = (version_major << 16) | (version_minor << 8) | version_major
        fields = [command, packetIdx, 0, version, tmp_pack]

        print("Fields to be send: {}".format(fields))

        self.parent.clearPlotviewLayout()
        print(msgpack.packb(fields))
        # tmp_data = Com.sendPacket(msgpack.packb(fields))
        """
        dataobject: Data = Data(tmp_data, frequency)
        plotview = ExamplePlot(dataobject.f_axis, dataobject.f_fftMagnitude, "frequency", "signal intensity")
        outputvalues = self.getOutputParameterObject(dataobject, operation.systemproperties)

        self.outputsection.set_parameters(outputvalues)
        self.parent.plotview_layout.addWidget(plotview)
        self.acquisitionData = dataobject

        print("Operation: \n {}".format(operation))
        """

# TODO: Startup routine (set frequency, set attenuation, set shim, upload sequence, etc. )
