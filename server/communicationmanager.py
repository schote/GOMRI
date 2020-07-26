"""
Communication Manager

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   1.0
@change:    02/05/2020

@summary:   Class for managing the communication between server and host.
            Trigger table (interpreted by server, through 28th bit)
            0:  no trigger
            1:  transmit
            2:  set frequency
            3:  set attenuation
            4:  upload sequence
            5:  set gradient offsets
            6:  acquire 2D SE image
            7:  acquire 1D projections

@status:    Under testing
@todo:

"""

from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from globalvars import grads, pax
from server import server_comms as sc
import numpy as np
import struct
import time

states = {
    QAbstractSocket.UnconnectedState: "Unconnected",
    QAbstractSocket.HostLookupState: "Host Lookup",
    QAbstractSocket.ConnectingState: "Connecting",
    QAbstractSocket.ConnectedState: "Connected",
    QAbstractSocket.BoundState: "Bound",
    QAbstractSocket.ClosingState: "Closing Connection",
}
status = QAbstractSocket.SocketState

class Commands:
    """
    Commands Class for Marcos-Server
    """
    fpgaClock = 'fpga_clk' # array of 3 values unsigned int (clock words)
    localOscillatorFrequency = 'lo_freq' # unsigned int (local oscillator freq. for TX/RX)
    txClockDivider = 'tx_div' # unsigned int (clock divider for RF TX samples)
    rfAmplitude = 'rf_amp' # unsigned int 16 bit (RF amplitude)
    rxRate = 'rx_rate' # unsigned int 16 bit (tx sample rate???)
    txSampleSize = 'tx_size' # unsigned int 16 bit (number of TX samples to return)
    txSamplesPerPulse = 'tx_size' # unsigned int (number of TX samples per pulse)
    gradientOffsetX = 'grad_offs_x' # unsigned int (X gradient channel shim)
    gradientOffsetY = 'grad_offs_y' # unsigned int (Y gradient channel shim)
    gradientOffsetZ = 'grad_offs_z' # unsigned int (Z gradient channel shim)
    gradientMemoryX = 'grad_mem_x' # binary byte array (write X gradient channel memory)
    gradientMemoryY = 'grad_mem_y' # binary byte array (write Y gradient channel memory)
    gradientMemoryZ = 'grad_mem_z' # binary byte array (write Z gradient channel memory)
    recomputeTxPulses = 'recomp_pul' # boolean (recompute the TX pulses)
    txRfWaveform = 'raw_tx_data' # binary byte array (write the RF waveform)
    sequenceData = 'seq_data' # binary byte array (pulse sequence instructions)
    runAcquisition = 'acq' # unsigned int [samples] (runs 'seq_data' and returns array of 64-bit complex floats, length = samples)
    testRxThroughput = 'test_throughput' # unsigned int [arg] (return array map, array-length = arg)


