##  @package    communicationhandler
#   @author     David Schote <david.schote@ovgu.de>
#   @date       25.04.2020

# Imports
from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket
from PyQt5.QtCore import pyqtSignal
from globalvars import grads
from parameters import params
import numpy as np
import struct
import time

tcp = QTcpSocket()
connected = QAbstractSocket.ConnectedState
unconnected = QAbstractSocket.UnconnectedState

sequenceLoaded = pyqtSignal()

class CommunicationHandler:

    ##  Documentation of a method.
    #   @param ip   The ip address for the connection
    @staticmethod
    def connectClient(ip: str) -> [bool, int]:
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
        tcp.disconnectFromHost()
        if tcp.state() is unconnected:
            print("Disconnected from server.")
        else:
            print("Connection to server still established.")

    @staticmethod
    def waitForTransmission() -> None:
        while True:
            if not tcp.waitForBytesWritten():
                break

    ##  Documentation of a method.
    #   @param byte_arr_sequence    Sequence as byte array
    @staticmethod
    def setSequence(byte_arr_sequence) -> None:
        tcp.write(struct.pack('<I', 4 << 28))
        tcp.write(byte_arr_sequence)
        while True:  # Wait until bytes written
            if not tcp.waitForBytesWritten():
                break
        sequenceLoaded.emit()

    @staticmethod
    def setFrequency(freq: float) -> None:
        params.freq = freq
        tcp.write(struct.pack('<I', 2 << 28 | int(1.0e6 * freq)))
        print("Set frequency!")

    # Function to set attenuation
    @staticmethod
    def setAttenuation(at) -> None:
        params.at = at
        tcp.write(struct.pack('<I', 3 << 28 | int(abs(at) / 0.25)))
        print("Set attenuation!")

    @staticmethod
    def setGradients(gx=None, gy=None, gz=None, gz2=None) -> None:
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
            # tcp.write(struct.pack('<I', 5 << 28 | grads.Z2 << 24 | sign << 20 | abs(gz2)))

        while True:  # Wait until bytes written
            if not tcp.waitForBytesWritten():
                break

    @staticmethod
    def acquireSpectrum() -> None:
        tcp.write(struct.pack('<I', 1 << 28))

    @staticmethod
    def acquireProjection(axis: int) -> None:
        tcp.write(struct.pack('<I', 7 << 28 | axis))

    @staticmethod
    def acquireImage(npe: int = 64, tr: int = 4000) -> None:
        tcp.write(struct.pack('<I', 6 << 28 | npe << 16 | tr))

    @staticmethod
    def readData(size: int) -> np.complex_64:
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


com: CommunicationHandler = CommunicationHandler()

