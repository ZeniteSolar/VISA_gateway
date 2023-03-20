# Loads
from meters.pa_1000 import Meter as PA1000, MeterMetrics as PA1000Metrics, MeterShunts as PA1000Shunts

#
# Example start point
#
def start() -> None:
	# Starts the session
	meter = PA1000("192.168.0.108")
	# Selects Voltage and Current metrics with auto range
	meter.sel_metric([
		(PA1000Metrics.VDC, True),
		(PA1000Metrics.ADC, True),
	])
	# Selects 20A shunt
	meter.sel_shunt(PA1000Shunts.INT20A)

	# Make some async measure or none
	for _i in range(1000):
		print(meter.measure_or_none())

	# Make some sync measure
	for _i in range(10):
		print(meter.measure_sync())

# Starts the gateway
start()