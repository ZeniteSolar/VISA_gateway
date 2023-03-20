# Load
from loads.keithley_2380_500_15 import Load as Keithley, LoadModes as KeithleyModes
# Time
import time

#
# Example start point
#
def start() -> None:
	# Use a valid resource from the discovery examples
	# if list_resources is empty, maybe its related with
	# the rules
	load = Keithley("USB0::1510::9088::802440052777070006::0::INSTR")

	# Identity
	print(load.identity())

	# Current mode
	print(load.using_as())

	# Selects a new mode (Constant current)
	print(load.use_as(KeithleyModes.CC))

	# Set to 10A
	print(load.set_level(10))

	# Turns the input on
	load.input_on()

	# Waits 10s
	time.sleep(10)

	# Turns the input off
	load.input_off()

# Starts the gateway
start()
