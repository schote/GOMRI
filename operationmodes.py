"""
Operation Modes

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0 (Beta)
@change:    13/06/2020

@summary:   TBD

@status:    Under development, simple 1D spectrum operation implemented
@todo:      Add gradient waveform, add more properties, add more operation types (create directory for operations)
"""

from warnings import warn
from globalvars import sqncs
from assembler import Assembler
from operationsnamespace import Namespace as nmspc
from operationsnamespace import Reconstruction as reco
from server.communicationmanager import Commands as cmd


class Spectrum:
    """
    Spectrum Operation Class
    """
    def __init__(self,
                 frequency: float = None,
                 # attenuation: float = None,
                 samples: int = None,
                 # sampletime: float = None,
                 shim=None):
        """
        Initialization of spectrum operation class
        @param frequency:       Frequency value for operation
        @param attenuation:     Attenuation value for operation
        @param shim:            Shim values for operation
        @return:                None
        """
        if shim is None:
            shim = [0, 0, 0, 0]
        else:
            while len(shim) < 4:
                shim += [0]

        self._frequency = frequency
        # self._attenuation = attenuation
        # self._sampletime = sampletime
        self._samples = samples
        self._shim_x = shim[0]
        self._shim_y = shim[1]
        self._shim_z = shim[2]
        self._shim_z2 = shim[3]
        self._sequence = sqncs.FID
        self._sequencebytestream = Assembler().assemble(self._sequence.path)

    @property
    def systemproperties(self) -> dict:
        # TODO: add server cmd's as third entry in list
        return {
            nmspc.frequency: [self._frequency, '_frequency', cmd.localOscillatorFrequency],
            # nmspc.attenuation: [self._attenuation, '_attenuation'],
            # nmspc.sampletime: [self._sampletime, '_sampletime'],
            nmspc.samples: [self._samples, '_samples', cmd.runAcquisition]
        }

    @property
    def gradientshims(self):
        return {
            nmspc.x_grad: [self._shim_x, '_shim_x', cmd.gradientOffsetX],
            nmspc.y_grad: [self._shim_y, '_shim_y', cmd.gradientOffsetY],
            nmspc.z_grad: [self._shim_z, '_shim_z', cmd.gradientMemoryZ]
            # nmspc.z2_grad: [self._shim_z2, '_shim_z2']
        }

    # TODO: Different interaction modes -> button to upload sequence/gradient file ?

    @property
    def pulsesequence(self) -> dict:
        return {
            nmspc.type: reco.spectrum,
            nmspc.sequence: [self._sequence, self._sequencebytestream]
            # TODO: Gradient waveform
        }


"""
Definition of default operations -- To be extended
"""
serviceOperation = Spectrum()
defaultoperations = {
    'FID Spectrum 1': Spectrum(20.0971, 1000, [0, 0, 0, 0]),
    'FID Spectrum 2': Spectrum(11.25811, 2000, [0, 0, 0, 0])
}
