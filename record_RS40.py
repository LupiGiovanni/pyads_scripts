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
duration = float(sys.argv[1])

f = open(f"recorded_movement_RS40_{stamp}.csv", "w")
f.write("time,set_pos,actual_pos,following_error\n")

def record ():
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < float(sys.argv[1]):
        t = time.perf_counter() - t0
        set_pos = plc.read_by_name("MAIN.axis_rot.NcToPlc.SetPos", pyads.PLCTYPE_LREAL)
        actual_pos = plc.read_by_name("MAIN.axis_rot.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
        following_error = plc.read_by_name("MAIN.axis_rot.NcToPlc.PosDiff", pyads.PLCTYPE_LREAL)
        f.write(f"{t},{set_pos},{actual_pos},{following_error}\n")

record()