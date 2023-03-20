
#
# Implementation for the power analyzer PA1000
#

# Imports
import pyvisa
import time
import numpy
# Typing
from typing import List, Optional, Tuple
from enum import Enum

class Meter:
	def __init__(self, ip_addr: str, timeout: int = 25000) -> None:
		# Creates a resource manager
		res_manager = pyvisa.ResourceManager("@py")
		# Inits a session
		self.session = res_manager.open_resource(f"TCPIP0::{ip_addr}::3490::SOCKET")
		# Termination config
		self.session.read_termination='\n'
		self.session.write_termination='\n'
		# Timeout
		self.session.timeout = timeout
		# Current source mode
		# Identifies the load
		print(f"Session open with device: {self.identity()}")
		# Default configs
		self.configure([
			"*CLS",
			"SYST:REM",
			"Ethernet",
			"SENSE:FUNC1 \"CURR:DC\"",
			"SENSE:FUNC2 \"VOLT:DC\"",
			"SENSE:VOLT:RANG:AUTO ON",
			"SENSE:CURR:RANG:AUTO ON",
			"SENS:DET:BAND MIN",
			"SENS:CURR:DC:FILT:STAT ON",
			"SENS:VOLT:DC:FILT:STAT ON",
			"SENS:ZERO:AUTO 1",
			"TRIG:SOUR IMM",
			"TRIG:DEL 0",
			"TRIG:COUN 1",
			"SAMP:COUN 1",
			"DISP OFF",
			":INIT",
		])

	def __del__(self) -> None:
		print(f"Session close with device: {self.identity()}")
		self.session.close()

	def write(self, command: str) -> None:
		self.session.write(command)

	def read(self) -> None:
		self.session.read()

	def query(self, command: str) -> None:
		return self.session.query(command)

	def identity(self) -> str:
		return self.query("*IDN?")

	def write_config(self, command: str) -> None:
		self.write(command)
		# Waits 300ms
		time.sleep(0.3)

	def measure_sync(self) -> List[ float ]:
		res = []
		while True:
			status = int(self.query("*OPC?"))
			if status == 1:
				raw_data = [ self.query(":FETC1?").replace("\r", ""), self.query(":FETC2?").replace("\r", "") ]
				res = [float(i) for i in raw_data]
				self.write_config(":INIT")
				break
			time.sleep(0.1)
		return res

	def filter_analog_on(self) -> None:
		self.write_config("SENS:DET:BAND MIN")
		self.write_config("SENS:CURR:DC:FILT:STAT ON")
		self.write_config("SENS:VOLT:DC:FILT:STAT ON")

	def filter_analog_off(self) -> None:
		self.write_config("SENS:CURR:DC:FILT:STAT OFF")
		self.write_config("SENS:VOLT:DC:FILT:STAT OFF")

	def filter_digital_on(self) -> None:
		self.write_config("SENS:CURR:DC:FILT:DIG ON")
		self.write_config("SENS:VOLT:DC:FILT:DIG ON")

	def filter_digital_off(self) -> None:
		self.write_config("SENS:CURR:DC:FILT:DIG OFF")
		self.write_config("SENS:VOLT:DC:FILT:DIG OFF")

	def set_sample_count(self, samples: int) -> None:
		samples = numpy.clip(samples, 1, 5000)
		self.write_config(f"SAMP:COUN {samples}")

	def configure(self, commands: List[ str ]) -> None:
		for cmd in commands:
			self.write_config(cmd)
