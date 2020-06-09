"""
Relaxation Manager

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   1.0
@change:    02/05/2020

@summary:   Class for managing the acquisition and procession of relaxation time measurements.

@status:    Under testing
@todo:      Improve get functions

"""

from server.communicationmanager import CommunicationManager as Com
from .sequencemanager import SequenceManager as SeqHndlr
from .acquisitionmanager import AcquisitionManager
from globalvars import sqncs, rlxs, SqncObject
from scipy.optimize import curve_fit, brentq

import numpy as np
import warnings
import time


# noinspection PyArgumentList
class RelaxometerManager:
    """
    Manager for the calculation of relaxation times
    """
    def __init__(self, p_relaxation: str, p_samples: int = 50000):
        """
        Initialization of relaxation manager
        @param p_relaxation:    Type of relaxation time (property)
        @param p_samples:       Number of sample points (property)
        """
        self.Acq = AcquisitionManager(p_samples)
        self.p_relaxation: str = p_relaxation

    # noinspection PyCallByClass
    def setTimeValue(self, p_sequence: SqncObject, p_tValue: int) -> None:
        """
        Set current time by calling sequence manager
        @param p_sequence:  Sequence that is going to be modified (property)
        @param p_tValue:    Current time value to be set (TI, TE, ...) (property)
        @return:            None
        """
        if self.p_relaxation is rlxs.T1:
            if p_sequence.str is sqncs.SIR:
                SeqHndlr.setSaturationInversionRecovery(p_tValue)
            elif p_sequence.str is sqncs.IR:
                SeqHndlr.setInversionRecovery(p_tValue)
            else:
                warnings.warn('Relaxation time to be measured or sequence not valid!')
                return
        elif self.p_relaxation and rlxs.T2:
            SeqHndlr.setSpinEcho(p_tValue)
        else:
            warnings.warn('Relaxation time to be measured or sequence not valid!')
            return
        SeqHndlr.packSequence(p_sequence)

    def get_relaxationTime(self, p_freq: float, p_sequence: SqncObject, p_tValues: list, p_recovery: int,
                           p_ts: int = 2, **kwargs) \
            -> [float, float, np.ndarray, np.ndarray, np.ndarray]:
        """
        Get the relaxation time
        @param p_sequence:      Sequence object that is used to get relaxation time
        @param p_freq:          Excitation frequency in MHz (property)
        @param p_tValues:       Time values for measurements (property, to be set in sequence)
        @param p_recovery:      Recovery time in ms
        @param p_ts:            Sample time in ms
        @param kwargs:          Optional Arguments (average, fit-boundaries)
        @return:                Relaxation time, R2 error metric, x-axis of fit, y-axis of fit, fitted parameters
        """
        p_averagesPerPoint: int = kwargs.get('avgPerPnt', 1)
        p_boundaries: list = kwargs.get('boundaries', 1)
        tmp_measurementBuffer: list = []

        Com.setFrequency(p_freq)

        for tValue in p_tValues:
            idx_datapoint: int = 0
            tmp_datapointBuffer: list = []
            self.setTimeValue(p_sequence, tValue)
            while idx_datapoint < p_averagesPerPoint:
                time.sleep(p_recovery / 1000)
                [data, _] = self.Acq.get_spectrum(p_ts)
                [_, datapoint, _, _] = data.get_peakparameters()
                sign_datapoint = data.get_sign()
                tmp_datapointBuffer.append(datapoint * sign_datapoint)
                idx_datapoint += 1
            tmp_measurementBuffer.append(np.mean(tmp_datapointBuffer))

        _fitter: FitFunction = FitFunction(self.p_relaxation, p_tValues, np.asarray(tmp_measurementBuffer),
                                           p_boundaries)

        return [_fitter.relaxation, _fitter.r2Metric, _fitter.fitXAxis, _fitter.fitYAxis, _fitter.fitParameter]


