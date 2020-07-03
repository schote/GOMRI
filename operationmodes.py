"""
Operation Modes

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    13/06/2020

@summary:   TBD

@status:    Under development
@todo:      Subdivide operation object in finer structure,
            system properties, sequence properties, type, etc.
"""

from warnings import warn
from globalvars import sqncs
from operationsnamespace import Namespace as nmspc
from operationsnamespace import AcquisitionTypes as acqtypes


class Spectrum:
    """
    Spectrum Operation Class
    """
    def __init__(self,
                 frequency: float = None,
                 attenuation: float = None,
                 sampletime: float = None,
                 shim: list = None):
        """
        Initialization of spectrum operation class
        @param frequency:       Frequency value for operation
        @param attenuation:     Attenuation value for operation
        @param shim:            Shim values for operation
        @return:                None
        """
        while len(shim) < 4:
            shim += [0]

        self._frequency = frequency
        self._attenuation = attenuation
        self._sampletime = sampletime
        self._shim_x = shim[0]
        self._shim_y = shim[1]
        self._shim_z = shim[2]
        self._shim_z2 = shim[3]

    @property
    def systemproperties(self) -> dict:
        return {
            nmspc.frequency: [self._frequency, '_frequency'],
            nmspc.attenuation: [self._attenuation, '_attenuation'],
            nmspc.sampletime: [self._sampletime, '_sampletime']
        }

    @property
    def gradientshims(self):
        return {
            nmspc.x_grad: [self._shim_x, '_shim_x'],
            nmspc.y_grad: [self._shim_y, '_shim_y'],
            nmspc.z_grad: [self._shim_z, '_shim_z'],
            nmspc.z2_grad: [self._shim_z2, '_shim_z2']
        }

    @property
    def pulsesequence(self) -> dict:
        return {
            nmspc.type: acqtypes.spectrum,
            nmspc.sequence: sqncs.FID
        }

"""
Definition of default operations
"""
defaultoperations = {
    # Example FID corresponds to "get_exampleFidData()" -- prototype data set
    'Example FID Spectrum': Spectrum(20.0971, 10, 7.5, [0, 0, 0, 0]),
    'Spectrum Test': Spectrum(11.25811, 10, 20, [0, 0, 0, 0]),
    'Spectrum3': Spectrum(10, 10, 10, [1, 2, 3, 4])
}
