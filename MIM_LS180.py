import time
import pyads
import pylot
from datetime import datetime

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

plc = pyads.Connection(plc_netid, plc_port, plc_ip)
plc.open()

filename = datetime.now().strftime("misure_LS180_%Y-%m-%d_%H-%M.csv")

def acquire_data(plc, target_y, direction):
    for i in range(30):
        actual_y = plc.read_by_name("MAIN.axis_y.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
        f.write(f"{target_y},{direction},{actual_y}\n")
        time.sleep(0.1)

def take_the_stairs(plc, start_position, step_size_mm):
    pylot.wait_for_movement_done(plc)
    for i in range(1, 11):
        target_y = start_position + i * step_size_mm
        pylot.move_wait_y_axis(plc, target_y)
        time.sleep(5)
        acquire_data(plc, target_y, "up")
    for i in range(9, 0, -1):
        target_y = start_position + i * step_size_mm
        pylot.move_wait_y_axis(plc, target_y)
        time.sleep(5)
        acquire_data(plc, target_y, "down")

try:
    with open(filename, "w") as f:
        f.write("target_y,direction,actual_y\n")

        # setting x axis to mid-range position
        pylot.move_home_x_axis(plc)

        # positioning and measurements with y axis
        positions = [100.0, 150.0, 200.0]
        step_size = 0.0003  # 300 nanometers

        for pos in positions:
            pylot.move_wait_y_axis(plc, pos)
            take_the_stairs(plc, pos, step_size)

        # moving back y axis to mid-range position
        pylot.move_home_y_axis(plc)

finally:
    plc.close()
