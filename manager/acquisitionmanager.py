"""
Acquisition Manager

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   1.0
@change:    02/05/2020

@summary:   Class for managing the acquisition of spectrum, projection or image.

@status:    Under testing
@todo:      Generalize image acquisition manager

"""

from PyQt5.QtCore import QObject, pyqtSignal
from server.communicationmanager import CommunicationManager as Com
from manager.datamanager import DataManager as Data
from parameters import params
import numpy as np
import time

class AcquisitionManager(QObject):
    """
    Acquisition manager class
    """
    readoutFinished = pyqtSignal()

    def __init__(self, p_samples: int = 50000):
        """
        Initialization of AcquisitionManager class
        @type p_samples: Amount of samples
        """
        super(AcquisitionManager, self).__init__()
        self._samples: int = p_samples

    # Function to trigger manager and perform single readout
    def get_spectrum(self, p_frequency: float, p_ts: int = 20) -> [np.complex64, float]:
        """
        Get the spectrum data of the sample volume
        @param p_ts:            Sample time in ms (parameter)
        @param p_frequency:     Excitation frequency in MHz (parameter)
        @return:                Data-object (processed), acquisition time
        """
        if p_frequency is not params.freq:
            Com.setFrequency(p_frequency)
        
        t0: float = time.time()
        Com.acquireSpectrum()
        Com.waitForTransmission()

        tmp_data: np.complex64 = Com.readData(self._samples)

        t1: float = time.time()
        acquisitiontime: float = (t1-t0)/60
        dataobject: Data = Data(tmp_data, p_ts)
        #self.readoutFinished.emit()

        return [dataobject, acquisitiontime]

    # Function to acquire an image with multiple readouts
    def get_kspace(self, p_npe: int = 16, p_tr: int = 4000) -> [np.complex, float]:
        """
        Get 2D k-space of sample volume (no slice selection)
        @param p_npe:   Number of phase encoding steps (parameter)
        @param p_tr:    Repetition time in ms (parameter)
        @return:        Raw data in 2D array, acquisition time
        """
        tmp_data: np.ndarray = np.array(np.zeros(p_npe, self._samples), ndmin=2, dtype=np.complex64)

        t0: float = time.time()
        Com.acquireImage(p_npe, p_tr)
        Com.waitForTransmission()

        for n in range(p_npe):
            tmp_data[n, :] = Com.readData(self._samples)
            self.readoutFinished.emit()

        t1: float = time.time()
        acquisitiontime: float = (t1 - t0) / 60

        print('Finished image manager in {:.4f} min'.format((t1 - t0) / 60))

        return [tmp_data, acquisitiontime]

    # Function to acquire 1D projection
    def get_projection(self, p_axis: int) -> [np.complex, float, int]:
        """
        Get 1D projection along a dedicated axis
        @param p_axis:      Axis (parameter)
        @return:            1D raw data, acquisition time
        """
        t0: float = time.time()
        Com.acquireProjection(p_axis)
        Com.waitForTransmission()

        tmp_data: np.complex64 = Com.readData(self._samples)

        t1: float = time.time()
        acquisitiontime: float = (t1 - t0) / 60
        self.readoutFinished.emit()

        # TODO: Return datahandler object for projection

        return [tmp_data, acquisitiontime, p_axis]
