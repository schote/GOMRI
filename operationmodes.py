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
from globalvars import sqncs, grads


class Spectrum:
    """
    Spectrum Operation Class
    """

    def __init__(self, frequency, attenuation, shim):
        """
        Initialization of spectrum operation class
        @param frequency:       Frequency value for operation
        @param attenuation:     Attenuation value for operation
        @param shim:            Shim values for operation
        @return:                None
        """
        if len(shim) != 4:
            warn('Invalid number of shim values.')
            return

        self.systemproperties = {
            'Frequency': frequency,
            'Attenuation': attenuation,
            'Shim Values': {
                "X Gradient": shim[0],
                "Y Gradient": shim[1],
                "Z Gradient": shim[2],
                "Z² Gradient": shim[3]
                }
        }

        self.sequences = {
            sqncs.FID.str: sqncs.FID.path,
            sqncs.SE.str: sqncs.SE.path,
            sqncs.IR.str: sqncs.IR.path,
            sqncs.SIR.str: sqncs.SIR.path
        }


# Initialization of default operationslist
operations = {
    'Spectrum1': Spectrum(20.1, 10, [0, 0, 0, 0]),
    'Spectrum2': Spectrum(13.1, 10, [0, 0, 0, 0]),
    'Spectrum3': Spectrum(10, 10, [1,2,3,4])
}
