# Instruments
import serial
from meters.dmm_4050 import Meter as DMM4050
from loads.keithley_2380_500_15 import Load as Keithley, LoadModes as KeithleyModes
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
serial_regex = re.compile('avg: ([+-]?[0-9]+\.[0-9]+)')

# Creates load and set to constant voltage
load = Keithley("USB0::1510::9088::802440052777070006::0::INSTR")
load.use_as(KeithleyModes.CV)
load.set_level(0.0)
load.input_on()

# Creates a meter
meter = DMM4050("192.168.0.185")

#
# Log file
#

# Finds correct log file
log_file: str = "./output/" + time.strftime("%Y%m%d-%H%M%S") + ".csv"

# Open the log file
print(f"Selected logfile: {log_file}")
f_log_file = open(log_file, "x")

# Header
f_log_file.write("Time,Adc,Vdc\n")

#
# Measuring loop
#

try:
	for i in np.linspace(0, 70, 150):
		# Set current level
		load.set_level(i)
		# Stops 500ms
		time.sleep(2)
		# Reads at least 5 samples
		adc_samples = []
		for i in range(5):
			data = serial_con.readline().decode("ascii")
			res = serial_regex.findall(data)
			if (len(res) > 0):
				avg = float(res[0])
				adc_samples.append(avg)
		# Reads the multimeter data
		data = meter.measure_sync()
		print(data)
		# Calculates the ADC average
		adc_avg = np.average(adc_samples)
		# Writes in the file
		f_log_file.write(str(time.time()) + ',' + str(adc_avg) + ',' + str(data[1]) + '\n')
		f_log_file.flush()
except KeyboardInterrupt:
	pass

# Turns off the load input
load.input_off()

print("Closing log file")
f_log_file.close()
