"""
Data Manager

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   1.0
@change:    02/05/2020

@summary:   Class for managing the data procession of acquired data.
            Processes data in time (t_) and frequency (f_) domain.

@status:    Under testing
@todo:      Improve get functions, snr calculation

"""

from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime
from parameters import params
from dataclasses import dataclass
import numpy as np

# just for debugging calculations:
# import matplotlib.pyplot as plt

@dataclass(repr=False, eq=False)
class DataManager(QObject):
    """
    Data manager class
    """
    # Init signal that's emitted when readout is processed
    t1_finished = pyqtSignal()
    t2_finished = pyqtSignal()
    uploaded = pyqtSignal(bool)

    __slots__ = ['_t_magnitude',
                 '_t_real',
                 '_t_imag',
                 '_t_axis',
                 '_t_magnitudeCon',
                 '_t_realCon',
                 '_f_axis',
                 '_f_fftData',
                 '_f_fftMagnitude']

    def __init__(self, data: np.complex, p_ts: int = 10, f_range: int = 250000):
        """
        Initialisation of data manager class
        @param data:        Raw data
        @param p_ts:        Sample time (property)
        @param f_range:     Range of frequency spectrum
        """
        super(DataManager, self).__init__()
        self.data = data
        self.f_range = f_range
        self.p_ts = p_ts
        self.idx_samplepoints = int(p_ts * 250)

        d_cropped = self.data[0:self.idx_samplepoints] * 2000.0
        self._t_axis = np.linspace(0, self.p_ts, self.idx_samplepoints)
        self._t_magnitude = np.abs(d_cropped)
        self._t_magnitudeCon = np.convolve(self.t_magnitude, np.ones((50,)) / 50, mode='same')
        self._t_real = np.real(d_cropped)
        self._t_realCon = np.convolve(self.t_real, np.ones((50,)) / 50, mode='same')
        self._t_imag = np.imag(d_cropped)

        self._f_axis = np.linspace(-self.f_range / 2, self.f_range / 2, self.idx_samplepoints)
        self._f_fftData = np.fft.fftshift(np.fft.fft(np.fft.fftshift(d_cropped), n=self.idx_samplepoints, norm='ortho'))
        self._f_fftMagnitude = abs(self.f_fftData)

    @property
    def t_axis(self):
        return self._t_axis

    @property
    def t_magnitude(self):
        return self._t_magnitude

    @property
    def t_magnitudeCon(self):
        return self._t_magnitudeCon

    @property
    def t_real(self):
        return self._t_real

    @property
    def t_realCon(self):
        return self._t_realCon

    @property
    def t_imag(self):
        return self._t_imag

    @property
    def f_axis(self):
        return self._f_axis

    @property
    def f_fftData(self):
        return self._f_fftData

    @property
    def f_fftMagnitude(self):
        return self._f_fftMagnitude

    # TODO: Implementation of params-setter (?)

    # Function to process the readout: extract spectrum, real, imag and magnitude data
    """
    def processReadoutData(self):

        #Process readout, sets frequency and time related class variables
        #@return: None

        timestamp = datetime.now()

        # +-1V -> multiply by 2000 to obtain mV
        d_cropped = self.data[0:self.idx_samplepoints] * 2000.0

        # Time domain data
        self.t_magnitude = np.abs(d_cropped)
        self.t_imag = np.imag(d_cropped)
        self.t_real = np.real(d_cropped)

        self.t_magnitudeCon = np.convolve(type(self).t_magnitude, np.ones((50,)) / 50, mode='same')
        self.t_realCon = np.convolve(type(self).t_real, np.ones((50,)) / 50, mode='same')
        self.t_axis = np.linspace(0, self.p_ts, self.idx_samplepoints)

        # Frequency domain data
        self.f_axis = np.linspace(-self.f_range / 2, self.f_range / 2, self.idx_samplepoints)  # 5000 points ~ 20ms
        self.f_fftData = np.fft.fftshift(np.fft.fft(np.fft.fftshift(d_cropped), n=self.idx_samplepoints,
                                                    norm='ortho'))  # Normalization through 1/sqrt(n)
        self.f_fftMagnitude = abs(type(self).f_fftData)

        params.dataTimestamp = timestamp.strftime('%m/%d/%Y, %H:%M:%S')
        params.data = d_cropped
        params.freqaxis = self.f_axis
        params.fft = self.f_fftMagnitude



        #   Amplitude and phase plot
        #   fig, ax = plt.subplots(2,1)
        #   ax[0].plot(self.time_axis, self.real_t)
        #   ax[0].plot(self.time_axis, np.convolve(self.real_t, np.ones((50,))/50, mode='same'))
        #   ax[1].plot(self.fft)
        #   ax[1].psd(self.dclip, Fs=250, Fc=int(1.0e6 * params.freq))
        #   fig.tight_layout(); plt.show()
    """

    def get_fwhm(self, f_fwhmWindow: int = 1000) -> [int, float, float]:
        """
        Get full width at half maximum
        @param f_fwhmWindow:    Frequency window
        @return:                FWHM in datapoint indices, hertz and ppm
        """
        [_peakValue, _, _peakIdx, _peakFreq] = self.get_peakparameters()
        # TODO: Use more than one line for next statement
        fft = self.f_fftMagnitude
        candidates: np.ndarray = np.abs([x - _peakValue / 2
                                         for x in fft[
                                                  _peakIdx - f_fwhmWindow / 2:_peakIdx + f_fwhmWindow / 2]])
        # Calculate index difference by find indices of minima, calculate fwhm in Hz thereafter
        _fwhm: int = np.argmin(candidates[f_fwhmWindow:]) + f_fwhmWindow - np.argmin(candidates[:f_fwhmWindow])
        _fwhm_hz: float = _fwhm * (abs(np.min(self._f_axis)) + abs(np.max(self._f_axis))) / self.idx_samplepoints
        _fwhm_ppm: float = _fwhm_hz / _peakFreq

        return [_fwhm, _fwhm_hz, _fwhm_ppm]

    def get_snr(self, f_windowfactor: float = 1.2, n: int = 50) -> float:
        """
        Get signal to noise ratio
        @param f_windowfactor:  Frequency window
        @param n:               N datapoints for moving average
        @return:                SNR
        """
        [f_fwhm, _] = self.get_fwhm()
        [f_signalValue, f_signalIdx, _] = self.get_peakparameters()
        f_peakWin: int = int(f_fwhm * f_windowfactor)
        f_fftMovingAverage: np.ndarray = np.convolve(self._f_fftMagnitude, np.ones((n,)) / n, mode='same')
        # TODO: Calculate noise through standard deviation of complex data
        _noise: np.ndarray = np.subtract(self._f_fftMagnitude, f_fftMovingAverage)
        _snr = round(f_signalValue / np.std([_noise[:f_signalIdx - f_peakWin / 2],
                                             _noise[f_signalIdx + f_peakWin / 2:]]), 2)

        return _snr  # TODO: Add return in dB

    def get_peakparameters(self) -> [float, float, int, float]:
        """
        Get peak parameters
        @return:            Frequency peak, time domain peak, index of frequency peak, frequency of peak
        """
        frequency: float = params.freq
        t_signalValue: float = round(np.max(self._t_magnitudeCon), 4)
        f_signalValue: float = round(np.max(self._f_fftMagnitude), 4)
        f_signalIdx: int = np.argmax(self._f_fftMagnitude)#[0]
        f_signalFrequency: float = round(frequency + ((f_signalIdx - self.idx_samplepoints / 2)
                                                      * self.f_range / self.idx_samplepoints) / 1.0e6, 6)

        return [f_signalValue, t_signalValue, f_signalIdx, f_signalFrequency]

    @property
    def get_sign(self) -> int:
        """
        Get sign of real part signal in time domain
        @return:    Sign
        """
        index: np.ndarray = np.argmin(self._t_realCon[0:50])
        return np.sign(self._t_realCon[index])
