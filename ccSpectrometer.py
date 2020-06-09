"""
Spectrometer Controlcenter

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0
@change:    11/05/2020

@summary:   Class of the spectrometer sub application.

@status:    Under development/testing
@todo:      Connect plotview class, store UI through QSettings package, implementation of logger

"""

import csv
from PyQt5.QtWidgets import QFileDialog
from PyQt5.uic import loadUiType
from PyQt5.QtCore import pyqtSignal, QStandardPaths
import numpy as np
import warnings
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from parameters import params
from manager.datamanager import DataManager as Data
from manager.sequencemanager import SqncMngr
from manager.acquisitionmanager import AcquisitionManager
from server.communicationmanager import Com
from globalvars import sqncs, grads
from dataLogger import logger

CC_Spec_Form, CC_Spec_Base = loadUiType('ui/ccSpectrometer.ui')

class CCSpecWidget(CC_Spec_Base, CC_Spec_Form):
    """
    Controlcenter spectrometer widget class
    """
    call_update = pyqtSignal()
    acquiredData: Data

    def __init__(self):
        super(CCSpecWidget, self).__init__()
        self.setupUi(self)

        #SqncMngr.sequenceUploaded.connect(self.sequence_uploaded)

        self.acqmngr = AcquisitionManager()

        SqncMngr.packSequence(sqncs.FID)

        self.initUI()

        self.fig = Figure()
        self.fig.set_facecolor("None")
        self.ax1 = self.fig.add_subplot(3, 1, 1)
        self.ax2 = self.fig.add_subplot(3, 1, 2)
        self.ax3 = self.fig.add_subplot(3, 1, 3)
        self.fig_canvas = FigureCanvas(self.fig)

        self.switchPlot(0)
        self.setSequence(0)

    def initUI(self):

        self.load_params()
        # Sequence selector
        self.seq_selector.addItems(
            [sqncs.FID.str, sqncs.SE.str, sqncs.IR.str, sqncs.SIR.str, "Custom Sequence"])
        # Manual manager toolbox
        self.uploadSeq_btn.clicked.connect(self.uploadSequence)
        self.uploadSeq_confirm.setEnabled(False)
        self.manualFreq_input.setKeyboardTracking(False)
        self.manualAt_input.setKeyboardTracking(False)
        self.manualFreq_input.valueChanged.connect(Com.setFrequency)  # (self.data.set_freq)
        self.manualAt_input.valueChanged.connect(Com.setAttenuation)  # (self.data.set_at)
        self.manualAcquire_btn.clicked.connect(self.onAcquisitionStarted)
        self.manualCenter_btn.clicked.connect(self.setCenterFrequency)
        self.manualAvg_input.setEnabled(False)
        self.manualAvg_enable.clicked.connect(self.manualAvg_input.setEnabled)
        self.manualTE_input.setKeyboardTracking(False)
        self.manualTE_input.valueChanged.connect(SqncMngr.setSpinEcho)  # (self.data.set_SE)
        self.manualTE_input.setVisible(False)
        self.manualTELabel.setVisible(False)
        self.manualTI_input.setKeyboardTracking(False)
        self.manualTI_input.setVisible(False)
        self.manualTILabel.setVisible(False)
        # Autocenter tool
        self.autoCenter_btn.clicked.connect(self.onAcquisitionStarted)
        self.autoCenter_save_btn.clicked.connect(self.save_autocenter)
        self.autoCenter_save_btn.setEnabled(False)
        # Flipangle tool
        self.flipangle_btn.clicked.connect(self.onAcquisitionStarted)
        self.flipangle_save_btn.clicked.connect(self.save_flipangle)
        self.flipangle_save_btn.setEnabled(False)
        # Shim tool
        self.setOffset_btn.clicked.connect(self.setGradientOffsets)

        self.toolBox.setCurrentIndex(0)
        self.seq_selector.setCurrentIndex(0)
        self.toolBox.currentChanged.connect(self.switchPlot)
        self.seq_selector.currentIndexChanged.connect(self.setSequence)

    # _______________________________________________________________________________
    #   Control Toolbox: Switch views depending on toolbox

    def switchPlot(self, idx):
        self.fig.clear()

        print("Current Index: {}".format(idx))

        if idx is 0:
            self.ax1 = self.fig.add_subplot(2, 1, 1)
            self.ax2 = self.fig.add_subplot(2, 1, 2)
            self.progressBar_container.setVisible(False)
        elif idx is 3:
            self.ax1 = self.fig.add_subplot(2, 1, 1)
            self.ax2 = self.fig.add_subplot(2, 1, 2)
            self.progressBar_container.setVisible(True)
        else:
            self.ax1 = self.fig.add_subplot(3, 1, 1)
            self.ax2 = self.fig.add_subplot(3, 1, 2)
            self.ax3 = self.fig.add_subplot(3, 1, 3)
            self.progressBar_container.setVisible(True)

        self.load_params()
        self.fig_canvas.draw()
        self.call_update.emit()

    def setSequence(self, idx) -> None:
        """
        Set sequence from drop down menu
        @param idx:     Selected index from drop down menu
        @return:        None
        """
        self.manualTI_input.setVisible(False)
        self.manualTILabel.setVisible(False)
        self.manualTE_input.setVisible(False)
        self.manualTELabel.setVisible(False)
        self.uploadSeq_btn.setVisible(False)
        self.uploadSeq_confirm.setVisible(False)

        if idx is 0:  # Free induction decay
            SqncMngr.packSequence(sqncs.FID)
        elif idx is 1:  # Spin echo
            self.manualTE_input.setVisible(True)
            self.manualTELabel.setVisible(True)
            SqncMngr.packSequence(sqncs.SE)
        elif idx is 2 or idx is 3:  # IR or SIR
            self.manualTI_input.setVisible(True)
            self.manualTILabel.setVisible(True)
            if idx is 2:  # Inversion recovery
                self.manualTI_input.disconnect()
                self.manualTI_input.valueChanged.connect(SqncMngr.setInversionRecovery)
                SqncMngr.packSequence(sqncs.IR)
            else:  # Saturation inversion recovery
                self.manualTI_input.disconnect()
                self.manualTI_input.valueChanged.connect(SqncMngr.setSaturationInversionRecovery)
                SqncMngr.packSequence(sqncs.SIR)
        else:  # Custom sequence
            self.uploadSeq_btn.setVisible(True)
            self.uploadSeq_confirm.setVisible(True)
            self.uploadSeq_confirm.setChecked(False)
            self.disable_controls()

    def uploadSequence(self) -> None:
        """
        Upload sequence from file dialog
        @return:    None
        """
        print("Upload Sequence")
        sequence = QFileDialog.getOpenFileName(self, 'Upload Custom Sequence',
                                               QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),
                                               'Textfile (*.txt)')
        status = SqncMngr.packSequence(sequence[0])
        if status is True:
            self.uploadSeq_confirm.setChecked(True)
        self.enable_controls()

    def setGradientOffsets(self) -> None:
        """
        Set gradient offset values in parameters and on console
        @return:    None
        """
        params.grad[0] = self.xOffset_input.value()
        params.grad[1] = self.yOffset_input.value()
        params.grad[2] = self.zOffset_input.value()
        params.grad[3] = self.z2Offset_input.value()

        Com.setGradients(params.grad[0], params.grad[1], params.grad[2], params.grad[3])

        # self.data.set_gradients(params.grad[0], params.grad[1], params.grad[2], params.grad[3])
        # self.data.acquire

    def onAcquisitionStarted(self) -> None:

        idx = self.toolBox.currentIndex()

        if idx is 0:    # Spectrum
            if self.manualAvg_enable is True:
                fValues = [params.freq] * self.manualAvg_input
                self.measureSpectrum(list(fValues), 10)
            else:
                self.measureSpectrum([params.freq], 10)
        elif idx is 1:  # Calibration
            self.findLarmorFrequency(params.freq)
        elif idx is 2:  # Transmit Adjust
            atValues = np.linspace(self.atStart_input, self.atEnd_input, self.atSteps_input, endpoint=True)
            self.transmitAdjust(params.freq, atValues)
        elif idx is 3:  # Gradient currents
            self.setGradientOffsets()
        else:
            print("Error: Toolbox index out of scope.")

    def measureSpectrum(self, frequency: list, sampletime: int = 10) -> None:
        """
        Measure spectrum for a list of frequencies
        @param frequency:       List of frequencies/frequency value for TX
        @param sampletime:      RX sample time
        @return:                None
        """
        self.disable_controls()
        self.ax3.clear()

        for fValue in frequency:
            #   [data, _] = self.acqmngr.get_spectrum(fValue, sampletime)
            data = self.acqmngr.get_exampleFidData()    # reads an example dataset

            [_, tPeak, _, fCenter] = data.get_peakparameters()
            snr = data.get_snr()
            [_, fwhmHZ, fwhmPPM] = data.get_fwhm(10)

            self.set_output(fValue, params.at, fCenter, tPeak, [fwhmHZ, fwhmPPM], snr)
            self.twoAxPlot(data, [-30000, 30000])

        self.enable_controls()
        self.acquiredData = data

    def transmitAdjust(self, fValue: float, attenuation: list) -> None:
        """
        Transmit adjust to calibrate TX power
        @param fValue:          TX frequency value
        @param attenuation:     List of attenuation values
        @return:                None
        """
        self.disable_controls()
        self.ax3.clear()

        for atValue in attenuation:
            Com.setAttenuation(atValue)
            Com.waitForTransmission()

            [data, _] = self.acqmngr.get_spectrum(fValue)
            [fPeakValue, tSignalValue, _, fCenter] = data.get_peakparameters()

            self.set_output(fValue, params.at, fCenter, fPeakValue, 0, 0)
            atData = {"attenuation [dB]": params.at, "signal maximum": tSignalValue}
            self.threeAxPlot(data, atData)

        self.acquiredData = data
        self.atPeak_output.setText(str(round(np.max(self.at_results), 2)))
        self.atMax_output.setText(str(round(self.at_values[np.argmax(self.at_results)], 2)))
        self.manualAt_input.setValue(self.at_values[np.argmax(self.at_results)])
        self.enable_controls()

    def findLarmorFrequency(self, fValue: float):
        print("Find Larmor frequency around {}".format(fValue))

    def setCenterFrequency(self) -> None:
        """
        Get and set real Larmor frequency, when data is available (requires previous acquisition)
        @return:    None
        """
        if self.acquiredData.f_fftMagnitude.size is not 0:
            [_, _, _, center] = self.acquiredData.get_peakparameters()
            self.acquiredData = self.acqmngr.get_spectrum(center)

    def set_output(self, freq: float, at: float, center: float, peak: float, fwhm: list, snr: float) -> None:
        """
        Set output parameter text boxes
        @param freq:        Acquisition frequency
        @param at:          Attenuation of acquisition
        @param center:      Real center frequency, corresponds to Larmor frequency
        @param peak:        Signal maximum in time domain
        @param fwhm:        Full width at half maximum
        @param snr:         Signal-to-noise ratio
        @return:            None
        """

        fwhmStr = "{} ({})".format(round(fwhm[0], 2), (fwhm[1], 4))

        self.freq_output.setText(str(round(freq, 5)))
        self.at_output.setText(str(round(at, 2)))
        self.center_output.setText(str(round(center, 5)))
        self.peak_output.setText(str(round(peak, 2)))
        self.fwhm_output.setText(fwhmStr)
        self.snr_output.setText(str(round(snr, 2)))

    def update_params(self):
        # Get params
        params.freq = self.manualFreq_input.value()
        params.at = self.manualAt_input.value()
        params.avgCyc = self.manualAvg_input.value()
        params.te = self.manualTE_input.value()
        params.ti = self.manualTI_input.value()
        params.autoSpan = self.freqSpan_input.value()
        params.autoStep = self.freqSteps_input.value()
        params.autoTimeout = self.freqTimeout_input.value()
        params.flipStart = self.atStart_input.value()
        params.flipEnd = self.atEnd_input.value()
        params.flipStep = self.atSteps_input.value()
        params.flipTimeout = self.atTimeout_input.value()

    def load_params(self):
        # Set params to GUI elements
        self.manualFreq_input.setValue(params.freq)
        self.manualAt_input.setValue(params.at)
        self.manualAvg_input.setValue(params.avgCyc)
        self.manualTE_input.setValue(params.te)
        self.manualTI_input.setValue(params.ti)
        self.freqCenter_input.setValue(params.freq)
        self.freqSpan_input.setValue(params.autoSpan)
        self.freqSteps_input.setValue(params.autoStep)
        self.freqTimeout_input.setValue(params.autoTimeout)
        self.atStart_input.setValue(params.flipStart)
        self.atEnd_input.setValue(params.flipEnd)
        self.atSteps_input.setValue(params.flipStep)
        self.atTimeout_input.setValue(params.flipTimeout)
        self.xOffset_input.setValue(params.grad[0])
        self.yOffset_input.setValue(params.grad[1])
        self.zOffset_input.setValue(params.grad[2])
        self.z2Offset_input.setValue(params.grad[3])

    # _______________________________________________________________________________
    #   Plotting Data

    def twoAxPlot(self, data: Data, fRange: list):

        idx0 = int(len(data.f_axis)/2)
        idxMin = (np.abs(data.f_axis[0:idx0-5] - fRange[0])).argmin()
        idxMax = (np.abs(data.f_axis[idx0+5:-1] - fRange[1])).argmin() + idx0

        self.ax1.clear()
        self.ax1.plot(data.f_axis[idxMin:idxMax], data.f_fftMagnitude[idxMin:idxMax] / max(data.f_fftMagnitude))
        self.ax2.clear()
        self.ax2.plot(data.t_axis, data.t_magnitude, label='Magnitude')
        self.ax2.plot(data.t_axis, data.t_real, label='Real Part')
        self.ax2.plot(data.t_axis, data.t_imag, label='Imaginary Part')
        self.ax1.set_ylabel('relative frequency spectrum')
        self.ax1.set_xlabel('frequency [Hz]')
        self.ax2.set_ylabel('RX signal [mV]')
        self.ax2.set_xlabel('time [ms]')
        self.ax2.legend()
        self.fig_canvas.draw()

        self.call_update.emit()

    def threeAxPlot(self, data: Data, thirdAxisData: dict):
        self.twoAxPlot(data)

        self.ax3.plot(list(thirdAxisData.values())[0], list(thirdAxisData.values())[1], 'x', color='#33A4DF')
        self.ax3.set_xlabel(list(thirdAxisData.keys())[0])
        self.ax3.set_ylabel(list(thirdAxisData.keys())[1])

    # _______________________________________________________________________________
    #   Save Data

    def save_flipangle(self):
        path = QFileDialog.getSaveFileName(self, 'Save Flipangle Data',
                                           QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),
                                           'csv (*.csv)')
        if not path[0] == '':
            with open(path[0], mode='w', newline='') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(['Flipangletool Data', params.dataTimestamp])
                writer.writerow([''])
                writer.writerow(['attenuation [dB]', 'fft peak magnitude'])
                for n in range(len(self.at_values)):
                    writer.writerow([self.at_values[n], self.at_results[n]])
            print("\nFlipangledata saved.")

    def save_autocenter(self):
        path = QFileDialog.getSaveFileName(self, 'Save Flipangle Data',
                                           QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),
                                           'csv (*.csv)')
        if not path[0] == '':
            with open(path[0], mode='w', newline='') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(['Autocenter Data', params.dataTimestamp])
                writer.writerow([''])
                writer.writerow(['frequency [MHz]', 'fft peak magnitude'])
                for n in range(len(self.freqSpace)):
                    writer.writerow([round(self.freqSpace[n], 5), self.peaks[n]])
            print("\nAutosavedata saved.")

    # _______________________________________________________________________________
    #   Functions to Disable and enable control elements like buttons, spinboxes, etc.

    def disable_controls(self):  # Function that disables controls
        self.manualAcqWidget.setEnabled(False)
        self.findCenterWidget.setEnabled(False)
        self.flipangleWidget.setEnabled(False)
        self.shimmingWidget.setEnabled(False)

    def enable_controls(self):  # Function that enables controls
        self.manualAcqWidget.setEnabled(True)
        self.findCenterWidget.setEnabled(True)
        self.flipangleWidget.setEnabled(True)
        self.shimmingWidget.setEnabled(True)
