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

import struct


class IMCPpacket:
    """

    """
    def __init__(self, dst=0, src=0):
        self.destination = dst
        self.source = src
        self.length = 0
        self.maxLength = 64
        self.data = bytearray()

    def prepare(self, dst, src):
        self.destination = dst
        self.source = src
        self.length = 3
        self.data.clear()
        return

    def add_uint8(self, val):
        if self.length < self.maxLength:
            self.data += int.to_bytes(val, length=1, byteorder='big', signed=False)
            self.length += 1
        return

    def add_uint16(self, val):
        if self.length < (self.maxLength - 1):
            self.data += int.to_bytes(val, length=2, byteorder='big', signed=False)
            self.length += 2
        return

    def add_unit32(self, val):
        if self.length < (self.maxLength - 3):
            self.data += int.to_bytes(val, length=4, byteorder='big', signed=False)
            self.length += 1
        return

    def dump(self):
        print("Packet: {} -> {} : {}".format(self.source, self.destination, self.length))
        print(self.data.hex())

    def clear(self):
        self.data.clear()
        self.length = 0


class IMCP:

    def __init__(self, serial):
        self.serial = serial

        self.count = 0
        self.state = 0
        self.id = 0x00

        return

    def receive(self, packet: IMCPpacket, data):

        for val in struct.unpack(str(len(data)) + 'c', data):

            # sync
            if self.state == 0:
                if val == bytes([0x16]):
                    self.state = 1

            # stx
            elif self.state == 1:

                if val == bytes([0x02]):
                    self.count = 0
                    packet.data.clear()
                    self.state = 2

                elif val == bytes([0x16]):
                    self.state = 1

                else:
                    self.state = 0

            # length
            elif self.state == 2:
                length = int.from_bytes(val, byteorder='big')
                if length > packet.maxLength:
                    self.state = 0
                else:
                    packet.length = length
                    self.count += 1
                    self.state = 3

            # destination
            elif self.state == 3:
                if val == bytes([self.id]) or val == bytes([0xFF]):
                    packet.destination = int.from_bytes(val, byteorder='big')
                    self.count += 1
                    self.state = 4
                else:
                    self.state = 0

            # source
            elif self.state == 4:
                packet.source = int.from_bytes(val, byteorder='big')
                self.count += 1
                self.state = 5

            # data
            elif self.state == 5:
                packet.data += val
                self.count += 1

                if self.count == packet.length:
                    self.state = 0
                    return [True, self.state]

        return [False, self.state]

    def transmit(self, packet: IMCPpacket):
        data = bytes([0x16, 0x02, packet.length, packet.destination, packet.source])
        data += packet.data
        return data
