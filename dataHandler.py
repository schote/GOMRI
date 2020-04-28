################################################################################
#
#   Author:     David Schote (david.schote@ovgu.de)
#   Date:       11/27/2019
#
#   Data Handler
#   This class handles the server connection, the setup of sequences,
#   the transmission of commands, execution of T1/T2 measurements and
#   spectroscopy
#
#   Trigger table on server when sending trigger-bit:
#   (shifted to the left by 28 bits)
#       0:  no trigger
#       1:  transmit
#       2:  set frequency
#       3:  set attenuation
#       4:  upload sequence
#       5:  set gradient offsets
#       6:  acquire 2D SE image
#       7:  acquire 1D projections
#
################################################################################

import sys
import struct
import time
from datetime import datetime

from PyQt5.QtCore import pyqtSignal

from server.communicationhandler import com
from server.acquisitionhandler import acq


import numpy as np
from scipy.optimize import curve_fit, brentq
# just for debugging calculations:
# import matplotlib.pyplot as plt

from parameters import params

class DataHandler:

    # Init signal that's emitted when readout is processed
    t1_finished = pyqtSignal()
    t2_finished = pyqtSignal()
    uploaded = pyqtSignal(bool)

    data: np.complex_64                 # data, from acquisition handler

    t_sample: int                       # sample time
    t_magnitude: np.ndarray             # magnitude, time domain
    t_real: np.ndarray                  # real part, time domain
    t_imag: np.ndarray                  # imaginary part, time domain
    t_axis: np.ndarray                  # axis, time domain
    t_magnitudeCon: np.ndarray          # convolution: magnitude, time domain
    t_realCon: np.ndarray               # convolution: real part, time domain

    f_axis: np.ndarray                  # axis, frequency domain
    f_range: int                        # range, frequency domain
    f_fftData: np.ndarray               # fft, complex data in frequency domain
    f_fftMagnitude: np.ndarray          # fft, magnitude, frequency domain

    def __init__(self, data: np.complex, t_sample: int = 20, f_range: int = 250000):
        self.data = data
        self.f_range = f_range
        self.t_sample = t_sample
        self.t_dataIdx = int(t_sample*250)

    # Function to process the readout: extract spectrum, real, imag and magnitude data
    def processReadoutData(self):

        timestamp = datetime.now()

        # +-1V -> multiply by 2000 to obtain mV
        d_cropped: np.complex_64 = self.data[0:self.t_dataIdx] * 2000.0

        # Time domain data
        self.t_magnitude = np.abs(d_cropped)
        self.t_imag = np.imag(d_cropped)
        self.t_real = np.real(d_cropped)

        self.t_magnitudeCon = np.convolve(self.t_magnitude, np.ones((50,))/50, mode='same')
        self.t_realCon = np.convolve(self.t_real, np.ones((50,))/50, mode='same')
        self.t_axis = np.linspace(0, self.t_sample, self.t_dataIdx)

        # Frequency domain data
        self.f_axis = np.linspace(-self.f_range/2, self.f_range/2, self.t_dataIdx)   # 5000 points ~ 20ms
        self.f_fftData = np.fft.fftshift(np.fft.fft(np.fft.fftshift(d_cropped), n=self.t_dataIdx, norm='ortho'))   # Normalization through 1/sqrt(n)
        self.f_fftMagnitude = abs(self.f_fftData)

        params.dataTimestamp = timestamp.strftime('%m/%d/%Y, %H:%M:%S')
        params.data = d_cropped
        params.freqaxis = self.f_axis
        params.fft = self.f_fftMagnitude

        # Amplitude and phase plot
        #fig, ax = plt.subplots(2,1)
        #ax[0].plot(self.time_axis, self.real_t)
        #ax[0].plot(self.time_axis, np.convolve(self.real_t, np.ones((50,))/50, mode='same'))
        #ax[1].plot(self.fft)
        #ax[1].psd(self.dclip, Fs=250, Fc=int(1.0e6 * params.freq))
        #fig.tight_layout(); plt.show()

        print("\tReadout processed.")

    def get_fwhm(self, f_fwhmWindow: int = 1000) -> [int, float, float]:
        [f_peakValue, f_peakIdx, f_peakFreq] = self.get_peakparameters()
        candidates: np.ndarray = np.abs([x - f_peakValue / 2 for x in self.f_fftMagnitude[f_peakIdx - f_fwhmWindow/2:f_peakIdx + f_fwhmWindow/2]])
        # Calculate index difference by find indices of minima, calculate fwhm in Hz thereafter
        f_fwhm: int = np.argmin(candidates[f_fwhmWindow:]) + f_fwhmWindow - np.argmin(candidates[:f_fwhmWindow])
        f_fwhm_hz: float = f_fwhm * (abs(np.min(self.f_axis)) + abs(np.max(self.f_axis))) / self.t_dataIdx
        f_fwhm_ppm: float = f_fwhm_hz/f_peakFreq

        return [f_fwhm, f_fwhm_hz, f_fwhm_ppm]

    def get_snr(self, f_windowfactor: float = 1.2, n: int = 50) -> float:
        [f_fwhm, _] = self.get_fwhm()
        [f_signalValue, f_signalIdx, _] = self.get_peakparameters()
        f_peakWin: int = int(f_fwhm * f_windowfactor)
        f_fftMovingAverage: np.ndarray = np.convolve(self.f_fftMagnitude, np.ones((n,)) / n, mode='same')
        noise: np.ndarray = np.subtract(self.f_fftMagnitude, f_fftMovingAverage)
        snr = round(f_signalValue / np.std([noise[:f_signalIdx - f_peakWin/2], noise[f_signalIdx + f_peakWin/2:]]), 2)

        return snr      # TODO: Add return in dB

    def get_peakparameters(self, freq: float = params.freq) -> [float, int, float]:

        f_signalValue: float = round(np.max(self.f_fftMagnitude), 2)
        f_signalIdx: int = np.argmax(self.f_fftMagnitude)[0]
        f_signalFrequency: float = round(freq + ((f_signalIdx - self.t_dataIdx / 2)
                                                 * self.f_range / self.t_dataIdx) / 1.0e6, 6)

        return [f_signalValue, f_signalIdx, f_signalFrequency]

    # TODO: Connect acquisitionhandler signal with instantiation of datahandler class

