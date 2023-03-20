# Imports
import pyvisa
# Typing
from typing import Tuple

#
# Resources discovery
#
def list_resources() -> Tuple[ str ]:
	print("Listing resources...")
	res_manager = pyvisa.ResourceManager("@py")
	return res_manager.list_resources()

