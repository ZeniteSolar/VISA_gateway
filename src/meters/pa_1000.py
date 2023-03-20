
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

class MeterMetrics(Enum):
	UNDEFINED = 0,
	VDC = 1, # Voltage DC
	ADC = 2, # Current DC

class MeterShunts(Enum):
	UNDEFINED = 0,
	INT20A = 1, # Internal 20A
	INT1A = 2, # Internal 1A
	EXT = 2, # External

class Meter:
	def __init__(self, ip_addr: str, timeout: int = 25000) -> None:
		# Creates a resource manager
		res_manager = pyvisa.ResourceManager("@py")
		# Inits a session
		self.session = res_manager.open_resource(f"TCPIP0::{ip_addr}::5025::SOCKET")
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
			"*RST", # Reset to power on
			":SEL:CLR", # Clear selection
			":INP:FILT:LPAS 1", # Activate low pass filter for voltage measurements
			":BLK:DIS", # Disable blanking
			":AVG 1", # Enables average
			":SYST:ZERO 0", # Disables auto zero
			":DSE 2"
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
		self.query(command)
		# Waits 2s
		time.sleep(2)

	def measure_or_none(self) -> Optional[ List[ float ] ]:
		status = self.query(":DSR?")
		if status == "2":
			raw_data = self.query(":FRD?")
			clean_data = raw_data.replace(' ', '')
			return [float(i) for i in clean_data.split(',')]
		else:
			return None

	def measure_sync(self) -> List[ float ]:
		res = []
		while True:
			status = self.query(":DSR?")
			if status == "2":
				raw_data = self.query(":FRD?")
				clean_data = raw_data.replace(' ', '')
				res = [float(i) for i in clean_data.split(',')]
				break
		return res

	def sel_metric(self, metrics: List[ Tuple[ MeterMetrics, bool, int ] ]) -> None:
		for i in metrics:
			sel_command: str = ""
			range_command: str = ""
			if i[0] == MeterMetrics.VDC:
				sel_command = ":SEL:VDC"
				range_command = ":RNG:VTL"
			elif i[0] == MeterMetrics.ADC:
				sel_command = ":SEL:ADC"
				range_command = ":RNG:AMP"
			else:
				continue
			if sel_command:
				self.write_config(sel_command)
			if i[1] or len(i) < 3:
				self.write_config(range_command + ":AUT")
			else:
				fixed: int = numpy.round(numpy.clip(i[2], 1, 10))
				self.write_config(range_command + f":FIX {fixed}")

	def sel_shunt(self, shunt: MeterShunts) -> None:
		command: str = ""
		if shunt == MeterShunts.INT20A:
			command = ":SHU:INT"
		elif shunt == MeterShunts.INT1A:
			command = ":SHU:INT1A"
		elif shunt == MeterShunts.EXT:
			command = ":SHU:EXT"
		else:
			return
		if command:
			self.write_config(command)

	def get_metrics(self) -> List[ MeterMetrics ]:
		data = self.query(":FRF?").split(',')[2::]
		return [ MeterMetrics.ADC if i == "adc" else MeterMetrics.VDC if i == "vdc" else MeterMetrics.UNDEFINED for i in [ j.lower() for j in data ] ]

	def low_pass_filter_on(self) -> None:
		self.write_config(":INP:FILT:LPAS 1")

	def low_pass_filter_off(self) -> None:
		self.write_config(":INP:FILT:LPAS 0")

	def average_on(self) -> None:
		self.write_config(":AVG 1")

	def average_off(self) -> None:
		self.write_config(":AVG 0")

	def configure(self, commands: List[ str ]) -> None:
		for cmd in commands:
			self.write_config(cmd)
