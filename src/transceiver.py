"""
The MIT License (MIT)

Copyright (C) 2017 Fabian Schöttler @ FH Aachen

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the “Software”),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import threading
from queue import Queue

import serial

from imcp import IMCP, IMCPpacket


class Transceiver:
    def __init__(self, main):
        self.main = main
        self.ser = None
        self.worker = None
        self.sio_status = 'down'

        self.cmd_buffer = Queue()
        self.imcp = IMCP(self)

        self._on_packet_complete = None

        self.packet_rx = IMCPpacket()

    def open(self, device, baudrate):
        """
        Open a connection to the given serial device with specified
         baud rate.

        Args:
            device: name of serial device to be opened
            baudrate: communication speed for connection as integer

        Returns:
            True on successful connection
            False otherwise
        """
        if self.ser is not None or self.sio_status != 'down':
            print("ERR - Serial connection already up")
            return True

        try:
            self.ser = serial.Serial(
                device,
                baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                timeout=0.01)
        except serial.SerialException:
            print('ERR - Port not available')
            self.ser = None
            self.sio_status = 'down'
            return False

        self.sio_status = 'up'
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        try:
            self.worker = threading.Thread(target=self.serial_io)
            self.worker.start()
        except threading.ThreadError:
            print("ERR - Worker not started correctly")
            self.worker = None
            return False
        return True

    def close(self):
        """
        Close an open connection to the active serial device, if one.
        Waits for all buffers to be regular empty, especially the
        command and realtime buffers.
        After all buffers are empty and the io thread joined,
        the connection will be closed.

        Returns: nothing
        """
        if self.ser is None:
            return
        self.sio_status = 'shutdown'
        self.worker.join()
        self.worker = None
        self.sio_status = 'down'
        self.ser.close()
        self.ser = None
        print("Serial closed")

    def bind_packet_complete_callback(self, callback):
        """
        Bind the given callback, executed on received messages
        :param callback: Callback function to be executed on received messages, callback(data) -> None
        :return: Nothing
        """
        self._on_packet_complete = callback

    def serial_io(self):
        """
        The worker for serial communication. Should run as separate
        thread, started after successful connection to serial device.

        Returns: nothing
        """
        self.sio_status = 'active'

        while self.worker and self.sio_status != 'shutdown':
            # read messages from machine
            data = self.ser.read(8)
            if len(data) != 0:
                if self.imcp.receive(self.packet_rx, data)[0] and self.packet_rx.length > 0:
                    if self._on_packet_complete is not None:
                        self._on_packet_complete(self.packet_rx)
                    self.packet_rx.clear()

    def transmit(self, cmd):
        if isinstance(cmd, IMCPpacket):
            num = self.ser.write(self.imcp.transmit(cmd))
            self.main.frontend.changed_cnt_tx.emit(num)