class FitFunction:
    """
    Class for fitting relaxation curve
    """
    fitXAxis: np.ndarray  # x-axis, fitted function
    fitYAxis: np.ndarray  # y-axis, fitted function
    fitParameter: np.ndarray  # optimized parameter array
    relaxation: float  # resulting t1/t2 value
    r2Metric: float  # R2 error of fitted function

    def __init__(self, relaxation: str, p_tValues: list, datapoints: np.ndarray, bounds=None):
        """
        Initialization of fitfunction class
        @param relaxation:      Relaxation type (T1/T2)
        @param p_tValues:       Time values (TI, TE, ...)
        @param datapoints:      Measured datapoints
        @param bounds:          Boundaries (optional)
        """

        if len(p_tValues) < 5 or len(datapoints) < 5:
            warnings.warn('Not enough data to calculate fit!')
            return
        elif len(p_tValues) is not len(datapoints):
            warnings.warn('Length of time values and acquired datapoints does not match!')
            return
        elif relaxation is not (rlxs.T1 or rlxs.T2):
            warnings.warn('Unknown relaxation time requested!')
            return
        else:
            self.type = relaxation

        self.fitXAxis = np.zeros(1000)
        self.fitYAxis = np.zeros(1000)
        self.fitParameter = np.zeros(3)
        self.relaxation = 0
        self.r2Metric = 0

        self.calculateRelaxationTime(p_tValues, datapoints, bounds)

    @staticmethod
    def fit_t1RelaxationTime(t, A, B, C):
        """
        Fit function layout for T1 relaxation time
        @param t:   Time
        @param A:   Parameter to fit
        @param B:   Parameter to fit
        @param C:   Parameter to fit
        @return:    Parameterized functional relation
        """
        return A - B * np.exp(-C * t)

    @staticmethod
    def fit_t2RelaxationTime(t, A, B, C):
        """
        Fit function layout for T2 relaxation time
        @param t:   Time in ms
        @param A:   Parameter to fit
        @param B:   Parameter to fit
        @param C:   Parameter to fit
        @return:    Parameterized functional relation
        """
        return A + B * np.exp(-C * t)

    # noinspection PyTypeChecker
    def calculateRelaxationTime(self, p_tValues: list, datapoints: np.ndarray, bounds=None) -> None:
        """
        Calculate and sets class intern relaxation time and fit data
        @param p_tValues:       Time values in ms
        @param datapoints:      Acquired datapoints
        @param bounds:          Boundaries (optional)
        @return:                None
        """
        # X values of fitted function
        self.fitXAxis: np.ndarray = np.linspace(0, int(1.2 * p_tValues[-1]), 1000)
        cov: float

        if self.type is rlxs.T1:  # Calculate T1 relaxation time
            if bounds is not None and len(bounds) is 6:
                fitParameter, cov = curve_fit(self.fit_t1RelaxationTime, p_tValues, datapoints,
                                              bounds=([bounds[0], bounds[2], bounds[4]],
                                                      [bounds[1], bounds[3], bounds[5]]))
            else:
                fitParameter, cov = curve_fit(self.fit_t1RelaxationTime, p_tValues, datapoints)

            def _fit(x: float) -> float:
                return float(fitParameter[0] - fitParameter[1] * np.exp(-fitParameter[2] * x))

            # Calculate relaxation time
            self.relaxation = round(1.44 * brentq(_fit, p_tValues[0], p_tValues[0]), 4)
            # Calculate r2 error metric
            self.r2Metric = round(1 - (np.sum((datapoints - self.fit_t1RelaxationTime(p_tValues, *fitParameter)) ** 2) /
                                       np.sum((datapoints - np.mean(datapoints)) ** 2)), 4)
            # Y values of fitted function
            self.fitYAxis: np.ndarray = self.fit_t1RelaxationTime(self.fitXAxis, *fitParameter)

        else:  # Calculate T2 relaxation time
            if bounds is not None and len(bounds) is 6:
                fitParameter, cov = curve_fit(self.fit_t2RelaxationTime, p_tValues, datapoints,
                                              bounds=([bounds[0], bounds[2], bounds[4]],
                                                      [bounds[1], bounds[3], bounds[5]]))
            else:
                fitParameter, cov = curve_fit(self.fit_t2RelaxationTime, p_tValues, datapoints)
            # Calculate relaxation time
            self.relaxation = round(-(1 / fitParameter[2]) * np.log(((0.37 * (fitParameter[0] + fitParameter[1]))
                                                                     - fitParameter[0]) / fitParameter[1]), 4)
            # Calculate r2 error metric
            self.r2Metric = round(1 - (np.sum((datapoints - self.fit_t2RelaxationTime(p_tValues, *fitParameter)) ** 2) /
                                       np.sum((datapoints - np.mean(datapoints)) ** 2)), 4)
            # Y values of fitted function
            self.fitYAxis = self.fit_t2RelaxationTime(self.fitXAxis, *fitParameter)

        self.fitParameter = fitParameter
