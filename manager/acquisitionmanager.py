##  @package    communicationhandler
#   @author     David Schote <david.schote@ovgu.de>
#   @date       25.04.2020

# Imports
from PyQt5.QtCore import pyqtSignal
from server.communicationhandler import CommunicationHandler as Com
from manager.datamanager import DataHandler as Data
from parameters import params
import numpy as np
import time

class AcquisitionManager:

    readoutFinished = pyqtSignal()

    def __init__(self, p_samples: int = 50000):
        self._samples: int = p_samples

    # Function to trigger manager and perform single readout
    def get_spectrum(self, p_ts: int = 20, frequency: float = params.freq) -> [np.complex64, float]:
        
        if frequency is not params.freq:
            Com.setFrequency(frequency)
        
        t0: float = time.time()
        Com.acquireSpectrum()
        Com.waitForTransmission()

        buffer: bytearray = Com.readData(self._samples)
        arr_data: np.complex_64 = np.frombuffer(buffer, np.complex64)

        t1: float = time.time()
        acquisitiontime: float = (t1-t0)/60
        obj_data: Data = Data(arr_data, p_ts)
        self.readoutFinished.emit()

        return [obj_data, acquisitiontime]

    # Function to acquire an image with multiple readouts
    def get_kspace(self, p_npe: int = 16, p_tr: int = 4000) -> [np.complex, float]:
        arr_data: np.ndarray = np.array(np.zeros(p_npe, self._samples), ndmin=2, dtype=np.complex_64)

        t0: float = time.time()
        Com.acquireImage(p_npe, p_tr)
        Com.waitForTransmission()

        for n in range(p_npe):
            buffer: bytearray = Com.readData(self._samples)
            arr_data[n, :] = np.frombuffer(buffer, np.complex_64)
            self.readoutFinished.emit()

        t1: float = time.time()
        acquisitiontime: float = (t1 - t0) / 60

        print('Finished image manager in {:.4f} min'.format((t1 - t0) / 60))

        return [arr_data, acquisitiontime]

    # Function to acquire 1D projection
    def get_projection(self, p_axis: int) -> [np.complex, float, int]:
        t0: float = time.time()
        Com.acquireProjection(p_axis)
        Com.waitForTransmission()

        buffer: bytearray = Com.readData(self._samples)
        l_data: np.complex_64 = np.frombuffer(buffer, np.complex_64)

        t1: float = time.time()
        acquisitiontime: float = (t1 - t0) / 60
        self.readoutFinished.emit()

        # TODO: Return datahandler object for projection

        return [l_data, acquisitiontime, p_axis]
