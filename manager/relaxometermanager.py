from server.communicationhandler import CommunicationHandler as Com
from .sequencemanager import SequenceManager as SeqHndlr
from .acquisitionmanager import AcquisitionManager
from globalvars import sqncs, rlxs

import numpy as np
import warnings
import time


class RelaxometerManager:
    """
    Manager for the calculation of relaxation times
    """
    def __init__(self, p_relaxation: str, p_sequence: str, p_samples: int = 50000):
        self.Acq = AcquisitionManager(p_samples)
        self.p_relaxation = p_relaxation
        self.p_sequence = p_sequence

    def setTimeValue(self, p_tValue: int) -> None:
        """
        This function sets the time value in the dedicated sequence
        @ param:    p_tValue    Time value from list
        @ return:   None
        """
        if self.p_relaxation is rlxs.T1:
            if self.p_sequence is sqncs.SIR:
                SeqHndlr.setSaturationInversionRecovery(p_tValue)
            elif self.p_sequence is sqncs.IR:
                SeqHndlr.setInversionRecovery(p_tValue)
            else:
                warnings.warn('Relaxation time to be measured or sequence not valid!')
        elif self.p_relaxation and rlxs.T2:
            SeqHndlr.setSpinEcho(p_tValue)
        else:
            warnings.warn('Relaxation time to be measured or sequence not valid!')

    def get_relaxationTime(self, p_freq: float, p_tValues: list, p_recovery: int, p_ts: int = 2, **kwargs):
        """
        This function calculates the relaxation time, specified through p_relaxation
        @ params:   p_freq, p_tValues, p_recovery, p_ts
        @ optional: avgPerPnt, boundaries
        @ returns:  relaxation time, error, fitted function, fitted parameters
        """
        p_averagesPerPoint: int = kwargs.get('avgPerPnt', 1)
        #   p_averagesPerMeasurement = kwargs.get('avgM', 1)
        p_boundaries: list = kwargs.get('boundaries', 1)
        #   idx_measurement: int = 0
        idx_datapoint: int = 0
        arr_relaxations: np.ndarray
        arr_measurementBuffer: list = []

        Com.setFrequency(p_freq)

        for tValue in p_tValues:
            arr_datapointBuffer: list = []
            self.setTimeValue(tValue)
            while idx_datapoint < p_averagesPerPoint:
                time.sleep(p_recovery / 1000)
                [obj_data, _] = self.Acq.get_spectrum(p_ts)
                [_, datapoint, _, _] = obj_data.get_peakparameters()
                sign_datapoint = obj_data.get_sign()
                arr_datapointBuffer.append(datapoint * sign_datapoint)
                idx_datapoint += 1

            arr_measurementBuffer.append(np.mean(arr_datapointBuffer))

        # TODO: Class for fit calculation?

        t1: float = np.nanmean(self.calculateT1fit(values, p_boundaries))
        self.t1_finished.emit()

        return np.nanmean(self.T1), np.nanmean(self.R2)

    def calculateT1fit(self, values, bnds=[]):  # values -- TI values from measurement

        def func(x):
            return p[0] - p[1] * np.exp(-p[2] * x)

        try:
            if len(bnds) == 6:
                p, cov = curve_fit(self.T1_fit, values, self.measurement,
                                   bounds=([bnds[0], bnds[2], bnds[4]], [bnds[1], bnds[3], bnds[5]]))
                print("T1 FIT\n bnds:\t{}\n p-values:\t{}\n cov:\t{}\n".format(bnds, p, cov))
            else:
                p, cov = curve_fit(self.T1_fit, values, self.measurement,
                                   bounds=([0, self.measurement[0], 0], [10, 50000, 0.5]))
                print("T1 FIT\n p-values:\t{}\n cov:\t{}\n".format(p, cov))

            # Calculate T1 value and error
            self.T1.append(round(1.44 * brentq(func, values[0], values[-1]), 2))
            self.R2.append(round(1 - (np.sum((self.measurement - self.T1_fit(values, *p)) ** 2) / (
                np.sum((self.measurement - np.mean(self.measurement)) ** 2))), 5))
            self.x_fit = np.linspace(0, int(1.2 * values[-1]), 1000)
            self.y_fit = self.T1_fit(self.x_fit, *p)
            self.fit_params = p
        except:  # in case no fit found
            self.T1.append(float('nan'))
            self.R2.append(float('nan'))
            self.x_fit = []  # float('nan')
            self.y_fit = []  # float('nan')
            self.fit_params = []  # float('nan')

        print("T1 FIT\n bnds:\t{}".format(bnds))

    # Calculates fit for multiple IR's to determine t0
    def T1_fit(self, x, A, B, C):
        return A - B * np.exp(-C * x)

    # _______________________________________________________________________________
    #   T2 Measurement

    # Acquires one or multiple T2 values through multiple SE's
    def T2_measurement(self, values, freq, recovery, **kwargs):
        print('T1 Measurement')

        ts = 2

        avgPoint = kwargs.get('avgP', 1)
        avgMeas = kwargs.get('avgM', 1)
        self.idxM = 0;
        self.idxP = 0
        self.T2 = [];
        self.R2 = [];
        self.measurement = []

        self.set_freq(freq)

        while self.idxM < avgMeas:
            print("Measurement : ", self.idxM + 1, "/", avgMeas)
            self.measurement = []

            for self.te in values:
                self.peaks = []
                self.set_SE(self.te)

                while self.idxP < avgPoint:
                    print("Datapoint : ", self.idxP + 1, "/", avgPoint)
                    time.sleep(recovery / 1000)
                    socket.write(struct.pack('<I', 1 << 28))

                    while True:
                        socket.waitForReadyRead()
                        datasize = socket.bytesAvailable()
                        print(datasize)
                        time.sleep(0.1)
                        if datasize == 8 * self.size:
                            print("IR readout finished : ", datasize)
                            self.buffer[0:8 * self.size] = socket.read(8 * self.size)
                            break
                        else:
                            continue

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
                p, cov = curve_fit(self.T2_fit, values, self.measurement,
                                   bounds=([0, self.measurement[0], 0], [10, 50000, 0.5]))
                # Calculation of T2: M(T2) = 0.37*(func(0)) = 0.37(A+B), T2 = -1/C * ln((M(T2)-A)/B)
                self.T2.append(round(-(1 / p[2]) * np.log(((0.37 * (p[0] + p[1])) - p[0]) / p[1]), 5))
                self.R2.append(round(1 - (np.sum((self.measurement - self.T2_fit(values, *p)) ** 2) / (
                    np.sum((self.measurement - np.mean(self.measurement)) ** 2))), 5))
                self.x_fit = np.linspace(0, int(1.2 * values[-1]), 1000)
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

class FitFunction:
    """
    Class to calculate fit function for the determination of relaxation time
    """

    arr_xFit: list              # x-axis, fitted function
    arr_yFit: list              # y-axis, fitted function
    arr_fitParameter: list      # optimized parameter array
    result: float               # resulting t1/t2 value
    errorR2: float              # R2 error of fitted function

    def __init__(self, relaxation: str):
        self.arr_xFit = []
        self.arr_yFit = []
        self.arr_fitParameter = []
        self.result = 0
        self.errorR2 = 0

        self.type = relaxation

    @staticmethod
    def fit_t1RelaxationTime(t, A, B, C):
        """
        T1 fit function
        """
        return A - B * np.exp(-C * t)

    @staticmethod
    def fit_t2RelaxationTime(t, A, B, C):
        """
        T2 fit function
        """
        return A + B * np.exp(-C * t)

    def calculateRelaxationTime(self):
        """
        Determine fit function and calculate T1/T2
        @ params:
        @ returns:  T1/T2 value, fit error
        """
        if self.type is rlxs.T1:
            print('T1')
        else:
            print('T2')
