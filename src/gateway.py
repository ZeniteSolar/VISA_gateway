# Instruments
import serial
from meters.dmm_4050 import Meter as DMM4050
# Time
import time
# Regex
import re
# Math
import numpy as np

#
# Instruments connections
#

# Creates a serial connection
serial_con = serial.serial_for_url(
	"spy:///dev/ttyACM0",
	baudrate = 115200,
	parity = serial.PARITY_NONE,
	stopbits = serial.STOPBITS_ONE,
	bytesize = serial.EIGHTBITS,
	timeout = 1
)
# Creates a regex for the serial data
serial_regex = re.compile('millis: ([0-9]+), batata: ([+-]?[0-9]+\.[0-9]+), freq: ([+-]?[0-9]+\.[0-9]+), v_pa: ([+-]?[0-9]+\.[0-9]+), i_pa: ([+-]?[0-9]+\.[0-9]+), v_ba: ([+-]?[0-9]+\.[0-9]+), i_ba: ([+-]?[0-9]+\.[0-9]+)')

# Starts the session
meter_ba = DMM4050("192.168.0.185")
meter_pa = DMM4050("192.168.0.174")

#
# Log file
#

# Finds correct log file
log_file: str = "./output/" + time.strftime("%Y%m%d-%H%M%S") + ".csv"

# Open the log file
print(f"Selected logfile: {log_file}")
f_log_file = open(log_file, "x")

# Header
f_log_file.write("time,millis,duty,freq,v_pa,i_pa,v_ba,i_ba,meter_v_pa,meter_i_pa,meter_v_ba,meter_i_ba\n")

#
# Measuring loop
#

def get_board_metrics():
	res = None
	while not res:
		# Read the serial
		data = serial_con.readline().decode("ascii")
		print(data)
		# Applies the regex
		res = serial_regex.findall(data)
		# If parsed data
		if (len(res) > 0):
			# Extracts the first to parse as int
			data = res[0]
			# Parses millis as int
			millis = int(data[0])
			# Parse all other values as floats
			res = [ millis ] + [ float(i) for i in res[0][1:] ]
		else:
			res = None
	return res

try:
	while True:
		print("RESET THE DEVICE")
		time.sleep(0.5)
except KeyboardInterrupt:
	time.sleep(1)

try:
	while True:
		# Fetches details from board
		[ millis, duty, freq, v_pa, i_pa, v_ba, i_ba ] = get_board_metrics()
		# Trigger both meters
		meter_pa.write(":INIT")
		meter_ba.write(":INIT")
		# Waits 300ms to fetch the measurement
		time.sleep(0.3)
		# Fetch the data
		[ meter_i_pa, meter_v_pa ] = meter_pa.measure_sync()
		[ meter_i_ba, meter_v_ba ] = meter_ba.measure_sync()
		# Write in the log
		f_log_file.write(
			f"{time.time()},{millis},{duty},{freq},{v_pa},{i_pa},{v_ba},{i_ba},{meter_v_pa},{meter_i_pa},{meter_v_ba},{meter_i_ba}\n"
		)
		f_log_file.flush()
except KeyboardInterrupt:
	pass

print("Closing log file")
f_log_file.close()
