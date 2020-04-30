## @package sequencehandler


## Imports
from assembler import Assembler
from server.communicationhandler import CommunicationHandler as Com
from globalvars import sqncs
from parameters import params


class SequenceManager:

    def __init__(self):
        self.assembler = Assembler()
        self.flag_sqncs = {
            sqncs.FID.str: False,
            sqncs.SE.str: False,
            sqncs.IR.str: False,
            sqncs.SIR: False
        }

    # Function to init and set FID -- only acquire call is necessary afterwards
    def uploadSequence(self, sqnc):

        byte_array = self.assembler.assemble(sqnc.path)
        Com.setSequence(byte_array)

        self.flag_sqncs = dict.fromkeys(self.flag_sqncs, False)
        self.flag_sqncs[sqnc.str] = True

        print("\n {} sequence uploaded.".format(sqnc.str))

    # Function to change TE in sequence
    @staticmethod
    def setSpinEcho(te: int = 10):
        params.te = te
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
    def setInversionRecovery(ti: int = 15):
        params.ti = ti
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
    def setSaturationInversionRecovery(ti: int = 15):
        params.ti = ti
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