#_______________________________________________________________________________
#   T1 Measurement

    # Acquires one or multiple T1 values through multiple IR's
    def T1_measurement(self, values, freq, recovery, **kwargs):
        print('T1 Measurement')

        avgPoint = kwargs.get('avgP', 1)
        avgMeas = kwargs.get('avgM', 1)
        seq_type = kwargs.get('seqType', 1)
        ts = 2

        self.idxM = 0; self.idxP = 0
        self.T1 = []; self.R2 = []
        self.set_freq(freq)

        #while self.idxM < avgMeas:
            #print("Measurement : ", self.idxM+1, "/", avgMeas)
        self.measurement = []

        for self.ti in values:
            self.peaks = []

            if seq_type == 'sir':
                self.set_SIR(self.ti)
            else: self.set_IR(self.ti)

            while self.idxP < avgPoint:
                print("Datapoint : ", self.idxP+1, "/", avgPoint)
                time.sleep(recovery/1000)
                socket.write(struct.pack('<I', 1 << 28))

                while True: # Readout data
                    socket.waitForReadyRead()
                    datasize = socket.bytesAvailable()
                    print(datasize)
                    time.sleep(0.1)
                    if datasize == 8*self.size:
                        print("IR readout finished : ", datasize)
                        self.buffer[0:8*self.size] = socket.read(8*self.size)
                        break
                    else: continue

                print("Start processing IR readout.")
                self.process_readout(ts)
                print("Start analyzing IR data.")
                self.analytics()
                self.peaks.append(np.max(self.mag_con)*np.sign(self.real_con[np.argmin(self.real_con[0:50])]))
                #self.peaks.append(self.peak_value*np.sign(self.real_con[np.argmin(self.real_con[0:50])]))
                self.readout_finished.emit()
                self.idxP += 1

            self.measurement.append(np.mean(self.peaks))
            self.idxP = 0

        #self.calculateT1fit(values)
        #bounds=([0, self.measurement[0], 0], [100, 50000, 1])
        self.calculateT1fit(values)#, bounds)

        self.t1_finished.emit()
            #self.idxM += 1

        return np.nanmean(self.T1), np.nanmean(self.R2)

    def calculateT1fit(self, values, bnds=[]): # values -- TI values from measurement

        def func(x):
            return p[0] - p[1] * np.exp(-p[2]*x)

        try:
            if len(bnds) == 6:
                p, cov = curve_fit(self.T1_fit, values, self.measurement, bounds =([bnds[0], bnds[2], bnds[4]], [bnds[1], bnds[3], bnds[5]]))
                print("T1 FIT\n bnds:\t{}\n p-values:\t{}\n cov:\t{}\n".format(bnds, p, cov))
            else:
                p, cov = curve_fit(self.T1_fit, values, self.measurement, bounds=([0, self.measurement[0], 0], [10, 50000, 0.5]))
                print("T1 FIT\n p-values:\t{}\n cov:\t{}\n".format(p, cov))

            # Calculate T1 value and error
            self.T1.append(round(1.44*brentq(func, values[0], values[-1]),2))
            self.R2.append(round(1-(np.sum((self.measurement - self.T1_fit(values, *p))**2)/(np.sum((self.measurement-np.mean(self.measurement))**2))),5))
            self.x_fit = np.linspace(0, int(1.2*values[-1]), 1000)
            self.y_fit = self.T1_fit(self.x_fit, *p)
            self.fit_params = p
        except: # in case no fit found
            self.T1.append(float('nan'))
            self.R2.append(float('nan'))
            self.x_fit = []#float('nan')
            self.y_fit = []#float('nan')
            self.fit_params = []#float('nan')

        print("T1 FIT\n bnds:\t{}".format(bnds))

    # Calculates fit for multiple IR's to determine t0
    def T1_fit(self, x, A, B, C):
        return A - B * np.exp(-C * x)