class CommunicationManager(QTcpSocket, QObject):
    """
    Communication Manager Class
    """
    statusChanged = pyqtSignal(str, name='onStatusChanged')

    def __init__(self):
        super(CommunicationManager, self).__init__()

        self.stateChanged.connect(self.getConnectionStatus)

    def connectClient(self, ip: str) -> [bool, int]:
        """
        Connect server and host through server's ip
        @param ip:  IP address of the server
        @return:    success of connection
        """
        self.connectToHost(ip, 1001)
        self.waitForConnected(1000)
        if self.state() == QAbstractSocket.ConnectedState:
            print("Connection to server established.")
            return True
        else:
            return False

    def disconnectClient(self) -> bool:
        """
        Disconnects server and host
        @return:    success of disconnection
        """
        self.disconnectFromHost()
        if self.state() is QAbstractSocket.UnconnectedState:
            print("Disconnected from server.")
            return True
        else:
            return False

    @pyqtSlot(status)
    def getConnectionStatus(self, state: status = None) -> None:
        if state in states:
            self.statusChanged.emit(states[state])
        else:
            self.statusChanged.emit(str(state))

    def waitForTransmission(self) -> None:
        """
        Wait until bytes are written on server
        @return:    None
        """
        while True:
            if not self.waitForBytesWritten():
                break

    def sendMsgPack(self, commands: dict = None):
        # TODO: Check if all commands are valid
        packet = sc.construct_packet(commands)
        response = sc.send_packet(packet, self)
        # return np.frombuffer(response[4]['acq'], np.complex64)
        print(response)

    def setSequence(self, bytearr_sequence: bytearray) -> bool:
        """
        Upload a sequence file to the server
        @param bytearr_sequence:    Byte array to be uploaded
        @return:                    None
        """
        self.write(struct.pack('<I', 4 << 28))
        self.write(bytearr_sequence)

        while True:  # Wait until bytes written
            if not self.waitForBytesWritten():
                break
            # TODO: Include condition to break loop after certain time -> return false

        return True

    def setFrequency(self, freq: float) -> None:
        """
        Set excitation frequency on the server
        @param freq:    Frequency in MHz
        @return:        None
        """
        self.write(struct.pack('<I', 2 << 28 | int(1.0e6 * freq)))
        print("Set frequency!")

    def setAttenuation(self, at) -> None:
        """
        Set attenuation value on the server
        @param at:      Attenuation in dB
        @return:        None
        """
        self.write(struct.pack('<I', 3 << 28 | int(abs(at) / 0.25)))
        print("Set attenuation!")

    def setGradients(self, gx=None, gy=None, gz=None, gz2=None) -> None:
        """
        Set gradient offset on the server
        @param gx:      X-gradient, offset in mA
        @param gy:      Y-gradient, offset in mA
        @param gz:      Z-gradient, offset in mA
        @param gz2:     Z2-gradient, offset in mA
        @return:        None
        """
        if gx is not None:
            if np.sign(gx) < 0:
                sign = 1
            else:
                sign = 0
            self.write(struct.pack('<I', 5 << 28 | grads.X << 24 | sign << 20 | abs(gx)))
        if gy is not None:
            if np.sign(gy) < 0:
                sign = 1
            else:
                sign = 0
            self.write(struct.pack('<I', 5 << 28 | grads.Y << 24 | sign << 20 | abs(gy)))
        if gz is not None:
            if np.sign(gz) < 0:
                sign = 1
            else:
                sign = 0
            self.write(struct.pack('<I', 5 << 28 | grads.Z << 24 | sign << 20 | abs(gz)))
        if gz2 is not None:
            if np.sign(gz2) < 0:
                sign = 1
            else:
                sign = 0
            self.write(struct.pack('<I', 5 << 28 | grads.Z2 << 24 | sign << 20 | abs(gz2)))

        while True:  # Wait until bytes written
            if not self.waitForBytesWritten():
                break

    def acquireSpectrum(self) -> None:
        """
        Trigger spectrum acquisition
        @return:    None
        """
        self.write(struct.pack('<I', 1 << 28))

    def acquireProjection(self, p_axis: int) -> None:
        """
        Trigger projection acquisition
        @param p_axis:    Axis of projection (property)
        @return:        None
        """
        if p_axis is not pax.x or pax.y or pax.z:
            return
        else:
            self.write(struct.pack('<I', 7 << 28 | p_axis))

    def acquireImage(self, p_npe: int = 64, p_tr: int = 4000) -> None:
        """
        Trigger image acquisition
        @param p_npe:   Number of phase encoding steps (property)
        @param p_tr:    Repetition time in ms (property)
        @return:        None
        """
        self.write(struct.pack('<I', 6 << 28 | p_npe << 16 | p_tr))

    def readAcquisitionData(self, size: int) -> np.complex64:
        """
        Perform a readout by receiving acquired data from server
        @param size:    Size of byte array to be read
        @return:        Complex data
        """
        buffer = bytearray(8 * size)
        while True:  # Read data
            self.waitForReadyRead()
            datasize = self.bytesAvailable()
            # print(datasize)
            time.sleep(0.0001)
            if datasize == 8 * size:
                print("Readout finished : ", datasize)
                buffer[0:8 * size] = self.read(8 * size)
                return np.frombuffer(buffer)
            else:
                continue


Com = CommunicationManager()
