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
from globalvars import grads, pax
from parameters import params
import numpy as np
import struct
import time

tcp = QTcpSocket()
connected = QAbstractSocket.ConnectedState
unconnected = QAbstractSocket.UnconnectedState

class CommunicationManager():
    """
    Communication Manager Class
    """
    @staticmethod
    def connectClient(ip: str) -> [bool, int]:
        """
        Connect server and host through server's ip
        @param ip:  IP address of the server
        @return:    Connection state
        """
        tcp.connectToHost(ip, 1001)
        tcp.waitForConnected(1000)

        if tcp.state() == connected:
            print("Connection to server established.")
            return True
        elif tcp.state() == unconnected:
            print("Connection to server failed.")
            return False
        else:
            print("TCP socket in state : ", tcp.state())
            return [False, tcp.state()]

    ##  Documentation of a method.
    #   Disconnects server and client
    @staticmethod
    def disconnectClient() -> None:
        """
        Disconnects server and host
        @return:    None
        """
        tcp.disconnectFromHost()
        if tcp.state() is unconnected:
            print("Disconnected from server.")
        else:
            print("Connection to server still established.")

    @staticmethod
    def waitForTransmission() -> None:
        """
        Wait until bytes are written on server
        @return:    None
        """
        while True:
            if not tcp.waitForBytesWritten():
                break

    ##  Documentation of a method.
    #   @param byte_arr_sequence    Sequence as byte array
    @staticmethod
    def setSequence(bytearr_sequence: bytearray) -> bool:
        """
        Upload a sequence file to the server
        @param bytearr_sequence:    Byte array to be uploaded
        @return:                    None
        """
        tcp.write(struct.pack('<I', 4 << 28))
        tcp.write(bytearr_sequence)

        while True:  # Wait until bytes written
            if not tcp.waitForBytesWritten():
                break
            # TODO: Include condition to break loop after certain time -> return false

        return True

    @staticmethod
    def setFrequency(freq: float) -> None:
        """
        Set excitation frequency on the server
        @param freq:    Frequency in MHz
        @return:        None
        """
        params.freq = freq
        tcp.write(struct.pack('<I', 2 << 28 | int(1.0e6 * freq)))
        print("Set frequency!")

    # Function to set attenuation
    @staticmethod
    def setAttenuation(at) -> None:
        """
        Set attenuation value on the server
        @param at:      Attenuation in dB
        @return:        None
        """
        params.at = at
        tcp.write(struct.pack('<I', 3 << 28 | int(abs(at) / 0.25)))
        print("Set attenuation!")

    @staticmethod
    def setGradients(gx=None, gy=None, gz=None, gz2=None) -> None:
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
            tcp.write(struct.pack('<I', 5 << 28 | grads.X << 24 | sign << 20 | abs(gx)))
        if gy is not None:
            if np.sign(gy) < 0:
                sign = 1
            else:
                sign = 0
            tcp.write(struct.pack('<I', 5 << 28 | grads.Y << 24 | sign << 20 | abs(gy)))
        if gz is not None:
            if np.sign(gz) < 0:
                sign = 1
            else:
                sign = 0
            tcp.write(struct.pack('<I', 5 << 28 | grads.Z << 24 | sign << 20 | abs(gz)))
        if gz2 is not None:
            if np.sign(gz2) < 0:
                sign = 1
            else:
                sign = 0
            tcp.write(struct.pack('<I', 5 << 28 | grads.Z2 << 24 | sign << 20 | abs(gz2)))

        while True:  # Wait until bytes written
            if not tcp.waitForBytesWritten():
                break

    @staticmethod
    def acquireSpectrum() -> None:
        """
        Trigger spectrum acquisition
        @return:    None
        """
        tcp.write(struct.pack('<I', 1 << 28))

    @staticmethod
    def acquireProjection(p_axis: int) -> None:
        """
        Trigger projection acquisition
        @param p_axis:    Axis of projection (property)
        @return:        None
        """
        if p_axis is not pax.x or pax.y or pax.z:
            return
        else:
            tcp.write(struct.pack('<I', 7 << 28 | p_axis))

    @staticmethod
    def acquireImage(p_npe: int = 64, p_tr: int = 4000) -> None:
        """
        Trigger image acquisition
        @param p_npe:   Number of phase encoding steps (property)
        @param p_tr:    Repetition time in ms (property)
        @return:        None
        """
        tcp.write(struct.pack('<I', 6 << 28 | p_npe << 16 | p_tr))

    @staticmethod
    def readData(size: int) -> np.complex64:
        """
        Perform a readout by receiving acquired data from server
        @param size:    Size of byte array to be read
        @return:        Complex data
        """
        buffer = bytearray(8 * size)
        while True:  # Read data
            tcp.waitForReadyRead()
            datasize = tcp.bytesAvailable()
            # print(datasize)
            time.sleep(0.0001)
            if datasize == 8 * size:
                print("Readout finished : ", datasize)
                buffer[0:8 * size] = tcp.read(8 * size)
                return np.frombuffer(buffer)
            else:
                continue


Com = CommunicationManager()
