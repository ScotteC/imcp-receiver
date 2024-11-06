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


class Interpreter:

    def __init__(self, main):
        self.main = main
        self.time = 0

        self.a = 0.0
        self.b = 0.0
        self.c = 0.0
        self.d = 0.0

        # self.x = 0.0
        # self.y = 0.0
        # self.z = 0.0
        # self.r = 0.0


    def interpret(self, packet):
        self.time = int.from_bytes(packet.data[0:4], byteorder='big', signed=False)

        self.a = struct.unpack('>f', packet.data[4:8])
        self.b = struct.unpack('>f', packet.data[8:12])
        self.c = struct.unpack('>f', packet.data[12:16])
        self.d = struct.unpack('>f', packet.data[16:20])

        # print(f"{self.time:} : ( {self.a[0]: 9.4f} / {self.b[0]: 9.4f} / {self.c[0]: 9.4f} ) , r: {self.d[0]:9.4f}")
        # print("{:11d} : ( {: 9.4f} / {: 9.4f} / {: 9.4f} ) , r: {:9.4f}\r".format(
        #     self.time, self.a[0], self.b[0], self.c[0], self.d[0]
        # ))

        print(self.time, self.a[0], self.b[0], self.c[0], self.d[0], sep=',', end='\r')

        # self.x = struct.unpack('f', packet.data[5:9])
        # self.y = struct.unpack('f', packet.data[5:9])
        # self.z = struct.unpack('f', packet.data[5:9])
        # self.r = struct.unpack('f', packet.data[5:9])
