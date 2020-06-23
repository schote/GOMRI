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
from globalvars import sqncs, nmspc, acqtypes


class Spectrum:
    """
    Spectrum Operation Class
    """

    def __init__(self, frequency, attenuation, sampletime, shim):
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

        self.properties = {
            nmspc.systemproperties: {
                nmspc.frequency: frequency,
                nmspc.attenuation: attenuation,
                nmspc.sampletime: sampletime
                },
            nmspc.shim: {
                nmspc.x_grad: shim[0],
                nmspc.y_grad: shim[1],
                nmspc.z_grad: shim[2],
                nmspc.z2_grad: shim[3]
                }
        }

        self.acquisition = {
            nmspc.type: acqtypes.spectrum,
            nmspc.sequence: {
                sqncs.FID.str: sqncs.FID.path
            }
        }


# Initialization of default operationslist
operations = {
    # Example FID corresponds to "get_exampleFidData()" -- prototype data set
    'Example FID Spectrum': Spectrum(20.0971, 10, 7.5, [0, 0, 0, 0]),
    'Spectrum Test': Spectrum(11.25811, 10, 20, [0, 0, 0, 0]),
    'Spectrum3': Spectrum(10, 10, 10, [1, 2, 3, 4])
}
