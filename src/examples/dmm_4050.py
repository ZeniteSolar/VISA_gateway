# Loads
from meters.dmm_4050 import Meter as DMM4050

#
# Example start point
#
def start() -> None:
	# Starts the session
	meter = DMM4050("192.168.0.185")

	# Make some async measure or none
	for _i in range(1000):
		print(meter.measure_or_none())

	# Make some sync measure
	for _i in range(10):
		print(meter.measure_sync())

# Starts the gateway
start()