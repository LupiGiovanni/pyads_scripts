import time
import struct
from datetime import datetime
import pyads
import pylot

PLC_NET_ID = "5.36.211.100.1.1"
PLC_IP = "192.168.34.130"

SETTLE = 2.0      # secondi di attesa a ogni percentuale prima di leggere
STOP_WAIT = 2.0   # secondi di attesa dopo lo stop, per ripartire da fermo

plc = pyads.Connection(PLC_NET_ID, 851, PLC_IP)
nc = pyads.Connection(PLC_NET_ID, 500, PLC_IP)
plc.open()
nc.open()

axis_id = plc.read_by_name("MAIN.axis_rot.NcToPlc.AxisId", pyads.PLCTYPE_UDINT)
print("ID asse:", axis_id)

# Index group
AXIS = 0x4200 + axis_id
DRIVE = 0x7100 + axis_id

# Index offset
START = 0x26
STOP = 0x27
PERCENTAGE_READ = 0x03

TYPE = 1   # 1 = percento, 2 = velocita'

filename = "velocity_curve_RS40_" + datetime.now().strftime("%Y-%m-%d_%H-%M") + ".csv"

try:
    with open(filename, "w") as f:
        f.write("output_percent,actual_velo\n")

        pylot.set_velocity(plc, 5.0)
        pylot.move_wait_rotational_axis(plc, 3.0)

        for percentage in range(1, 101):
            mypack = struct.pack("<IId", TYPE, 0, float(percentage))
            pylot.write_into_memory(nc, AXIS, START, mypack)

            time.sleep(SETTLE)

            percentage_val = nc.read(DRIVE, PERCENTAGE_READ, pyads.PLCTYPE_LREAL) * 100
            actual_velo_val = plc.read_by_name("MAIN.axis_rot.NcToPlc.ActVelo", pyads.PLCTYPE_LREAL)
            print("Output:", percentage_val, "%  Actual velocity:", actual_velo_val)

            f.write(f"{percentage_val},{actual_velo_val}\n")

            pylot.write_into_memory(nc, AXIS, STOP, b"")   # nessun dato
            time.sleep(STOP_WAIT)

finally:
    pylot.write_into_memory(nc, AXIS, STOP, b"")   # nessun dato
    plc.close()
    nc.close()
