#!/usr/bin/env python3
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
import argparse
import signal
import sys
from time import sleep

from transceiver import Transceiver
from interpreter import Interpreter


class App:
    def __init__(self, device='/dev/ttyUSB0', baud=115200):
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

        self.running = True
        self.connection = Transceiver(self)
        self.interpreter = Interpreter(self)
        self.connection.bind_packet_complete_callback(self.interpreter.interpret)
        self.connection.open(device, baud)

    def exit(self, signum, frame):
        self.running = False
        print("Exiting...")

    def exec(self):
        while self.running:
            sleep(1)
        self.connection.close()
        print("Connection closed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple imcp receiver, interpreter and logger')
    parser.add_argument('--device', type=str,
                        default='/dev/ttyUSB0',
                        help='Path to serial device')
    parser.add_argument('--baud', type=int,
                        default=115200,
                        help='Baud rate for serial connection')
    args = parser.parse_args()

    app = App(args.device, args.baud)
    app.exec()
