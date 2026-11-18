import time
import pyads
import pylot
from datetime import datetime

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

plc = pyads.Connection(plc_netid, plc_port, plc_ip)
plc.open()

filename = datetime.now().strftime("100_gradini_LS270_%Y-%m-%d_%H-%M.csv")

def acquire_data(plc, target_x):
    for i in range(30):
        actual_x = plc.read_by_name("MAIN.axis_x.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
        f.write(f"{target_x},{actual_x}\n")
        time.sleep(0.1)

def do_100_steps(plc, start_position, step_size_mm):
    pylot.wait_for_movement_done(plc)
    for i in range(1, 101):
        target_x = start_position + i * step_size_mm
        pylot.move_wait_x_axis(plc, target_x)
        time.sleep(5)
        acquire_data(plc, target_x)

try:
    with open(filename, "w") as f:
        f.write("target_x,actual_x\n")

        # setting y axis to mid-range position
        pylot.move_home_y_axis(plc)

        # positioning and measurements with x axis
        positions = [300.0]
        step_size = 0.0003  # 300 nanometers

        for pos in positions:
            pylot.move_wait_x_axis(plc, pos)
            do_100_steps(plc, pos, step_size)

        # moving back x axis to mid-range position
        pylot.move_home_x_axis(plc)

finally:
    plc.close()
