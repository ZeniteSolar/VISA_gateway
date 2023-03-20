#
# Implementation for the load Keithley 2380-500-15
#

# Imports
import pyvisa
import time
import numpy
# Typing
from typing import List
from enum import Enum

class LoadModes(Enum):
	UNDEFINED = 0
	CC = 1
	CV = 2
	CR = 3
	CW = 4

class Load:
	def __init__(self, resource: str, timeout: int = 25000) -> None:
		# Creates a resource manager
		res_manager = pyvisa.ResourceManager("@py")
		# Inits a session
		self.session = res_manager.open_resource(resource)
		# Termination config
		self.session.read_termination='\n'
		self.session.write_termination='\n'
		# Timeout
		self.session.timeout = timeout
		# Current source mode
		# Identifies the load
		print(f"Session open with device: {self.identity()}")
		# Enable remote configuration
		self.configure([
			"*RST",
			":SEL:CLR",
			":SYST:REM"
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
		# Waits 700ms
		time.sleep(0.7)

	def using_as(self) -> LoadModes:
		mode = self.query(":FUNC?")
		# Selects the correct mode
		if mode == "CURRENT":
			return LoadModes.CC
		elif mode == "VOLTAGE":
			return LoadModes.CV
		elif mode == "RESISTANCE":
			return LoadModes.CR
		elif mode == "POWER":
			return LoadModes.CW
		else:
			return LoadModes.UNDEFINED

	def use_as(self, mode: LoadModes) -> None:
		# Init as null value
		mode_str: str = ""
		# Selects the correct mode
		if mode == LoadModes.CC:
			mode_str = "CURR"
		elif mode == LoadModes.CV:
			mode_str = "VOLT"
		elif mode == LoadModes.CR:
			mode_str = "RES"
		elif mode == LoadModes.CW:
			mode_str = "POW"
		# If no valid value was provided blocks the command
		if not mode_str:
			return
		# Configures the load
		self.write_config(f"FUNC {mode_str}")

	def set_level(self, level: float) -> None:
		# Fetch current mode
		mode = self.using_as()
		# Clamp val
		command = ""
		# Clamp the val
		if mode == LoadModes.CC:
			level = numpy.clip(level, 0.0, 15.0)
			command = f":CURR:LEV {numpy.round(level, 4)}"
		elif mode == LoadModes.CV:
			level = numpy.clip(level, 0.1, 400.0)
			command = f":VOLT:LEV {numpy.round(level, 4)}"
		elif mode == LoadModes.CR:
			level = numpy.clip(level, 0.3, 7500.0)
			command = f":RES:LEV {numpy.round(level, 4)}"
		elif mode == LoadModes.CW:
			level = numpy.clip(level, 0.0, 200.0)
			command = f":POW:LEV {numpy.round(level, 4)}"
		else:
			return
		self.write_config(command)

	def input_on(self) -> None:
		self.write_config(":INP 1")

	def input_off(self) -> None:
		self.write_config(":INP 0")

	def configure(self, commands: List[ str ]) -> None:
		for cmd in commands:
			self.write_config(cmd)