#_______________________________________________________________________________
#   T2 Measurement

    # Acquires one or multiple T2 values through multiple SE's
    def T2_measurement(self, values, freq, recovery, **kwargs):
        print('T1 Measurement')

        ts = 2

        avgPoint = kwargs.get('avgP', 1)
        avgMeas = kwargs.get('avgM', 1)
        self.idxM = 0; self.idxP = 0
        self.T2 = []; self.R2 = []; self.measurement = []

        self.set_freq(freq)

        while self.idxM < avgMeas:
            print("Measurement : ", self.idxM+1, "/", avgMeas)
            self.measurement = []

            for self.te in values:
                self.peaks = []
                self.set_SE(self.te)

                while self.idxP < avgPoint:
                    print("Datapoint : ", self.idxP+1, "/", avgPoint)
                    time.sleep(recovery/1000)
                    socket.write(struct.pack('<I', 1 << 28))

                    while True:
                        socket.waitForReadyRead()
                        datasize = socket.bytesAvailable()
                        print(datasize)
                        time.sleep(0.1)
                        if datasize == 8*self.size:
                            print("IR readout finished : ", datasize)
                            self.buffer[0:8*self.size] = socket.read(8*self.size)
                            break
                        else: continue

                    print("Start processing SE readout.")
                    self.process_readout(ts)
                    print("Start analyzing SE data.")
                    self.analytics()
                    self.peaks.append(np.max(self.mag_con))

                    self.readout_finished.emit()
                    self.idxP += 1

                self.measurement.append(np.mean(self.peaks))
                self.idxP = 0

            # Calculate T2 value and error
            try:
                p, cov = curve_fit(self.T2_fit, values, self.measurement, bounds=([0, self.measurement[0], 0], [10, 50000, 0.5]))
                # Calculation of T2: M(T2) = 0.37*(func(0)) = 0.37(A+B), T2 = -1/C * ln((M(T2)-A)/B)
                self.T2.append(round(-(1/p[2])*np.log(((0.37*(p[0]+p[1]))-p[0])/p[1]), 5))
                self.R2.append(round(1-(np.sum((self.measurement - self.T2_fit(values, *p))**2)/(np.sum((self.measurement-np.mean(self.measurement))**2))),5))
                self.x_fit = np.linspace(0, int(1.2*values[-1]), 1000)
                self.y_fit = self.T2_fit(self.x_fit, *p)
                self.fit_params = p
                self.t2_finished.emit()
                self.idxM += 1
            except:
                self.T2.append(float('nan'))
                self.R2.append(float('nan'))
                self.x_fit = float('nan')
                self.y_fit = float('nan')
                self.fit_params = float('nan')
                self.t2_finished.emit()
                self.idxM += 1



        return np.nanmean(self.T2), np.nanmean(self.R2)

    # Calculates fit for multiple SE's to determine drop of Mxy
    def T2_fit(self, x, A, B, C):
        return A + B * np.exp(-C * x)



