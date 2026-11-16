import sys
import time
import pyads
from datetime import datetime 

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

plc = pyads.Connection(plc_netid, plc_port, plc_ip)
plc.open()

stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

f = open(f"LS270_acceleration_test_{stamp}.csv", "w")
f.write("start_x,time,set_x,actual_x,following_error\n")