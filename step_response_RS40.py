import time
import pyads
import pylot
from datetime import datetime

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

plc = pyads.Connection(plc_netid, plc_port, plc_ip)
plc.open()

stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
filename = f"step_response_RS40_{stamp}.csv"

def step_and_record(plc, step_degrees):
    start_pos = plc.read_by_name("MAIN.axis_rot.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
    pylot.move_rotational_axis(plc, step_degrees)
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 3.0:
        set_pos = plc.read_by_name("MAIN.axis_rot.NcToPlc.SetPos", pyads.PLCTYPE_LREAL)
        actual_pos = plc.read_by_name("MAIN.axis_rot.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
        following_error = plc.read_by_name("MAIN.axis_rot.NcToPlc.PosDiff", pyads.PLCTYPE_LREAL)
        f.write(f"{start_pos},{time.perf_counter() - t0},{set_pos},{actual_pos},{following_error}\n")

try:
    with open(filename, "w") as f:
        f.write("start_pos,time,set_pos,actual_pos,following_error\n")

        # setting velocity
        pylot.set_velocity(plc, 5.0)
        step_size = 5 # degrees

        for i in range(30):
            time.sleep(3)
            step_and_record(plc, step_size)
            pylot.wait_for_movement_done(plc)

finally:
    plc.close()
