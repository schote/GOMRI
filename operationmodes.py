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
                 sequence: sqncs,
                 frequency: float = None,
                 # attenuation: float = None,
                 samples: int = None,
                 shim: list = None):
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

        self._frequency: float = frequency
        # self._attenuation = attenuation
        # self._sampletime = sampletime
        self._samples: int = samples
        self._shim_x: int = shim[0]
        self._shim_y: int = shim[1]
        self._shim_z: int = shim[2]
        self._shim_z2: int = shim[3]
        self._sequence = sequence # sqncs.FID
        self._sequencebytestream = Assembler().assemble(self._sequence.path)

    @property
    def systemproperties(self) -> dict:
        # TODO: add server cmd's as third entry in list
        return {
            nmspc.frequency: [float(self._frequency), '_frequency', cmd.localOscillatorFrequency],
            # nmspc.attenuation: [self._attenuation, '_attenuation'],
            # nmspc.sampletime: [self._sampletime, '_sampletime'],
            nmspc.samples: [int(self._samples), '_samples', cmd.runAcquisition]
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
            # nmspc.gradwaveform: []

            # 2D Imaging Implementations:
            # Insert gradient waveforms here with normalized waveform values in the range of 0-1.
            # Add repetitions - calculate scaling from system preferences and repetitions.
            # Load sequence and gradient waveforms in a sequence manager from csv file.
        }


"""
Definition of default operations
"""
defaultoperations = {
    'FID Spectrum': Spectrum(sqncs.FID, 11.295, 2000),
    'SE Spectrum (TE=10ms)': Spectrum(sqncs.SE, 11.295, 2000)
}
