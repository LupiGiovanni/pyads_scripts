import time
import struct
from datetime import datetime
import pyads
import sys

PLC_NET_ID = "5.36.211.100.1.1"
PLC_IP = "192.168.34.130"

SETTLE = 2.0      # secondi di attesa a ogni percentuale prima di leggere
STOP_WAIT = 2.0   # secondi di attesa dopo lo stop, per ripartire da fermo

plc = pyads.Connection(PLC_NET_ID, 851, PLC_IP)
nc = pyads.Connection(PLC_NET_ID, 500, PLC_IP)
plc.open()
nc.open()

axis_id = plc.read_by_name("MAIN.axis_x.NcToPlc.AxisId", pyads.PLCTYPE_UDINT)
print("ID asse:", axis_id)

# Index group
AXIS = 0x4200 + axis_id
DRIVE = 0x7100 + axis_id 

# Index offset
START = 0x26
STOP = 0x27
PERCENTAGE_READ = 0x03

TYPE = 1   # 1 = percento, 2 = velocita'

filename = "velocity_curve_LS270_" + datetime.now().strftime("%Y-%m-%d_%H-%M") + ".csv"

def write(index_group, index_offset, dati):
    nc.write(index_group, index_offset, dati, pyads.PLCTYPE_BYTE * len(dati))

def move_x_axis(plc, target_x):
    plc.write_by_name("MAIN.target_x", target_x, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)

def move_y_axis(plc, target_y):
    plc.write_by_name("MAIN.target_y", target_y, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)

def wait_for_movement_done(plc):
    time.sleep(0.2)
    state = plc.read_by_name("MAIN.state", pyads.PLCTYPE_INT)
    while state != 0:
        if state == 3:
            print("ERROR")
            f.close()
            plc.close()
            sys.exit(1)
        time.sleep(0.2)
        state = plc.read_by_name("MAIN.state", pyads.PLCTYPE_INT)

try:
    with open(filename, "w") as f:
        f.write("output_percent,actual_velo\n")

        plc.write_by_name("MAIN.velocity", 8.0, pyads.PLCTYPE_LREAL)
        move_x_axis(plc, 300.0)
        move_y_axis(plc, 150.0)
        wait_for_movement_done(plc)

        for percentage in range(1, 101):
            mypack = struct.pack("<IId", TYPE, 0, float(percentage))
            write(AXIS, START, mypack)

            time.sleep(SETTLE)

            percentage_val = nc.read(DRIVE, PERCENTAGE_READ, pyads.PLCTYPE_LREAL) * 100
            actual_velo_val = plc.read_by_name("MAIN.axis_x.NcToPlc.ActVelo", pyads.PLCTYPE_LREAL)
            print("Output:", percentage_val, "%  Actual velocity:", actual_velo_val)

            f.write(f"{percentage_val},{actual_velo_val}\n")

            write(AXIS, STOP, b"")   # nessun dato
            time.sleep(STOP_WAIT)

            move_x_axis(plc, 300)
            wait_for_movement_done(plc)

finally:
    write(AXIS, STOP, b"")   # nessun dato
    plc.close()
    nc.close()