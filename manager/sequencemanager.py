"""
Sequence Manager

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   1.0
@change:    02/05/2020

@summary:   Class for modifying and packing a sequence.

@status:    Under testing
@todo:

"""
from PyQt5.QtCore import QObject, pyqtSignal
from assembler import Assembler
from server.communicationmanager import CommunicationManager as Com
from globalvars import sqncs, SqncObject


class SequenceManager(QObject):
    """
    Sequence manager class
    """
    sequenceUploaded = pyqtSignal()

    def __init__(self):
        """
        Initialisation of sequence manager class
        """
        super(SequenceManager, self).__init__()
        self.assembler = Assembler()
        self.flag_sqncs = {
            sqncs.FID.str: False,
            sqncs.SE.str: False,
            sqncs.IR.str: False,
            sqncs.SIR: False
        }

    # Function to init and set FID -- only acquire call is necessary afterwards
    def packSequence(self, sqnc: SqncObject) -> bool:
        """
        Pack a sequence and call upload
        @param sqnc:    Sequence to be packed
        @return:        None
        """
        byte_array = self.assembler.assemble(sqnc.path)
        upload = Com.setSequence(byte_array)

        self.flag_sqncs = dict.fromkeys(self.flag_sqncs, False)
        self.flag_sqncs[sqnc.str] = True

        print("\n {} sequence uploaded.".format(sqnc.str))
        return upload

    # Function to change TE in sequence
    @staticmethod
    def setSpinEcho(te: int = 10) -> None:
        """
        Set a spin echo sequence by changing echo time
        @param te:  Echo time in ms
        @return:    None
        """
        # Open sequence and read lines
        f = open(sqncs.SE.path, 'r+')
        lines = f.readlines()
        if te < 2:
            te = 2
        # Modify TE time in the 8th last line
        lines[-10] = 'PR 3, ' + str(int(te / 2 * 1000 - 112)) + '\t// wait&r\n'
        lines[-6] = 'PR 3, ' + str(int(te / 2 * 1000 - 975)) + '\t// wait&r\n'
        # Close and write/save modified sequence
        f.close()
        with open(sqncs.SE.path, "w") as out_file:
            for line in lines:
                out_file.write(line)

    # Function to set default IR sequence
    @staticmethod
    def setInversionRecovery(ti: int = 15) -> None:
        """
        Set inversion recovery sequence by changing time of inversion
        @param ti:  Time of inversion in ms
        @return:    None
        """
        f = open(sqncs.IR.path, 'r+')  # Open sequence and read lines
        lines = f.readlines()
        # Modify TI time in the 8th last line
        lines[-14] = 'PR 3, ' + str(int(ti * 1000 - 198)) + '\t// wait&r\n'
        f.close()  # Close and write/save modified sequence
        with open(sqncs.IR.path, "w") as out_file:
            for line in lines:
                out_file.write(line)

    # Function to set default SIR sequence
    @staticmethod
    def setSaturationInversionRecovery(ti: int = 15) -> None:
        """
        Set saturation inversion recovery sequence by changing time of inversion
        @param ti:  Time of inversion in ms
        @return:    None
        """
        f = open(sqncs.SIR.path, 'r+')  # Open sequence and read lines
        lines = f.readlines()
        # Modify TI time in the 8th last line
        # ines[-14] = 'PR 3, ' + str(int(TI * 1000 - 198)) + '\t// wait&r\n'
        # lines[-18] = 'PR 3, ' + str(int(TI * 1000 - 198)) + '\t// wait&r\n'
        lines[-9] = 'PR 3, ' + str(int(ti * 1000 - 198)) + '\t// wait&r\n'
        lines[-13] = 'PR 3, ' + str(int(ti * 1000 - 198)) + '\t// wait&r\n'
        f.close()  # Close and write/save modified sequence
        with open(sqncs.SIR.path, "w") as out_file:
            for line in lines:
                out_file.write(line)


SqncMngr = SequenceManager()
