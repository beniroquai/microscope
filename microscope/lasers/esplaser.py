#!/usr/bin/env python3

## Copyright (C) 2020 David Miguel Susano Pinto <carandraug@gmail.com>
## Copyright (C) 2020 Julio Mateos Langerak <julio.mateos-langerak@igh.cnrs.fr>
## Copyright (C) 2020 Mick Phillips <mick.phillips@gmail.com>
##
## This file is part of Microscope.
##
## Microscope is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Microscope is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Microscope.  If not, see <http://www.gnu.org/licenses/>.

import logging

import serial

import microscope
import microscope.abc

_logger = logging.getLogger(__name__)


class ESPLaser(microscope.abc.SerialDeviceMixin, microscope.abc.LightSource):
    def __init__(self, com, baud=115200, timeout=0.5, maxpower=100, pwmresolution=2**10, cmdprefix="LASERRED", **kwargs) -> None:
        super().__init__(**kwargs)
        self.connection = serial.Serial(
            port=com,
            baudrate=baud,
            timeout=timeout,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
        )
        # Start a logger.
        self._max_power_mw = float(maxpower) 
        self._cmdprefix = cmdprefix

    def _write(self, command):
        """Send a command."""
        response = self.connection.write(command + b"\r\n")
        return response

    def _readline(self):
        """Read a line from connection without leading and trailing whitespace.
        We override from SerialDeviceMixin
        """
        response = self.connection.readline().strip()
        return response

    def _flush_handshake(self):
        self.connection.readline()

    @microscope.abc.SerialDeviceMixin.lock_comms
    def get_status(self):
        print("We cannot get any status from the ESP ")
        result = None
        return result

    @microscope.abc.SerialDeviceMixin.lock_comms
    def enable(self):
        """Turn the laser ON. Return True if we succeeded, False otherwise."""
        _logger.info("Turning laser ON.")
        return True

    def _do_shutdown(self) -> None:
        self.disable()
        # We set the power to a safe level
        self._set_power_mw(0)
        
    def initialize(self):
        # self.flush_buffer()
        print("Initializiation - Nothing to do here")
        
    @microscope.abc.SerialDeviceMixin.lock_comms
    def disable(self):
        """Turn the laser OFF. Return True if we succeeded, False otherwise."""
        _logger.info("Turning laser OFF.")
        # Turning LASER OFF
        self._set_power_mw(0)
        return True

    @microscope.abc.SerialDeviceMixin.lock_comms
    def is_alive(self):
        self._write(b"*IDN?")
        reply = self._readline()
        # 'Coherent, Inc-<model name>-<firmware version>-<firmware date>'
        return reply.startswith(b"Coherent, Inc-")

    @microscope.abc.SerialDeviceMixin.lock_comms
    def get_is_on(self):
        """Return True if the laser is currently able to produce light."""
        self._write(b"SOURce:AM:STATe?")
        response = self._readline()
        _logger.info("Are we on? [%s]", response.decode())
        return response == b"ON"

    @microscope.abc.SerialDeviceMixin.lock_comms
    def _get_power_mw(self):
        if not self.get_is_on():
            return 0.0
        self._write(b"SOURce:POWer:LEVel?")
        response = self._readline()
        return float(response.decode())

    @microscope.abc.SerialDeviceMixin.lock_comms
    def _set_power_mw(self, mw):
        power_w = mw 
        _logger.info("Setting laser power to %.7sW", power_w)
        self._write(b(self._cmdprefix)+LASERINTENSITY%.5f" % power_w)
        self._flush_handshake()

    def _do_set_power(self, power: float) -> None:
        self._set_power_mw(power * self._max_power_mw)

    def _do_get_power(self) -> float:
        return self._get_power_mw() / self._max_power_mw
