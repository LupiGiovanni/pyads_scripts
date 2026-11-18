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
filename = f"step_response_LS270_{stamp}.csv"

def step_and_record(plc, start_x, step_mm):
    pylot.move_x_axis(plc, start_x + step_mm)
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 4.0:
        set_x = plc.read_by_name("MAIN.axis_x.NcToPlc.SetPos", pyads.PLCTYPE_LREAL)
        actual_x = plc.read_by_name("MAIN.axis_x.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
        following_error = plc.read_by_name("MAIN.axis_x.NcToPlc.PosDiff", pyads.PLCTYPE_LREAL)
        f.write(f"{start_x},{time.perf_counter() - t0},{set_x},{actual_x},{following_error}\n")

try:
    with open(filename, "w") as f:
        f.write("start_x,time,set_x,actual_x,following_error\n")

        # setting velocity
        pylot.set_velocity(plc, 10.0)

        # setting y axis to mid-range position
        pylot.move_home_y_axis(plc)

        positions = [100.0, 300.0, 500.0]
        step_size = 10.0  # mm

        for pos in positions:
            pylot.move_wait_x_axis(plc, pos)
            time.sleep(5)
            step_and_record(plc, pos, step_size)
            pylot.wait_for_movement_done(plc)

        # moving back x axis to mid-range position
        pylot.move_home_x_axis(plc)

finally:
    plc.close()
