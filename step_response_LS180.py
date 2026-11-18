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
filename = f"step_response_LS180_{stamp}.csv"

def step_and_record(plc, start_y, step_mm):
    pylot.move_y_axis(plc, start_y + step_mm)
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 4.0:
        set_y = plc.read_by_name("MAIN.axis_y.NcToPlc.SetPos", pyads.PLCTYPE_LREAL)
        actual_y = plc.read_by_name("MAIN.axis_y.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
        following_error = plc.read_by_name("MAIN.axis_y.NcToPlc.PosDiff", pyads.PLCTYPE_LREAL)
        f.write(f"{start_y},{time.perf_counter() - t0},{set_y},{actual_y},{following_error}\n")

try:
    with open(filename, "w") as f:
        f.write("start_y,time,set_y,actual_y,following_error\n")

        # setting velocity
        pylot.set_velocity(plc, 10.0)

        # setting x axis to mid-range position
        pylot.move_home_x_axis(plc)

        positions = [100.0, 150.0, 200.0]
        step_size = 10.0  # mm

        for pos in positions:
            pylot.move_wait_y_axis(plc, pos)
            time.sleep(5)
            step_and_record(plc, pos, step_size)
            pylot.wait_for_movement_done(plc)

        # moving back y axis to mid-range position
        pylot.move_home_y_axis(plc)

finally:
    plc.close()
